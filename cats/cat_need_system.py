class CatNeedSystem:
    RATES = {'hunger': 0.025, 'thirst': 0.035, 'fatigue': 0.02, 'safety': 0.0, 'social': 0.018, 'curiosity': 0.015}

    @classmethod
    def advance(cls, cat):
        needs = cat.needs
        setattr(needs, 'tick', int(getattr(needs, 'tick', 0)) + 1)
        for key, rate in cls.RATES.items():
            setattr(needs, key, cls._clamp(float(getattr(needs, key, 0.0)) + rate))
        dominant = max(cls.RATES, key=lambda key: getattr(needs, key))
        setattr(needs, 'dominant', dominant)
        return {'name': 'cat_needs_advanced', 'cat': cat.name, 'dominant': dominant, 'needs': dict(vars(needs))}

    @classmethod
    def apply_action(cls, cat, intention_type):
        needs = cat.needs
        if intention_type == 'rest':
            setattr(needs, 'fatigue', cls._clamp(getattr(needs, 'fatigue', 0.0) - 0.35))
        elif intention_type in ('approach_cat', 'share_legend'):
            setattr(needs, 'social', cls._clamp(getattr(needs, 'social', 0.0) - 0.3))
        elif intention_type in ('wander', 'observe', 'explore_box'):
            setattr(needs, 'curiosity', cls._clamp(getattr(needs, 'curiosity', 0.0) - 0.22))
        return dict(vars(needs))

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))
