class ComponentObject:

    def __init__(self, **values):
        for key, value in values.items():
            setattr(self, key, value)

    def to_dict(self):
        return dict(vars(self))

    def __eq__(self, other):
        if isinstance(other, ComponentObject):
            return vars(self) == vars(other)
        if isinstance(other, dict):
            return vars(self) == other
        return NotImplemented

    def __repr__(self):
        fields = ', '.join((f'{key}={value!r}' for key, value in vars(self).items()))
        return f'<{self.__class__.__name__} {fields}>'
