from universe.logger import UniverseLogger


class BarBlacklist:

    def __init__(self):
        self.name = "bar_blacklist"
        self.denied_identities = []

        UniverseLogger.boot(
            "BAR BLACKLIST CREATED"
        )

    def ban(
        self,
        identity
    ):
        if identity is None:
            return False

        identity = str(identity)

        if identity not in self.denied_identities:
            self.denied_identities.append(
                identity
            )

            UniverseLogger.event(
                f"BAR BLACKLIST ADDED: {identity}"
            )

        return True

    def is_banned(
        self,
        identity
    ):
        if identity is None:
            return False

        return (
            str(identity)
            in self.denied_identities
        )
