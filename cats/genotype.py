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


@dataclass(slots=True, frozen=True)
class CatAutosomalInheritanceRecord:
    black: CatParentalContribution
    dilution: CatParentalContribution
    agouti: CatParentalContribution
    white_spotting: CatParentalContribution
    colorpoint: CatParentalContribution
    longhair: CatParentalContribution

    def __post_init__(self):
        for field_name in (
            "black",
            "dilution",
            "agouti",
            "white_spotting",
            "colorpoint",
            "longhair",
        ):
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                CatParentalContribution,
            ):
                raise TypeError(
                    "Autosomal inheritance loci "
                    "must contain "
                    "CatParentalContribution objects."
                )


@dataclass(slots=True, frozen=True)
class CatAutosomalGenotype:
    black: tuple[str, str]
    dilution: tuple[str, str]
    agouti: tuple[str, str]
    white_spotting: tuple[str, str]
    colorpoint: tuple[str, str]
    longhair: tuple[str, str]

    def __post_init__(self):
        for field_name in (
            "black",
            "dilution",
            "agouti",
            "white_spotting",
            "colorpoint",
            "longhair",
        ):
            alleles = getattr(
                self,
                field_name,
            )

            if not isinstance(
                alleles,
                tuple,
            ):
                raise TypeError(
                    f"{field_name} autosomal genotype "
                    "must use an allele tuple."
                )

            if len(alleles) != 2:
                raise ValueError(
                    f"{field_name} autosomal genotype "
                    "must contain two alleles."
                )


@dataclass(slots=True)
class CatInheritanceRecord:
    sex_chromosomes: CatParentalContribution
    orange_locus: CatParentalContribution
    autosomal_loci: CatAutosomalInheritanceRecord

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

        if not isinstance(
            self.autosomal_loci,
            CatAutosomalInheritanceRecord,
        ):
            raise TypeError(
                "autosomal_loci inheritance must be a "
                "CatAutosomalInheritanceRecord object."
            )

    def to_dict(self):
        return {
            "sex_chromosomes": (
                self.sex_chromosomes.to_dict()
            ),
            "orange_locus": self.orange_locus.to_dict(),
            "autosomal_loci": {
                "black": (
                    self.autosomal_loci
                    .black.to_dict()
                ),
                "dilution": (
                    self.autosomal_loci
                    .dilution.to_dict()
                ),
                "agouti": (
                    self.autosomal_loci
                    .agouti.to_dict()
                ),
                "white_spotting": (
                    self.autosomal_loci
                    .white_spotting.to_dict()
                ),
                "colorpoint": (
                    self.autosomal_loci
                    .colorpoint.to_dict()
                ),
                "longhair": (
                    self.autosomal_loci
                    .longhair.to_dict()
                ),
            },
        }


@dataclass(slots=True)
class CatGenotype:
    sex: str
    sex_chromosomes: tuple[str, ...]
    orange_locus: tuple[str, ...]
    autosomal_loci: CatAutosomalGenotype
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

        if not isinstance(
            self.autosomal_loci,
            CatAutosomalGenotype,
        ):
            raise TypeError(
                "autosomal_loci must use a "
                "CatAutosomalGenotype object."
            )
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

        default_autosomal = CatAutosomalGenotype(
            black=(
                "B",
                "B",
            ),
            dilution=(
                "D",
                "D",
            ),
            agouti=(
                "a",
                "a",
            ),
            white_spotting=(
                "s",
                "s",
            ),
            colorpoint=(
                "C",
                "C",
            ),
            longhair=(
                "L",
                "L",
            ),
        )

        if autosomal_loci is None:
            resolved_autosomal = (
                default_autosomal
            )
        elif isinstance(
            autosomal_loci,
            CatAutosomalGenotype,
        ):
            resolved_autosomal = (
                autosomal_loci
            )
        else:
            raise TypeError(
                "Founder autosomal_loci must use "
                "CatAutosomalGenotype."
            )

        genotype = cls(
            sex=sex,
            sex_chromosomes=resolved_chromosomes,
            orange_locus=tuple(
                orange_locus
                or default_orange
            ),
            autosomal_loci=(
                resolved_autosomal
            ),
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

        (
            black,
            black_inheritance,
        ) = cls._inherit_autosomal_locus(
            mother_genotype,
            father_genotype,
            "black",
            rng,
        )
        (
            dilution,
            dilution_inheritance,
        ) = cls._inherit_autosomal_locus(
            mother_genotype,
            father_genotype,
            "dilution",
            rng,
        )
        (
            agouti,
            agouti_inheritance,
        ) = cls._inherit_autosomal_locus(
            mother_genotype,
            father_genotype,
            "agouti",
            rng,
        )
        (
            white_spotting,
            white_spotting_inheritance,
        ) = cls._inherit_autosomal_locus(
            mother_genotype,
            father_genotype,
            "white_spotting",
            rng,
        )
        (
            colorpoint,
            colorpoint_inheritance,
        ) = cls._inherit_autosomal_locus(
            mother_genotype,
            father_genotype,
            "colorpoint",
            rng,
        )
        (
            longhair,
            longhair_inheritance,
        ) = cls._inherit_autosomal_locus(
            mother_genotype,
            father_genotype,
            "longhair",
            rng,
        )

        autosomal_genotype = (
            CatAutosomalGenotype(
                black=black,
                dilution=dilution,
                agouti=agouti,
                white_spotting=(
                    white_spotting
                ),
                colorpoint=colorpoint,
                longhair=longhair,
            )
        )

        autosomal_inheritance = (
            CatAutosomalInheritanceRecord(
                black=black_inheritance,
                dilution=(
                    dilution_inheritance
                ),
                agouti=agouti_inheritance,
                white_spotting=(
                    white_spotting_inheritance
                ),
                colorpoint=(
                    colorpoint_inheritance
                ),
                longhair=(
                    longhair_inheritance
                ),
            )
        )

        genotype = cls(
            sex=sex,
            sex_chromosomes=sex_chromosomes,
            orange_locus=orange_locus,
            autosomal_loci=(
                autosomal_genotype
            ),
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
                        autosomal_inheritance
                    ),
                )
            ),
        )

        cls.validate(genotype)
        return genotype

    @staticmethod
    def _inherit_autosomal_locus(
        mother_genotype,
        father_genotype,
        locus,
        rng,
    ):
        mother_allele = rng.choice(
            getattr(
                mother_genotype.autosomal_loci,
                locus,
            )
        )
        father_allele = rng.choice(
            getattr(
                father_genotype.autosomal_loci,
                locus,
            )
        )

        return (
            (
                mother_allele,
                father_allele,
            ),
            CatParentalContribution(
                from_mother=mother_allele,
                from_father=father_allele,
            ),
        )

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

        if not isinstance(
            loci,
            CatAutosomalGenotype,
        ):
            raise TypeError(
                "Genotype autosomal_loci must use "
                "CatAutosomalGenotype."
            )

        for locus, allowed in (
            cls.AUTOSOMAL_LOCI.items()
        ):
            alleles = getattr(
                loci,
                locus,
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
                "black": tuple(
                    self.autosomal_loci.black
                ),
                "dilution": tuple(
                    self.autosomal_loci.dilution
                ),
                "agouti": tuple(
                    self.autosomal_loci.agouti
                ),
                "white_spotting": tuple(
                    self.autosomal_loci
                    .white_spotting
                ),
                "colorpoint": tuple(
                    self.autosomal_loci.colorpoint
                ),
                "longhair": tuple(
                    self.autosomal_loci.longhair
                ),
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
