class RedButton:

    def __init__(self):
        self.name = "red_button"
        self.type = "bar_control"

        self.alarm_active = False
        self.red_light_on = False
        self.horn_active = False
        print("RED BUTTON INSTALLED ON BAR COUNTER")

    def activate_alarm(self):
        self.alarm_active = True
        self.red_light_on = True
        self.horn_active = True

        print("RED BUTTON ALARM ACTIVATED")

    def press(self):
        if not self.alarm_active:
            print("RED BUTTON PRESS IGNORED: NO ACTIVE ALARM")
            return False

        print("RED BUTTON PRESSED")
        self.clear_alarm()
        return True

    def clear_alarm(self):
        self.alarm_active = False
        self.red_light_on = False
        self.horn_active = False

        print("RED BUTTON ALARM CLEARED")

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "alarm_active": self.alarm_active,
            "red_light_on": self.red_light_on,
            "horn_active": self.horn_active
        }
