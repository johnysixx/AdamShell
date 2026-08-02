from cats.genotype import CatGenotype


class KittenGeneticViabilityResolver:

    @classmethod
    def resolve(
        cls,
        genotype
    ):
        try:
            CatGenotype.validate(
                genotype
            )

        except (
            ValueError,
            TypeError,
            KeyError
        ) as error:
            return {
                "name": (
                    "kitten_genetic_viability_resolved"
                ),
                "status": "nonviable",
                "viable": False,
                "rare": False,
                "reason": "invalid_genotype",
                "details": str(error),
                "special_traits": [],
                "genotype": genotype
            }

        lethal_mutations = list(
            genotype.get(
                "lethal_mutations",
                []
            )
        )

        if lethal_mutations:
            return {
                "name": (
                    "kitten_genetic_viability_resolved"
                ),
                "status": "nonviable",
                "viable": False,
                "rare": False,
                "reason": (
                    "lethal_genetic_combination"
                ),
                "details": {
                    "lethal_mutations": (
                        lethal_mutations
                    )
                },
                "special_traits": [],
                "genotype": genotype
            }

        chromosomes = tuple(
            genotype[
                "sex_chromosomes"
            ]
        )

        if (
            genotype["sex"] == "male"
            and chromosomes
            == (
                "X",
                "X",
                "Y"
            )
        ):
            traits = [
                "rare_valid_genotype",
                "xxy_male"
            ]

            orange = tuple(
                genotype[
                    "orange_locus"
                ]
            )

            if set(orange) == {
                "O",
                "o"
            }:
                traits.append(
                    "xxy_tortoiseshell_capable"
                )

            return {
                "name": (
                    "kitten_genetic_viability_resolved"
                ),
                "status": "rare_valid",
                "viable": True,
                "rare": True,
                "reason": "xxy_male",
                "details": {
                    "sex_chromosomes": (
                        chromosomes
                    )
                },
                "special_traits": traits,
                "genotype": genotype
            }

        return {
            "name": (
                "kitten_genetic_viability_resolved"
            ),
            "status": "standard",
            "viable": True,
            "rare": False,
            "reason": None,
            "details": None,
            "special_traits": [],
            "genotype": genotype
        }