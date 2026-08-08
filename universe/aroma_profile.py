from copy import deepcopy


class AromaProfile:

    @staticmethod
    def create(
        identity,
        components=None,
        intensity=1.0
    ):
        return {
            "identity": identity,
            "base_components": dict(
                components or {}
            ),
            "base_intensity": float(
                intensity
            ),
            "surface_residues": [],
            "type": "chemical_aroma_profile"
        }

    @staticmethod
    def add_surface(
        profile,
        source,
        components,
        intensity=1.0,
        decay_rate=0.03
    ):
        residue = {
            "source": source,
            "components": dict(
                components
            ),
            "intensity": max(
                0.0,
                float(intensity)
            ),
            "decay_rate": max(
                0.0,
                min(
                    1.0,
                    float(decay_rate)
                )
            ),
            "age_ticks": 0
        }

        profile.setdefault(
            "surface_residues",
            []
        ).append(
            residue
        )

        return deepcopy(
            residue
        )

    @staticmethod
    def current(profile):
        result = {}

        base_intensity = float(
            profile.get(
                "base_intensity",
                1.0
            )
        )

        for component, amount in (
            profile.get(
                "base_components",
                {}
            ).items()
        ):
            result[component] = (
                result.get(
                    component,
                    0.0
                )
                + float(amount)
                * base_intensity
            )

        for residue in profile.get(
            "surface_residues",
            []
        ):
            intensity = float(
                residue.get(
                    "intensity",
                    0.0
                )
            )

            for component, amount in (
                residue.get(
                    "components",
                    {}
                ).items()
            ):
                result[component] = (
                    result.get(
                        component,
                        0.0
                    )
                    + float(amount)
                    * intensity
                )

        return result

    @staticmethod
    def decay(
        profile,
        ticks=1
    ):
        ticks = max(
            0,
            int(ticks)
        )

        survivors = []

        for residue in profile.get(
            "surface_residues",
            []
        ):
            residue[
                "age_ticks"
            ] += ticks

            decay_rate = float(
                residue.get(
                    "decay_rate",
                    0.03
                )
            )

            residue[
                "intensity"
            ] *= (
                (1.0 - decay_rate)
                ** ticks
            )

            if residue[
                "intensity"
            ] > 0.001:
                survivors.append(
                    residue
                )

        profile[
            "surface_residues"
        ] = survivors

        return AromaProfile.current(
            profile
        )