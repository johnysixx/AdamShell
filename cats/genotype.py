class CatGenotype:

    AUTOSOMAL_LOCI = {
        "black": {
            "B",
            "b",
            "bl"
        },
        "dilution": {
            "D",
            "d"
        },
        "agouti": {
            "A",
            "a"
        },
        "white_spotting": {
            "S",
            "s"
        },
        "colorpoint": {
            "C",
            "cb",
            "cs",
            "c"
        },
        "longhair": {
            "L",
            "l"
        }
    }

    ORANGE_ALLELES = {
        "O",
        "o"
    }

    @classmethod
    def create_founder(
        cls,
        sex,
        autosomal_loci=None,
        orange_locus=None,
        sex_chromosomes=None,
        lethal_mutations=None
    ):
        if sex == "female":
            resolved_chromosomes = tuple(
                sex_chromosomes
                or (
                    "X",
                    "X"
                )
            )

            default_orange = (
                "o",
                "o"
            )

        elif sex == "male":
            resolved_chromosomes = tuple(
                sex_chromosomes
                or (
                    "X",
                    "Y"
                )
            )

            default_orange = (
                ("o", "o")
                if resolved_chromosomes
                == (
                    "X",
                    "X",
                    "Y"
                )
                else ("o",)
            )

        else:
            raise ValueError(
                "Cat genotype sex must be "
                "female or male."
            )

        default_autosomal = {
            "black": (
                "B",
                "B"
            ),
            "dilution": (
                "D",
                "D"
            ),
            "agouti": (
                "a",
                "a"
            ),
            "white_spotting": (
                "s",
                "s"
            ),
            "colorpoint": (
                "C",
                "C"
            ),
            "longhair": (
                "L",
                "L"
            )
        }

        genotype = {
            "sex": sex,
            "sex_chromosomes": (
                resolved_chromosomes
            ),
            "orange_locus": tuple(
                orange_locus
                or default_orange
            ),
            "autosomal_loci": {
                locus: tuple(alleles)
                for locus, alleles
                in (
                    autosomal_loci
                    or default_autosomal
                ).items()
            },
            "lethal_mutations": list(
                lethal_mutations or []
            ),
            "origin": "founder"
        }

        cls.validate(
            genotype
        )

        return genotype

    @classmethod
    def inherit(
        cls,
        mother_genotype,
        father_genotype,
        rng
    ):
        cls.validate(
            mother_genotype
        )

        cls.validate(
            father_genotype
        )

        if mother_genotype["sex"] != "female":
            raise ValueError(
                "Mother genotype must be female."
            )

        if father_genotype["sex"] != "male":
            raise ValueError(
                "Father genotype must be male."
            )

        maternal_x_orange = rng.choice(
            list(
                mother_genotype[
                    "orange_locus"
                ]
            )
        )

        paternal_chromosome = rng.choice(
            [
                "X",
                "Y"
            ]
        )

        if paternal_chromosome == "X":
            sex = "female"
            sex_chromosomes = (
                "X",
                "X"
            )

            paternal_orange = (
                father_genotype[
                    "orange_locus"
                ][0]
            )

            orange_locus = (
                maternal_x_orange,
                paternal_orange
            )

        else:
            sex = "male"
            sex_chromosomes = (
                "X",
                "Y"
            )

            orange_locus = (
                maternal_x_orange,
            )

        inherited_loci = {}
        inheritance_record = {}

        for locus in cls.AUTOSOMAL_LOCI:
            mother_allele = rng.choice(
                list(
                    mother_genotype[
                        "autosomal_loci"
                    ][locus]
                )
            )

            father_allele = rng.choice(
                list(
                    father_genotype[
                        "autosomal_loci"
                    ][locus]
                )
            )

            inherited_loci[locus] = (
                mother_allele,
                father_allele
            )

            inheritance_record[locus] = {
                "from_mother": (
                    mother_allele
                ),
                "from_father": (
                    father_allele
                )
            }

        genotype = {
            "sex": sex,
            "sex_chromosomes": (
                sex_chromosomes
            ),
            "orange_locus": (
                orange_locus
            ),
            "autosomal_loci": (
                inherited_loci
            ),
            "lethal_mutations": [],
            "origin": "parental_inheritance",
            "inheritance_record": {
                "sex_chromosomes": {
                    "from_mother": "X",
                    "from_father": (
                        paternal_chromosome
                    )
                },
                "orange_locus": {
                    "from_mother": (
                        maternal_x_orange
                    ),
                    "from_father": (
                        father_genotype[
                            "orange_locus"
                        ][0]
                        if paternal_chromosome
                        == "X"
                        else None
                    )
                },
                "autosomal_loci": (
                    inheritance_record
                )
            }
        }

        cls.validate(
            genotype
        )

        return genotype

    @classmethod
    def validate(
        cls,
        genotype
    ):
        sex = genotype.get(
            "sex"
        )

        chromosomes = tuple(
            genotype.get(
                "sex_chromosomes",
                ()
            )
        )

        orange = tuple(
            genotype.get(
                "orange_locus",
                ()
            )
        )

        if sex == "female":
            if chromosomes != (
                "X",
                "X"
            ):
                raise ValueError(
                    "Standard female genotype "
                    "must use XX."
                )

            if len(orange) != 2:
                raise ValueError(
                    "Female orange locus must "
                    "contain two alleles."
                )

        elif sex == "male":
            if chromosomes not in {
                (
                    "X",
                    "Y"
                ),
                (
                    "X",
                    "X",
                    "Y"
                )
            }:
                raise ValueError(
                    "Supported male genotype "
                    "must use XY or XXY."
                )

            expected_orange_count = (
                2
                if chromosomes
                == (
                    "X",
                    "X",
                    "Y"
                )
                else 1
            )

            if len(orange) != (
                expected_orange_count
            ):
                raise ValueError(
                    "Male orange locus does not "
                    "match the number of X chromosomes."
                )

        else:
            raise ValueError(
                "Unsupported genotype sex."
            )

        if not set(orange).issubset(
            cls.ORANGE_ALLELES
        ):
            raise ValueError(
                "Unsupported orange allele."
            )

        loci = genotype.get(
            "autosomal_loci",
            {}
        )

        missing = (
            set(cls.AUTOSOMAL_LOCI)
            - set(loci)
        )

        if missing:
            raise ValueError(
                "Missing autosomal loci: "
                + ", ".join(
                    sorted(missing)
                )
            )

        for locus, allowed in (
            cls.AUTOSOMAL_LOCI.items()
        ):
            alleles = tuple(
                loci[locus]
            )

            if len(alleles) != 2:
                raise ValueError(
                    f"{locus} must contain "
                    "two alleles."
                )

            if not set(alleles).issubset(
                allowed
            ):
                raise ValueError(
                    f"Unsupported allele "
                    f"at {locus}."
                )

        return True