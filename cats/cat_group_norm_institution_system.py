from cats.cat_group_norm_institution_link_state import (
    CatNormAttachedToInstitutionResult,
    CatNormInstitutionLinkDeniedResult,
)


class CatGroupNormInstitutionSystem:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

    def attach_norm(
        self,
        group_id,
        institution_name,
        norm_id,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        institution = (
            group.institutions.get(
                institution_name
            )
        )

        norm = (
            group.norms.get(
                norm_id
            )
        )

        if (
            institution is None
            or norm is None
        ):
            return (
                CatNormInstitutionLinkDeniedResult()
            )

        if not hasattr(
            institution,
            "norms",
        ):
            institution.norms = []

        if (
            norm_id
            not in institution.norms
        ):
            institution.norms.append(
                norm_id
            )

        return (
            CatNormAttachedToInstitutionResult(
                group_id=group_id,
                institution=institution_name,
                norm_id=norm_id,
            )
        )
