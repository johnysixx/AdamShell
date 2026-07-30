class UniverseLogger:
    enabled_levels = {
        "BOOT",
        "DEBUG",
        "INFO",
        "EVENT",
        "WARNING",
        "ERROR",
    }

    @classmethod
    def log(cls, level, message):
        level = level.upper()

        if level in cls.enabled_levels:
            print(f"{level}: {message}")

    @classmethod
    def boot(cls, message):
        cls.log("BOOT", message)

    @classmethod
    def debug(cls, message):
        cls.log("DEBUG", message)

    @classmethod
    def info(cls, message):
        cls.log("INFO", message)

    @classmethod
    def event(cls, message):
        cls.log("EVENT", message)

    @classmethod
    def warning(cls, message):
        cls.log("WARNING", message)

    @classmethod
    def error(cls, message):
        cls.log("ERROR", message)
