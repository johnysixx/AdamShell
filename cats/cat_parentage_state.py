from dataclasses import dataclass


@dataclass(slots=True)
class CatParentageState:
    mother: str | None = None
    father: str | None = None

    @classmethod
    def require_from_cat(
        cls,
        cat,
    ):
        family = getattr(
            cat,
            'family',
            None,
        )

        state = getattr(
            family,
            'parents',
            None,
        )

        if not isinstance(
            state,
            cls,
        ):
            raise TypeError(
                'Cat family parentage must be '
                'CatParentageState.'
            )

        return state

    def name_for_role(
        self,
        role,
    ):
        if role == 'mother':
            return self.mother

        if role == 'father':
            return self.father

        raise ValueError(
            f'Unsupported cat parent role: '
            f'{role}'
        )
