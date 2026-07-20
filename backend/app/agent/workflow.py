from copy import deepcopy

from app.agent.discovery_agent import DiscoveryAgent
from app.agent.negotiation_agent import NegotiationAgent

from app.agent.intent_analyzer import IntentAnalyzer
from app.agent.offer_analyzer import OfferAnalyzer
from app.agent.counter_offer import CounterOfferGenerator
from app.agent.scope_optimizer import ScopeOptimizer
from app.agent.intent_gate import IntentGate
from app.agent.negotiation_nlu import NegotiationNLU

from app.engines.project_estimator import ProjectEstimator
from app.engines.timeline_engine import TimelineEngine
from app.engines.pricing_engine import PricingEngine
from app.engines.decision_engine import DecisionEngine

from app.agent.workflow_state import WorkflowState
from app.agent.agreement_detector import AgreementDetector
from app.agent.proposal_generator import ProposalGenerator
from app.agent.proposal_store import proposal_store
from app.agent.reply_guard import reply_is_grounded, reply_matches_current_offer, safe_fallback_reply


class NegotiationWorkflow:

    def __init__(self, llm):

        self.llm = llm

        self.discovery = DiscoveryAgent(llm)

        self.estimator = ProjectEstimator()

        self.timeline = TimelineEngine()

        self.pricing = PricingEngine()

        self.decision = DecisionEngine()

        self.negotiator = NegotiationAgent(llm)

        self.intent = IntentAnalyzer()

        self.offer_analyzer = OfferAnalyzer()

        self.counter_generator = CounterOfferGenerator()

        self.scope = ScopeOptimizer()
        self.agreement = AgreementDetector()
        self.proposal = ProposalGenerator()
        self.intent_gate = IntentGate()
        self.nlu = NegotiationNLU(llm)

    def _recompute_with_carry_forward(self, memory):
        """
        Re-runs estimation/timeline/pricing after a genuine requirements change
        (timeline or platform), carrying the same CONCESSION DEPTH forward onto the new
        price basis instead of resetting negotiation progress to zero. Used by both the
        timeline-change and platform-change handling below — they need identical
        behavior, just triggered by different things changing.
        """

        old_recommended = memory.pricing.recommended_price if memory.pricing else None
        old_minimum = memory.pricing.minimum_price if memory.pricing else None
        old_counter = memory.counter_offers[-1] if memory.counter_offers else None

        memory.estimation = self.estimator.estimate(memory.requirements)
        memory.timeline = self.timeline.calculate(
            memory.estimation, memory.requirements, memory.owner_email
        )
        memory.pricing = self.pricing.calculate(
            memory.estimation, memory.requirements, memory.timeline, memory.owner_email
        )

        if (
            old_counter is not None
            and old_recommended is not None
            and old_minimum is not None
            and old_recommended != old_minimum
        ):
            concession_depth = (old_recommended - old_counter) / (old_recommended - old_minimum)
            concession_depth = max(0.0, min(1.0, concession_depth))

            new_span = memory.pricing.recommended_price - memory.pricing.minimum_price
            carried_counter = round(
                memory.pricing.recommended_price - (new_span * concession_depth), 2
            )
            memory.counter_offers[-1] = carried_counter

    def _polish_description(self, requirements) -> str:
        """
        Rewrites the client's raw, pasted-together discovery messages into a coherent
        2-3 sentence project brief for the proposal, grounded in the FINAL negotiated
        scope (platform/features may have changed since the client first described the
        idea) rather than what they originally said before any negotiation happened.
        Falls back to the raw text if the LLM call fails, rather than losing it.
        """

        raw_description = requirements.description or ""

        prompt = (
            "Rewrite this into a polished 2-3 sentence project description for a "
            "freelance proposal. Base it on the FINAL scope listed below — if the raw "
            "notes mention something not in the final feature/platform list, leave it "
            "out, since it may have been cut during negotiation. Plain prose, no "
            "bullet points, no markdown.\n\n"
            f"Raw client notes: {raw_description}\n\n"
            f"Final project type: {requirements.project_type}\n"
            f"Final platform: {', '.join(requirements.platform)}\n"
            f"Final features: {', '.join(requirements.features)}"
        )

        try:
            polished = self.llm.chat(
                system_prompt="You write concise, professional project descriptions for freelance proposals.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return polished.strip() or raw_description
        except Exception:
            return raw_description

    def process(self, message, memory):

        # ==========================================================
        # INTENT GATE
        # ==========================================================

        if memory.stage == WorkflowState.DISCOVERY and not memory.messages:

            # Only runs on the true first message of the whole session. This is the
            # actual fix for "I was thinking about an ecommerce website" getting
            # wrongly deflected as off-topic — that regex-based project-intent check
            # only recognizes certain verbs ("want", "build", "need"), and kept needing
            # individual patches for every new phrasing. Once we've already asked a
            # follow-up question, any reply is by definition part of the project
            # conversation — there's no reason to keep re-screening it.
            gated_reply = self.intent_gate.check(message, memory)

            if gated_reply is not None:
                memory.add_client_message(message)
                memory.add_agent_message(gated_reply)
                return {
                    "stage": WorkflowState.DISCOVERY,
                    "reply": gated_reply,
                    "requirements": memory.requirements,
                }

        # ==========================================================
        # DISCOVERY
        # ==========================================================

        if memory.stage == WorkflowState.DISCOVERY:

            discovery = self.discovery.process(
                message,
                memory
            )

            if discovery["status"] != "READY_FOR_ESTIMATION":

                # This was the bug: the AI's clarifying question was returned to the
                # client but never saved to memory.messages, so every early discovery
                # Q&A silently vanished from history on reload/re-login.
                memory.add_agent_message(discovery["question"])

                return {
                    "stage": WorkflowState.DISCOVERY,
                    "reply": discovery["question"],
                    "requirements": memory.requirements
                }

            requirements = memory.requirements

            estimation = self.estimator.estimate(
                requirements
            )

            timeline = self.timeline.calculate(
                estimation,
                requirements,
                memory.owner_email
            )

            pricing = self.pricing.calculate(
                estimation,
                requirements,
                timeline,
                memory.owner_email
            )

            decision = self.decision.decide(
                requirements,
                estimation,
                pricing,
                timeline
            )

            memory.estimation = estimation
            memory.timeline = timeline
            memory.pricing = pricing
            memory.decision = decision

            memory.stage = WorkflowState.WAITING_FOR_CLIENT

            # No longer shown to the client: "Estimated Hours" and "Our Estimated
            # Timeline" — those are internal numbers used to calculate price, not
            # something the client needs to see or negotiate against. The timeline
            # shown back to them is THEIRS — what they actually told us — not our own
            # recalculated figure.
            timeline_line = (
                f"Timeline: {requirements.deadline_days} days"
                if requirements.deadline_days is not None
                else "Timeline: to be discussed"
            )

            if requirements.deadline_days is not None and not timeline.feasible:
                timeline_line += " — heads up, that's a tight turnaround for this scope."

            budget_note = ""
            if requirements.budget_min is not None:
                if requirements.budget_min == requirements.budget_max:
                    budget_note = f"\nYour budget: ${requirements.budget_min}"
                else:
                    budget_note = (
                        f"\nYour budget range: ${requirements.budget_min}–${requirements.budget_max}"
                    )

            # A polished restatement of what the client described, rather than just a
            # raw data dump — confirms we understood correctly, and reads like a real
            # proposal opener rather than a system printout.
            platform_str = "/".join(requirements.platform) if requirements.platform else "your platform"
            features_str = (
                ", ".join(requirements.features)
                if requirements.features
                else "the core functionality you described"
            )

            summary = f"""
Got it — a {requirements.project_type or 'project'} for {platform_str}, with {features_str}. Here's the initial scope and pricing:

{timeline_line}
{budget_note}

Price: ${pricing.recommended_price}

That covers the full build as described. Let me know if you'd like to negotiate on price, timeline, or scope — otherwise I'll note this down and get back to you as soon as it's confirmed.
"""

            memory.add_agent_message(summary)

            return {
                "stage": WorkflowState.WAITING_FOR_CLIENT,
                "reply": summary,
                "requirements": requirements
            }

        # ==========================================================
        # NEGOTIATION
        # ==========================================================

        if memory.stage in (
            WorkflowState.WAITING_FOR_CLIENT,
            WorkflowState.NEGOTIATION,
        ):

            memory.add_client_message(message)

            # Captured BEFORE anything this turn can change it — this is what the
            # regression guard further down needs to compare against. Using the
            # post-turn value there was the actual bug: when the ladder's raw math
            # wants to go lower than the client's own offer, a clamp forces our new
            # counter UP to match their number exactly, which made "the current
            # offer" and "what the client just said" the same value by coincidence —
            # so a reply that quoted the client's own rejected number back at them
            # (while actually demanding the original recommended price) slipped past
            # the guard, since that number was technically "mentioned."
            pre_turn_standing_offer = (
                memory.counter_offers[-1] if memory.counter_offers else None
            )

            # ---------------------------------------------
            # Scope Optimizer
            # ---------------------------------------------

            updated_requirements, added, removed = self.scope.optimize(
                memory.requirements,
                message
            )

            if added or removed:

                memory.requirements = updated_requirements

                estimation = self.estimator.estimate(
                    memory.requirements
                )

                timeline = self.timeline.calculate(
                    estimation,
                    memory.requirements,
                    memory.owner_email
                )

                pricing = self.pricing.calculate(
                    estimation,
                    memory.requirements,
                    timeline,
                    memory.owner_email
                )

                decision = self.decision.decide(
                    memory.requirements,
                    estimation,
                    pricing,
                    timeline
                )

                memory.estimation = estimation
                memory.timeline = timeline
                memory.pricing = pricing
                memory.decision = decision

            # ---------------------------------------------
            # Understand this message — LLM-based classification first (this is what
            # replaces the old keyword/regex approach, which kept needing individual
            # patches for typos like "okhay"/"extent" and phrasing like "we can extend
            # the timeline" being misread as agreement). Falls back to the regex-based
            # detectors only if the LLM call itself fails.
            # ---------------------------------------------
            nlu_result = self.nlu.analyze(message, memory)

            if nlu_result is not None:
                is_agreement_signal = nlu_result.is_final_agreement
                intent_label = nlu_result.intent
                price_offer = nlu_result.price_offer
            else:
                is_agreement_signal = self.agreement.is_agreement(message, memory)
                fallback_intent = self.intent.analyze(message)
                intent_label = fallback_intent.intent
                price_offer = fallback_intent.offer

            # ---------------------------------------------
            # Timeline changes actually get recalculated now, instead of the LLM
            # inventing a plausible-sounding "discount for the extended schedule" with
            # nothing real behind it (this is literally what happened: it accepted a
            # client's number while fabricating a timeline-discount justification we
            # never computed). If the client proposes a new deadline, we update
            # requirements.deadline_days, recompute timeline + pricing for real (the
            # rush multiplier genuinely drops if the new deadline is more comfortable),
            # and everything downstream — the facts sent to the LLM, the summary, the
            # counter-offer ladder — automatically reflects the real new numbers.
            # ---------------------------------------------
            timeline_changed = False
            old_recommended_price = None

            if (
                nlu_result is not None
                and nlu_result.timeline_days_offer is not None
                and nlu_result.timeline_days_offer != memory.requirements.deadline_days
            ):

                old_recommended_price = memory.pricing.recommended_price if memory.pricing else None
                memory.requirements.deadline_days = nlu_result.timeline_days_offer
                self._recompute_with_carry_forward(memory)
                timeline_changed = True

            # This is the real fix for "across Android, iOS, and Desktop" persisting
            # even after being corrected three times, and for the AI leaking the raw
            # floor price ($728) while improvising about dropping platforms — there was
            # no actual platform-change logic at all before this, so the LLM was just
            # free-associating a number instead of a real recalculation.
            platform_changed = False

            if (
                nlu_result is not None
                and nlu_result.platform_update
                and set(nlu_result.platform_update) != set(memory.requirements.platform)
            ):

                if old_recommended_price is None:
                    old_recommended_price = memory.pricing.recommended_price if memory.pricing else None

                memory.requirements.platform = nlu_result.platform_update
                self._recompute_with_carry_forward(memory)
                platform_changed = True

            if is_agreement_signal:

                memory.agreement_reached = True

                memory.agreed_price = (
                    memory.counter_offers[-1]
                    if memory.counter_offers
                    else memory.pricing.recommended_price
                )
                memory.agreed_timeline = (
                    memory.requirements.deadline_days
                    if memory.requirements.deadline_days is not None
                    else (memory.timeline.estimated_days if memory.timeline else None)
                )

                memory.stage = WorkflowState.COMPLETED

                # Polish the description now, using the FINAL negotiated scope — not
                # the raw pasted-together chat text. This is what fixes the proposal
                # reading like disconnected sentences instead of a coherent brief, and
                # makes sure it reflects what was actually agreed (e.g. Desktop only),
                # not whatever the client originally described before negotiation.
                memory.requirements.description = self._polish_description(memory.requirements)

                proposal_text = self.proposal.generate(
                    memory.requirements,
                    memory.estimation,
                    memory.pricing,
                    memory.timeline,
                    agreed_price=memory.agreed_price,
                    agreed_timeline=memory.agreed_timeline,
                )

                # Create the persisted proposal record right now, at the moment of
                # agreement — this is the fix for "the proposal isn't saved at all".
                # It's saved as pending_review: the client doesn't see it accepted yet,
                # the freelancer reviews it in Proposal History and hits Accept/Reject.
                record = proposal_store.create(
                    owner_email=memory.owner_email,
                    session_id=memory.session_id,
                    title=f"{memory.requirements.project_type or 'Untitled'} project",
                    project_type=memory.requirements.project_type,
                    platform=memory.requirements.platform,
                    features=memory.requirements.features,
                    estimated_hours=(
                        memory.estimation.estimated_hours if memory.estimation else None
                    ),
                    timeline_days=memory.agreed_timeline,
                    agreed_price=memory.agreed_price,
                    recommended_price=(
                        memory.pricing.recommended_price if memory.pricing else None
                    ),
                    minimum_price=(
                        memory.pricing.minimum_price if memory.pricing else None
                    ),
                    proposal_text=proposal_text,
                )
                memory.proposal_id = record["id"]

                reply = (
                    f"Great, let's lock that in at ${memory.agreed_price}. "
                    "I've drafted the proposal and sent it to the freelancer for review — "
                    "you'll hear back once it's confirmed on their end."
                )
                memory.add_agent_message(reply)

                return {
                    "stage": WorkflowState.COMPLETED,
                    "reply": reply,
                    "proposal_id": memory.proposal_id,
                }

            # A bare "no" carries no information about what would actually work —
            # asking a direct clarifying question is more useful (and guaranteed
            # non-repetitive) than letting the LLM re-pitch the same numbers.
            if intent_label == "DECLINE":

                # Uses its own counter, NOT negotiation_round — that one drives the
                # price concession ladder, and a plain decline with no actual counter-
                # offer exchanged was previously consuming a ladder round for free,
                # causing the price to drop faster than the real back-and-forth
                # warranted.
                memory.decline_count += 1
                clarifying_questions = [
                    "No worries — what would help: a lower price, more time, or trimming some features?",
                    "Got it. Is it the price, the timeline, or the scope that's the sticking point?",
                    "Understood — what number or timeline would actually work for you?",
                ]
                reply = clarifying_questions[
                    min(memory.decline_count - 1, len(clarifying_questions) - 1)
                ]

                memory.add_agent_message(reply)
                memory.stage = WorkflowState.NEGOTIATION

                return {
                    "stage": WorkflowState.NEGOTIATION,
                    "reply": reply,
                    "requirements": memory.requirements,
                }

            # The client asking "how can we adjust scope" deserves a real answer, not
            # the generic price-fallback that was firing here before (twice, verbatim
            # identical, in the actual test that surfaced this). Simulate removing each
            # current feature to find the REAL price impact — since pricing is now
            # complexity-tier based rather than per-feature hours, this is computed by
            # actually re-running the estimator/pricing engine without each feature,
            # not guessed.
            if intent_label == "SCOPE" and memory.requirements.features and memory.pricing:

                options = []

                for feature in memory.requirements.features:

                    trial_requirements = deepcopy(memory.requirements)
                    trial_requirements.features = [
                        f for f in trial_requirements.features if f != feature
                    ]

                    trial_estimation = self.estimator.estimate(trial_requirements)
                    trial_timeline = self.timeline.calculate(
                        trial_estimation, trial_requirements, memory.owner_email
                    )
                    trial_pricing = self.pricing.calculate(
                        trial_estimation, trial_requirements, trial_timeline, memory.owner_email
                    )

                    savings = round(
                        memory.pricing.recommended_price - trial_pricing.recommended_price, 2
                    )

                    if savings > 0:
                        options.append((feature, savings, trial_pricing.recommended_price))

                options.sort(key=lambda o: -o[1])

                if options:
                    top_feature, top_savings, top_price = options[0]

                    current_full_price = (
                        memory.counter_offers[-1]
                        if memory.counter_offers
                        else memory.pricing.recommended_price
                    )

                    # This is what makes "okay let's do it" answerable later instead of
                    # ambiguous — we now know exactly what the two options ON THE TABLE
                    # are, and can check which one a vague confirmation actually means.
                    memory.pending_scope_offer = {
                        "feature": top_feature,
                        "reduced_price": top_price,
                        "full_price": current_full_price,
                    }

                    lines = [
                        f"dropping {f} brings it to ${p} (saves ${s})"
                        for f, s, p in options[:2]
                    ]
                    reply = "Here's what actually moves the price: " + "; ".join(lines) + ". Want to cut one?"
                else:
                    reply = (
                        "Honestly, none of the current features would meaningfully lower the "
                        "price on their own — want to look at the timeline or budget instead?"
                    )

                memory.add_agent_message(reply)
                memory.stage = WorkflowState.NEGOTIATION

                return {
                    "stage": WorkflowState.NEGOTIATION,
                    "reply": reply,
                    "requirements": memory.requirements,
                }

            analysis = None

            counter_offer = None

            if (
                intent_label == "PRICE"
                and price_offer is not None
            ):

                memory.offers.append(
                    price_offer
                )

                last_counter = (
                    memory.counter_offers[-1] if memory.counter_offers else None
                )

                analysis = self.offer_analyzer.analyze(
                    price_offer,
                    memory.pricing,
                    last_counter=last_counter,
                )

                memory.negotiation_round += 1

                counter_offer = self.counter_generator.generate(
                    analysis,
                    round_number=memory.negotiation_round,
                )

                # This is the actual fix for "$1300 is a bit low... I need to be at
                # $1510": our own ladder was willing to go to ~$542 by this round, so
                # the clamp in counter_offer.py (never counter below what the client
                # already offered) forced this turn's counter UP to exactly $1300 —
                # meaning we were genuinely fine with their number. The decision label
                # still said "COUNTER" because analyze() only compares against the
                # PREVIOUS round's counter, not what we'd actually settle for this
                # round. Reconciling it here means the LLM gets told to accept warmly
                # instead of holding out for a number we'd already have conceded past.
                if counter_offer <= price_offer:
                    analysis.decision = "ACCEPT"

                memory.counter_offers.append(
                    counter_offer
                )

            # If we're at the last round of the ladder and still not agreeing, this is
            # genuinely a final offer — say so plainly instead of sounding like there's
            # more room to move, which is what you asked for ("sorry, it's not gonna
            # work, the last I can offer is $X, let me know").
            is_final_round = (
                memory.negotiation_round >= self.counter_generator.MAX_ROUNDS
                and analysis is not None
                and analysis.decision != "ACCEPT"
            )

            # ---------------------------------------------
            # Generate LLM response
            # ---------------------------------------------

            reply = self.negotiator.negotiate(

                requirements=memory.requirements,

                estimation=memory.estimation,

                timeline=memory.timeline,

                pricing=memory.pricing,

                decision=memory.decision,

                client_message=message,

                intent=intent_label,

                analysis=analysis,

                counter_offer=counter_offer,

                added_features=added,

                removed_features=removed,

                current_standing_offer=(
                    memory.counter_offers[-1] if memory.counter_offers else None
                ),

                timeline_changed=timeline_changed,

                platform_changed=platform_changed,

                old_recommended_price=old_recommended_price,

                is_final_round=is_final_round,
            )

            # Hard guardrail: reject any reply that mentions a dollar figure not actually
            # grounded in our own pricing numbers. This is what catches things like the
            # invented "$1,200" — prompt instructions alone weren't reliable enough.
            current_standing_offer = (
                memory.counter_offers[-1] if memory.counter_offers else None
            )

            allowed_values = [
                memory.pricing.recommended_price if memory.pricing else None,
                counter_offer,
                analysis.client_offer if analysis else None,
                current_standing_offer,
                old_recommended_price,
            ]

            needs_fallback = not reply_is_grounded(reply, allowed_values)

            # Second check: catches reverting to the price that was on the table BEFORE
            # this turn — using pre_turn_standing_offer specifically here (not the
            # post-append current_standing_offer above) is the actual fix: the clamp in
            # counter_offer.py can force this turn's new counter to equal the client's
            # own number, which made the post-turn value coincidentally match whatever
            # the client just said, letting a reply that misused it slip through.
            if not needs_fallback and memory.pricing:
                needs_fallback = not reply_matches_current_offer(
                    reply, pre_turn_standing_offer, memory.pricing.recommended_price
                )

            if needs_fallback:
                reply = safe_fallback_reply(
                    memory.pricing,
                    counter_offer=counter_offer if counter_offer is not None else current_standing_offer,
                    client_offer=analysis.client_offer if analysis else None,
                )

            memory.add_agent_message(reply)

            memory.stage = WorkflowState.NEGOTIATION

            return {
                "stage": WorkflowState.NEGOTIATION,
                "reply": reply,
                "requirements": memory.requirements
            }

        # ==========================================================
        # COMPLETED — negotiation is over, proposal already created above.
        # ==========================================================

        if memory.proposal_id:
            return {
                "stage": WorkflowState.COMPLETED,
                "reply": (
                    "This negotiation is closed — the proposal is with the freelancer "
                    "for review. You'll be notified once it's confirmed."
                ),
                "proposal_id": memory.proposal_id,
            }

        # Safety net: shouldn't normally be reached since the proposal is created at the
        # moment agreement is detected above, but covers any stale session that reached
        # COMPLETED before this fix.
        proposal_text = self.proposal.generate(
            memory.requirements,
            memory.estimation,
            memory.pricing,
            memory.timeline,
            agreed_price=memory.agreed_price,
            agreed_timeline=memory.agreed_timeline,
        )

        return {
            "stage": WorkflowState.COMPLETED,
            "reply": proposal_text,
        }