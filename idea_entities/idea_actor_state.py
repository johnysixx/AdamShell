from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdeaPrePhysicalAttributes:
    can_exist_before_form: bool = True
    can_influence: bool = True
    can_become_process: bool = True
    can_hold_symbolic_energy: bool = True
    can_hold_will: bool = True

    def to_dict(self):
        return {
            "can_exist_before_form": self.can_exist_before_form,
            "can_influence": self.can_influence,
            "can_become_process": self.can_become_process,
            "can_hold_symbolic_energy": self.can_hold_symbolic_energy,
            "can_hold_will": self.can_hold_will,
        }
