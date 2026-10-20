PactAI

An AI that negotiates freelance projects on your behalf. A client describes what they need in plain language .PactAI scopes it, prices it, negotiates the terms, and hands the freelancer a finished proposal to accept or reject.

Built for the Global AI Hackathon Series.


What it does


Discovery — the client describes their project conversationally; PactAI extracts project type, platform, features, timeline, and budget.
Pricing priced either hourly (hours × rate) or as a fixed range per platform, positioned by project complexity.
Negotiation. PactAI holds the actual back-and-forth: countering offers with a gradual concession ladder, recalculating honestly if scope or timeline changes mid-conversation, and never revealing the freelancer's floor price.
Proposal once a deal is reached, PactAI drafts a full proposal and queues it for the freelancer to Accept or Reject the AI negotiates, the human decides.


Tech stack

LayerTechBackendFastAPI, Pydantic, UvicornLLMQwen (qwen3.7-max) via Alibaba Cloud DashScope, OpenAI-compatible APIFrontendReact, Vite, Tailwind CSS v4, React RouterStorageJSON files + pickled sessions (no database currently in use)

Project structure

backend/
  app/
    agent/          # Discovery, negotiation, NLU, scope/timeline logic, session + proposal storage
    engines/         # Project estimation, pricing, timeline, decision logic
    llm/             # Qwen / Groq LLM clients behind a shared interface
    prompts/         # System prompts for extraction, negotiation, and NLU classification
    schemas/         # Pydantic models (profile, project requirements, chat)
    api/routes/      # auth, profile, chat, proposals, sessions
    storage/         # users.json, proposals.json, per-user profiles, sessions (gitignored)
    config.py
    main.py
  requirements.txt

pactai-frontend/
  src/
    pages/           # Landing, auth, dashboard, negotiation, proposals, settings
    components/      # Layout, forms, shared UI
    context/         # Auth state
    lib/api.js        # Backend API client
  package.json

Setup

Backend

bashcd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your real values
uvicorn app.main:app --reload --port 8000

Frontend

bashcd pactai-frontend
npm install
npm run dev

Runs at http://localhost:5173, proxying /api/* to the backend at http://localhost:8000.

Environment variables

Create backend/.env (never committed — see .env.example for the template):

VariableDescriptionQWEN_API_KEYYour DashScope API keyQWEN_BASE_URLhttps://dashscope-intl.aliyuncs.com/compatible-mode/v1QWEN_MODELDefault Qwen model, e.g. qwen-plusQWEN_THINKING_MODELReasoning model, e.g. qwen3.7-maxGROQ_API_KEYOptional — only needed if using the Groq LLM client insteadGROQ_MODELe.g. llama-3.3-70b-versatile

Known limitations


Auth is identity, not security. Login/signup don't issue a real session token — the frontend sends the logged-in user's email with each request, and the backend trusts it. Enough to keep accounts from crossing over in a demo; not real authentication. Replace with JWT before this handles real users.
No real database. All data is flat JSON/pickle files on disk — fine for a single-instance hackathon demo, not for concurrent production use.


License

MIT (or update to whatever you'd prefer).
