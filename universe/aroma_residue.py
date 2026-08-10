from copy import deepcopy

from universe.aroma_profile import AromaProfile


class AromaResidue:

    @staticmethod
    def ensure(target):
        if isinstance(target, dict):
            aroma = target.get("aroma")

            if not isinstance(aroma, dict):
                target["aroma"] = (
                    AromaProfile.create(
                        identity=(
                            f"object:"
                            f"{target.get('name', 'unknown')}"
                        ),
                        components={},
                        intensity=0.0
                    )
                )

            return target["aroma"]

        aroma = getattr(
            target,
            "aroma",
            None
        )

        if not isinstance(aroma, dict):
            identity = (
                getattr(target, "id", None)
                or getattr(target, "name", None)
                or target.__class__.__name__
            )

            target.aroma = (
                AromaProfile.create(
                    identity=(
                        f"object:{identity}"
                    ),
                    components={},
                    intensity=0.0
                )
            )

        return target.aroma

    @classmethod
    def transfer(
        cls,
        source_profile,
        target,
        source_identity,
        fraction=0.15,
        decay_rate=0.04
    ):
        target_profile = cls.ensure(
            target
        )

        current = AromaProfile.current(
            source_profile
        )

        fraction = max(
            0.0,
            min(
                1.0,
                float(fraction)
            )
        )

        transferred = {
            component: (
                float(amount)
                * fraction
            )
            for component, amount
            in current.items()
            if float(amount) > 0.0
        }

        residue = AromaProfile.add_surface(
            profile=target_profile,
            source=source_identity,
            components=transferred,
            intensity=1.0,
            decay_rate=decay_rate
        )

        return {
            "transferred": True,
            "source": source_identity,
            "components": deepcopy(
                transferred
            ),
            "residue": residue
        }

    @classmethod
    def transfer_existing(
        cls,
        source,
        target,
        source_identity,
        fraction=0.08,
        decay_rate=0.03
    ):
        if isinstance(source, dict):
            source_profile = source.get(
                "aroma"
            )
        else:
            source_profile = getattr(
                source,
                "aroma",
                None
            )

        if not isinstance(
            source_profile,
            dict
        ):
            return {
                "transferred": False,
                "source": source_identity,
                "components": {},
                "reason": "source_has_no_aroma"
            }

        current = AromaProfile.current(
            source_profile
        )

        if not current:
            return {
                "transferred": False,
                "source": source_identity,
                "components": {},
                "reason": "source_aroma_is_empty"
            }

        return cls.transfer(
            source_profile=source_profile,
            target=target,
            source_identity=source_identity,
            fraction=fraction,
            decay_rate=decay_rate
        )

    @classmethod
    def decay(
        cls,
        target,
        ticks=1
    ):
        if isinstance(target, dict):
            profile = target.get(
                "aroma"
            )
        else:
            profile = getattr(
                target,
                "aroma",
                None
            )

        # Objekt bez pachu z?st?v? bez pachu.
        if not isinstance(
            profile,
            dict
        ):
            return {}

        return AromaProfile.decay(
            profile,
            ticks=ticks
        )
