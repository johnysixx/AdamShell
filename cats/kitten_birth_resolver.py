from cats.development_resolver import (
    CatDevelopmentResolver
)


class KittenBirthResolver:

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

        self.development_resolver = (
            CatDevelopmentResolver(
                universe
            )
        )

    def give_birth(
        self,
        mother,
        current_day=None
    ):
        reproduction = mother.get(
            "reproduction",
            {}
        )

        if mother.get("sex") != "female":
            raise ValueError(
                "Only a female cat can give birth."
            )

        if not reproduction.get(
            "pregnant",
            False
        ):
            raise ValueError(
                "Cat is not pregnant."
            )

        pregnancy_day = int(
            reproduction.get(
                "pregnancy_day",
                0
            )
        )

        gestation_days = int(
            reproduction.get(
                "gestation_days",
                0
            )
        )

        if pregnancy_day < gestation_days:
            return {
                "name": "kitten_birth_denied",
                "reason": "gestation_not_complete",
                "mother": mother["name"],
                "pregnancy_day": pregnancy_day,
                "gestation_days": gestation_days,
                "born": False
            }

        embryos = list(
            reproduction.get(
                "embryos",
                []
            )
        )

        litter_number = (
            int(
                reproduction.get(
                    "litters_born",
                    0
                )
            )
            + 1
        )

        kittens = []
        birth_results = []

        for embryo in embryos:
            kitten_name = (
                self._next_kitten_name()
            )

            profile = dict(
                embryo["profile"]
            )

            manifestation = (
                self.universe.manifest_cat(
                    name=kitten_name,
                    source=(
                        "kitten_birth_resolver"
                    ),
                    color=profile["color"],
                    fur_length=profile[
                        "fur_length"
                    ],
                    pattern=profile["pattern"],
                    eye_color=profile[
                        "eye_color"
                    ],
                    sex=profile["sex"]
                )
            )

            if manifestation is None:
                birth_results.append({
                    "embryo_id": embryo["id"],
                    "kitten": None,
                    "born": False,
                    "reason": (
                        "manifest_cat_failed"
                    )
                })
                continue

            kitten = manifestation["cat"]

            kitten["state"] = "newborn"

            self.development_resolver.initialize_newborn(
                kitten,
                birth_day=current_day
            )

            kitten["genotype"] = embryo[
                "genotype"
            ]
            kitten["phenotype"] = embryo[
                "phenotype"
            ]
            kitten["mother_name"] = mother[
                "name"
            ]
            kitten["father_name"] = embryo[
                "father_name"
            ]
            kitten["parents"] = {
                "mother": mother["name"],
                "father": embryo[
                    "father_name"
                ]
            }
            kitten["embryo_id"] = embryo[
                "id"
            ]
            kitten["genetic_status"] = (
                embryo[
                    "genetic_status"
                ]
            )
            kitten["rare"] = embryo["rare"]

            for trait in embryo.get(
                "special_traits",
                []
            ):
                if trait not in kitten[
                    "special_traits"
                ]:
                    kitten[
                        "special_traits"
                    ].append(
                        trait
                    )

            kittens.append(
                kitten
            )

            birth_results.append({
                "embryo_id": embryo["id"],
                "kitten": kitten_name,
                "father": embryo[
                    "father_name"
                ],
                "genetic_status": embryo[
                    "genetic_status"
                ],
                "rare": embryo["rare"],
                "born": True
            })

        father_names = []

        for kitten in kittens:
            father_name = kitten[
                "father_name"
            ]

            if father_name not in father_names:
                father_names.append(
                    father_name
                )

        litter = {
            "name": "cat_litter_born",
            "litter_number": litter_number,
            "mother": mother["name"],
            "father_names": father_names,
            "multiple_sires": (
                len(father_names) > 1
            ),
            "embryos_present": len(
                embryos
            ),
            "kittens_born": len(
                kittens
            ),
            "kitten_names": [
                kitten["name"]
                for kitten in kittens
            ],
            "birth_results": birth_results,
            "pregnancy_day": pregnancy_day,
            "gestation_days": gestation_days,
            "birth_day": current_day,
            "born": True
        }

        reproduction[
            "pregnant"
        ] = False
        reproduction[
            "pregnancy_day"
        ] = None
        reproduction[
            "gestation_days"
        ] = None
        reproduction[
            "expected_birth_day"
        ] = None
        reproduction[
            "mating_window_open"
        ] = False
        reproduction[
            "estrus_active"
        ] = False
        reproduction[
            "mating_contacts"
        ] = []
        reproduction[
            "potential_fathers"
        ] = []
        reproduction[
            "father_name"
        ] = None
        reproduction[
            "father_names"
        ] = []
        reproduction[
            "embryos"
        ] = []
        reproduction[
            "litters_born"
        ] = litter_number
        reproduction[
            "last_litter"
        ] = litter
        reproduction.setdefault(
            "litters",
            []
        ).append(
            litter
        )

        self.history.append(
            litter
        )

        self.universe.quantum_events.append(
            litter
        )

        return {
            **litter,
            "kittens": kittens
        }

    def _next_kitten_name(
        self
    ):
        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if cats_layer is None:
            raise RuntimeError(
                "Kitten birth requires cats_layer."
            )

        existing_names = {
            cat.get("name")
            for cat in cats_layer.cats
        }

        number = 1

        while True:
            name = (
                f"kitten_{number:04d}"
            )

            if name not in existing_names:
                return name

            number += 1