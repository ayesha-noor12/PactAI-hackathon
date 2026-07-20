from copy import deepcopy


class ScopeOptimizer:

    FEATURE_KEYWORDS = {
        "authentication": "Authentication",
        "login": "Authentication",
        "signup": "Authentication",

        "dashboard": "Admin Dashboard",
        "admin": "Admin Dashboard",

        "payment": "Payment Gateway",
        "billing": "Payment Gateway",

        "cart": "Shopping Cart",
        "shopping cart": "Shopping Cart",
    }

    REMOVE_WORDS = [
        "remove",
        "without",
        "exclude",
        "delete",
        "drop"
    ]

    ADD_WORDS = [
        "add",
        "include",
        "also",
        "need"
    ]

    def optimize(self, requirements, message):

        updated = deepcopy(requirements)

        text = message.lower()

        removed = []
        added = []

        remove_mode = any(word in text for word in self.REMOVE_WORDS)
        add_mode = any(word in text for word in self.ADD_WORDS)

        for keyword, feature in self.FEATURE_KEYWORDS.items():

            if keyword not in text:
                continue

            if remove_mode:

                if feature in updated.features:

                    updated.features.remove(feature)
                    removed.append(feature)

            elif add_mode:

                if feature not in updated.features:

                    updated.features.append(feature)
                    added.append(feature)

        return updated, added, removed