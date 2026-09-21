from copy import deepcopy

from universe.aroma_profile import AromaProfile


class AromaResidue:

    @staticmethod
    def ensure(target):
        if isinstance(target, dict):
            raise TypeError(
                "Aroma residue targets must be object entities."
            )

        aroma = getattr(target, "aroma", None)

        if aroma is None:
            identity = (
                getattr(target, "id", None)
                or getattr(target, "name", None)
                or target.__class__.__name__
            )

            target.aroma = AromaProfile(
                identity=f"object:{identity}",
                base_components={},
                base_intensity=0.0,
            )
            return target.aroma

        if not isinstance(aroma, AromaProfile):
            raise TypeError(
                "Entity aroma must be an AromaProfile object."
            )

        return aroma

    @classmethod
    def transfer(
        cls,
        source_profile,
        target,
        source_identity,
        fraction=0.15,
        decay_rate=0.04,
    ):
        if not isinstance(source_profile, AromaProfile):
            raise TypeError(
                "source_profile must be an AromaProfile object."
            )

        target_profile = cls.ensure(target)
        current = source_profile.current()

        fraction = max(0.0, min(1.0, float(fraction)))

        transferred = {
            component: float(amount) * fraction
            for component, amount in current.items()
            if float(amount) > 0.0
        }

        residue = target_profile.add_surface(
            source=source_identity,
            components=transferred,
            intensity=1.0,
            decay_rate=decay_rate,
        )

        return {
            "transferred": True,
            "source": source_identity,
            "components": deepcopy(transferred),
            "residue": residue.to_dict(),
        }

    @classmethod
    def transfer_existing(
        cls,
        source,
        target,
        source_identity,
        fraction=0.08,
        decay_rate=0.03,
    ):
        if isinstance(source, dict):
            raise TypeError(
                "Aroma residue sources must be object entities."
            )

        source_profile = getattr(source, "aroma", None)

        if source_profile is None:
            return {
                "transferred": False,
                "source": source_identity,
                "components": {},
                "reason": "source_has_no_aroma",
            }

        if not isinstance(source_profile, AromaProfile):
            raise TypeError(
                "Source aroma must be an AromaProfile object."
            )

        current = source_profile.current()

        if not current:
            return {
                "transferred": False,
                "source": source_identity,
                "components": {},
                "reason": "source_aroma_is_empty",
            }

        return cls.transfer(
            source_profile=source_profile,
            target=target,
            source_identity=source_identity,
            fraction=fraction,
            decay_rate=decay_rate,
        )

    @classmethod
    def decay(cls, target, ticks=1):
        if isinstance(target, dict):
            raise TypeError(
                "Aroma residue targets must be object entities."
            )

        profile = getattr(target, "aroma", None)

        if profile is None:
            return {}

        if not isinstance(profile, AromaProfile):
            raise TypeError(
                "Entity aroma must be an AromaProfile object."
            )

        return profile.decay(ticks=ticks)
