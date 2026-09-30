from enum import Enum


class CatGeneticsValidationStatus(Enum):

    STANDARD_GENETICS = "standard_genetics"
    RARE_GENETIC_EXCEPTION = (
        "rare_genetic_exception"
    )
    IMPOSSIBLE_FOR_DECLARED_GENOTYPE = (
        "impossible_for_declared_genotype"
    )
    UNSUPPORTED_GENETIC_MODEL = (
        "unsupported_genetic_model"
    )
