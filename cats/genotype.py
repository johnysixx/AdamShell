from dataclasses import dataclass
from typing import ClassVar


@dataclass(slots=True)
class CatParentalContribution:
    from_mother: str | None
    from_father: str | None

    def to_dict(self):
        return {
            "from_mother": self.from_mother,
            "from_father": self.from_father,
        }


@dataclass(slots=True)
class CatInheritanceRecord:
    sex_chromosomes: CatParentalContribution
    orange_locus: CatParentalContribution
    autosomal_loci: dict[str, CatParentalContribution]

    def __post_init__(self):
        if not isinstance(
            self.sex_chromosomes,
            CatParentalContribution,
        ):
            raise TypeError(
                "sex_chromosomes inheritance must be "
                "a CatParentalContribution object."
            )

        if not isinstance(
            self.orange_locus,
            CatParentalContribution,
        ):
            raise TypeError(
                "orange_locus inheritance must be "
                "a CatParentalContribution object."
            )

        if not isinstance(self.autosomal_loci, dict):
            raise TypeError(
                "autosomal_loci inheritance must be a locus map."
            )

        self.autosomal_loci = dict(self.autosomal_loci)

        for contribution in self.autosomal_loci.values():
            if not isinstance(
                contribution,
                CatParentalContribution,
            ):
                raise TypeError(
                    "autosomal_loci inheritance values must be "
                    "CatParentalContribution objects."
                )

    def to_dict(self):
        return {
            "sex_chromosomes": (
                self.sex_chromosomes.to_dict()
            ),
            "orange_locus": self.orange_locus.to_dict(),
            "autosomal_loci": {
                locus: contribution.to_dict()
                for locus, contribution
                in self.autosomal_loci.items()
            },
        }


@dataclass(slots=True)
class CatGenotype:
    sex: str
    sex_chromosomes: tuple[str, ...]
    orange_locus: tuple[str, ...]
    autosomal_loci: dict[str, tuple[str, str]]
    lethal_mutations: tuple[str, ...]
    origin: str
    inheritance_record: CatInheritanceRecord | None = None

    AUTOSOMAL_LOCI: ClassVar[dict[str, set[str]]] = {
        "black": {
            "B",
            "b",
            "bl",
        },
        "dilution": {
            "D",
            "d",
        },
        "agouti": {
            "A",
            "a",
        },
        "white_spotting": {
            "S",
            "s",
        },
        "colorpoint": {
            "C",
            "cb",
            "cs",
            "c",
        },
        "longhair": {
            "L",
            "l",
        },
    }

    ORANGE_ALLELES: ClassVar[set[str]] = {
        "O",
        "o",
    }

    def __post_init__(self):
        self.sex_chromosomes = tuple(
            self.sex_chromosomes
        )
        self.orange_locus = tuple(
            self.orange_locus
        )

        if not isinstance(self.autosomal_loci, dict):
            raise TypeError(
                "autosomal_loci must be a locus map."
            )

        self.autosomal_loci = {
            locus: tuple(alleles)
            for locus, alleles
            in self.autosomal_loci.items()
        }
        self.lethal_mutations = tuple(
            self.lethal_mutations
        )

        if (
            self.inheritance_record is not None
            and not isinstance(
                self.inheritance_record,
                CatInheritanceRecord,
            )
        ):
            raise TypeError(
                "inheritance_record must be a "
                "CatInheritanceRecord object."
            )

    @classmethod
    def create_founder(
        cls,
        sex,
        autosomal_loci=None,
        orange_locus=None,
        sex_chromosomes=None,
        lethal_mutations=None,
    ):
        if sex == "female":
            resolved_chromosomes = tuple(
                sex_chromosomes
                or (
                    "X",
                    "X",
                )
            )

            default_orange = (
                "o",
                "o",
            )

        elif sex == "male":
            resolved_chromosomes = tuple(
                sex_chromosomes
                or (
                    "X",
                    "Y",
                )
            )

            default_orange = (
                ("o", "o")
                if resolved_chromosomes
                == (
                    "X",
                    "X",
                    "Y",
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
                "B",
            ),
            "dilution": (
                "D",
                "D",
            ),
            "agouti": (
                "a",
                "a",
            ),
            "white_spotting": (
                "s",
                "s",
            ),
            "colorpoint": (
                "C",
                "C",
            ),
            "longhair": (
                "L",
                "L",
            ),
        }

        genotype = cls(
            sex=sex,
            sex_chromosomes=resolved_chromosomes,
            orange_locus=tuple(
                orange_locus
                or default_orange
            ),
            autosomal_loci={
                locus: tuple(alleles)
                for locus, alleles
                in (
                    autosomal_loci
                    or default_autosomal
                ).items()
            },
            lethal_mutations=tuple(
                lethal_mutations or ()
            ),
            origin="founder",
        )

        cls.validate(genotype)
        return genotype

    @classmethod
    def inherit(
        cls,
        mother_genotype,
        father_genotype,
        rng,
    ):
        cls.validate(mother_genotype)
        cls.validate(father_genotype)

        if mother_genotype.sex != "female":
            raise ValueError(
                "Mother genotype must be female."
            )

        if father_genotype.sex != "male":
            raise ValueError(
                "Father genotype must be male."
            )

        maternal_x_orange = rng.choice(
            list(mother_genotype.orange_locus)
        )

        paternal_chromosome = rng.choice(
            [
                "X",
                "Y",
            ]
        )

        if paternal_chromosome == "X":
            sex = "female"
            sex_chromosomes = (
                "X",
                "X",
            )

            paternal_orange = (
                father_genotype.orange_locus[0]
            )

            orange_locus = (
                maternal_x_orange,
                paternal_orange,
            )

        else:
            sex = "male"
            sex_chromosomes = (
                "X",
                "Y",
            )

            orange_locus = (
                maternal_x_orange,
            )

        inherited_loci = {}
        inheritance_record = {}

        for locus in cls.AUTOSOMAL_LOCI:
            mother_allele = rng.choice(
                list(
                    mother_genotype.autosomal_loci[
                        locus
                    ]
                )
            )

            father_allele = rng.choice(
                list(
                    father_genotype.autosomal_loci[
                        locus
                    ]
                )
            )

            inherited_loci[locus] = (
                mother_allele,
                father_allele,
            )

            inheritance_record[locus] = (
                CatParentalContribution(
                    from_mother=mother_allele,
                    from_father=father_allele,
                )
            )

        genotype = cls(
            sex=sex,
            sex_chromosomes=sex_chromosomes,
            orange_locus=orange_locus,
            autosomal_loci=inherited_loci,
            lethal_mutations=(),
            origin="parental_inheritance",
            inheritance_record=(
                CatInheritanceRecord(
                    sex_chromosomes=(
                        CatParentalContribution(
                            from_mother="X",
                            from_father=(
                                paternal_chromosome
                            ),
                        )
                    ),
                    orange_locus=(
                        CatParentalContribution(
                            from_mother=(
                                maternal_x_orange
                            ),
                            from_father=(
                                father_genotype.orange_locus[0]
                                if paternal_chromosome
                                == "X"
                                else None
                            ),
                        )
                    ),
                    autosomal_loci=(
                        inheritance_record
                    ),
                )
            ),
        )

        cls.validate(genotype)
        return genotype

    @classmethod
    def validate(cls, genotype):
        if not isinstance(genotype, cls):
            raise TypeError(
                "genotype must be a CatGenotype object."
            )

        sex = genotype.sex
        chromosomes = tuple(
            genotype.sex_chromosomes
        )
        orange = tuple(
            genotype.orange_locus
        )

        if sex == "female":
            if chromosomes != (
                "X",
                "X",
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
                    "Y",
                ),
                (
                    "X",
                    "X",
                    "Y",
                ),
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
                    "Y",
                )
                else 1
            )

            if len(orange) != expected_orange_count:
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

        loci = genotype.autosomal_loci

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

    def to_dict(self):
        return {
            "sex": self.sex,
            "sex_chromosomes": tuple(
                self.sex_chromosomes
            ),
            "orange_locus": tuple(
                self.orange_locus
            ),
            "autosomal_loci": {
                locus: tuple(alleles)
                for locus, alleles
                in self.autosomal_loci.items()
            },
            "lethal_mutations": list(
                self.lethal_mutations
            ),
            "origin": self.origin,
            "inheritance_record": (
                self.inheritance_record.to_dict()
                if self.inheritance_record is not None
                else None
            ),
        }
