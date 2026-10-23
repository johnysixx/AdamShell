from dataclasses import (
    dataclass,
    field,
)

from core.entity.domain_object import (
    DomainObject,
)


@dataclass(slots=True)
class CatGroupRoleHolderRecord:

    role: str

    holders: list = field(
        default_factory=list
    )

    def __post_init__(
        self,
    ):
        self.role = str(
            self.role
        )

        if not self.role:
            raise ValueError(
                "Cat group role holder record "
                "requires role."
            )

        normalized = []

        for holder in self.holders:
            holder = str(
                holder
            )

            if (
                holder
                and holder not in normalized
            ):
                normalized.append(
                    holder
                )

        self.holders = normalized

    def add_holder(
        self,
        cat_name,
    ):
        cat_name = str(
            cat_name
        )

        if not cat_name:
            raise ValueError(
                "Cat group role holder requires "
                "cat name."
            )

        if cat_name not in self.holders:
            self.holders.append(
                cat_name
            )

        return self

    def remove_holder(
        self,
        cat_name,
    ):
        cat_name = str(
            cat_name
        )

        if cat_name in self.holders:
            self.holders.remove(
                cat_name
            )

            return True

        return False

    def has_holder(
        self,
        cat_name,
    ):
        return (
            str(cat_name)
            in self.holders
        )

    def holder_names(
        self,
    ):
        return tuple(
            self.holders
        )


class CatGroupRoleRegistry(
    DomainObject
):

    def __init__(
        self,
    ):
        self._records = []

    @property
    def is_empty(
        self,
    ):
        return not self._records

    @property
    def count(
        self,
    ):
        return len(
            self._records
        )

    def store(
        self,
        record,
    ):
        if not isinstance(
            record,
            CatGroupRoleHolderRecord,
        ):
            raise TypeError(
                "Cat group role registry requires "
                "CatGroupRoleHolderRecord."
            )

        role = str(
            record.role
        )

        if not role:
            raise ValueError(
                "Stored cat group role holder record "
                "requires role."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.role == role:
                self._records[
                    index
                ] = record

                return record

        self._records.append(
            record
        )

        return record

    def ensure(
        self,
        role,
    ):
        role = str(
            role
        )

        if not role:
            raise ValueError(
                "Cat group role registry requires role."
            )

        current = self.record(
            role
        )

        if current is not None:
            return current

        return self.store(
            CatGroupRoleHolderRecord(
                role=role
            )
        )

    def record(
        self,
        role,
    ):
        role = str(
            role
        )

        for record in self.records():
            if record.role == role:
                return record

        return None

    def has(
        self,
        role,
    ):
        return (
            self.record(
                role
            )
            is not None
        )

    def has_holders(
        self,
        role,
    ):
        return bool(
            self.holders(
                role
            )
        )

    def holders(
        self,
        role,
    ):
        record = self.record(
            role
        )

        if record is None:
            return ()

        return record.holder_names()

    def assign(
        self,
        role,
        cat_name,
    ):
        record = self.ensure(
            role
        )

        record.add_holder(
            cat_name
        )

        return record

    def release_holder(
        self,
        role,
        cat_name,
    ):
        record = self.record(
            role
        )

        if record is None:
            return False

        return record.remove_holder(
            cat_name
        )

    def release(
        self,
        role,
    ):
        role = str(
            role
        )

        for index, record in enumerate(
            self.records()
        ):
            if record.role == role:
                del self._records[
                    index
                ]

                return record

        return None

    def records(
        self,
    ):
        for record in self._records:
            if not isinstance(
                record,
                CatGroupRoleHolderRecord,
            ):
                raise TypeError(
                    "Cat group role registry "
                    "contains invalid runtime state."
                )

            if (
                not isinstance(
                    record.role,
                    str,
                )
                or not record.role
            ):
                raise ValueError(
                    "Cat group role record requires role."
                )

        return tuple(
            self._records
        )


@dataclass(slots=True)
class CatGroupRoleSpecializationRecord:

    base_role: str

    specialization: str

    holders: list = field(
        default_factory=list
    )

    def __post_init__(
        self,
    ):
        self.base_role = str(
            self.base_role
        )

        self.specialization = str(
            self.specialization
        )

        if not self.base_role:
            raise ValueError(
                "Cat group role specialization "
                "requires base_role."
            )

        if not self.specialization:
            raise ValueError(
                "Cat group role specialization "
                "requires specialization."
            )

        normalized = []

        for holder in self.holders:
            holder = str(
                holder
            )

            if (
                holder
                and holder not in normalized
            ):
                normalized.append(
                    holder
                )

        self.holders = normalized

    def add_holder(
        self,
        cat_name,
    ):
        cat_name = str(
            cat_name
        )

        if not cat_name:
            raise ValueError(
                "Cat group role specialization holder "
                "requires cat name."
            )

        if cat_name not in self.holders:
            self.holders.append(
                cat_name
            )

        return self

    def remove_holder(
        self,
        cat_name,
    ):
        cat_name = str(
            cat_name
        )

        if cat_name in self.holders:
            self.holders.remove(
                cat_name
            )

            return True

        return False

    def holder_names(
        self,
    ):
        return tuple(
            self.holders
        )


class CatGroupRoleSpecializationRegistry(
    DomainObject
):

    def __init__(
        self,
    ):
        self._records = []

    @property
    def is_empty(
        self,
    ):
        return not self._records

    @property
    def count(
        self,
    ):
        return len(
            self._records
        )

    def store(
        self,
        record,
    ):
        if not isinstance(
            record,
            CatGroupRoleSpecializationRecord,
        ):
            raise TypeError(
                "Cat group role specialization registry "
                "requires "
                "CatGroupRoleSpecializationRecord."
            )

        current = self.record(
            record.base_role,
            record.specialization,
        )

        if current is not None:
            index = self._records.index(
                current
            )

            self._records[
                index
            ] = record

            return record

        self._records.append(
            record
        )

        return record

    def ensure(
        self,
        base_role,
        specialization,
    ):
        base_role = str(
            base_role
        )

        specialization = str(
            specialization
        )

        if not base_role:
            raise ValueError(
                "Cat group role specialization "
                "requires base_role."
            )

        if not specialization:
            raise ValueError(
                "Cat group role specialization "
                "requires specialization."
            )

        current = self.record(
            base_role,
            specialization,
        )

        if current is not None:
            return current

        return self.store(
            CatGroupRoleSpecializationRecord(
                base_role=base_role,
                specialization=specialization,
            )
        )

    def record(
        self,
        base_role,
        specialization,
    ):
        base_role = str(
            base_role
        )

        specialization = str(
            specialization
        )

        for record in self.records():
            if (
                record.base_role
                == base_role
                and record.specialization
                == specialization
            ):
                return record

        return None

    def has(
        self,
        base_role,
        specialization,
    ):
        return (
            self.record(
                base_role,
                specialization,
            )
            is not None
        )

    def holders(
        self,
        base_role,
        specialization,
    ):
        record = self.record(
            base_role,
            specialization,
        )

        if record is None:
            return ()

        return record.holder_names()

    def assign(
        self,
        base_role,
        specialization,
        cat_name,
    ):
        record = self.ensure(
            base_role,
            specialization,
        )

        record.add_holder(
            cat_name
        )

        return record

    def release_holder(
        self,
        base_role,
        specialization,
        cat_name,
    ):
        record = self.record(
            base_role,
            specialization,
        )

        if record is None:
            return False

        return record.remove_holder(
            cat_name
        )

    def records(
        self,
        base_role=None,
    ):
        result = []

        for record in self._records:
            if not isinstance(
                record,
                CatGroupRoleSpecializationRecord,
            ):
                raise TypeError(
                    "Cat group role specialization "
                    "registry contains invalid "
                    "runtime state."
                )

            if (
                not isinstance(
                    record.base_role,
                    str,
                )
                or not record.base_role
            ):
                raise ValueError(
                    "Cat group role specialization "
                    "record requires base_role."
                )

            if (
                not isinstance(
                    record.specialization,
                    str,
                )
                or not record.specialization
            ):
                raise ValueError(
                    "Cat group role specialization "
                    "record requires specialization."
                )

            if (
                base_role is None
                or record.base_role
                == str(base_role)
            ):
                result.append(
                    record
                )

        return tuple(
            result
        )
