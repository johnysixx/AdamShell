from dataclasses import replace

from universe.logger import UniverseLogger
from meeting_place.bar_objects import (
    BarTab,
    BarTabItem,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)
from meeting_place.bar_payment_state import BarPaymentState


class CashRegister:

    def __init__(self):
        self.name = "cash_register"
        self.type = "bar_cash_register"
        self.location = "on_bar_counter"
        self.receipts = []
        self.receipt_count = 0
        self.open_tabs = {}
        UniverseLogger.boot(
            "CASH REGISTER PLACED ON BAR COUNTER"
        )

    def _entity_identity(self, entity):
        return (
            getattr(entity, "name", None),
            getattr(entity, "type", None),
        )

    def open_tab(self, entity):
        entity_name, entity_type = (
            self._entity_identity(entity)
        )

        tab = self.open_tabs.get(
            entity_name
        )

        if tab is None:
            tab = BarTab(
                guest=entity_name,
                guest_type=entity_type,
            )

            self.open_tabs[
                entity_name
            ] = tab

        return tab

    def _drink_identity(self, drink):
        if isinstance(
            drink,
            dict,
        ):
            return (
                drink.get("name"),
                drink.get("category"),
            )

        return (
            getattr(
                drink,
                "name",
                str(drink),
            ),
            getattr(
                drink,
                "category",
                None,
            ),
        )

    def add_to_tab(
        self,
        entity,
        drink,
    ):
        tab = self.open_tab(
            entity
        )

        (
            drink_name,
            drink_category,
        ) = self._drink_identity(
            drink
        )

        tab.add_item(
            drink=drink_name,
            drink_category=drink_category,
        )

        return tab

    def _require_receipts(self):
        if not isinstance(
            self.receipts,
            list,
        ):
            raise TypeError(
                "Cash register receipts "
                "must be list."
            )

        for receipt in self.receipts:
            if not isinstance(
                receipt,
                BarReceiptState,
            ):
                raise TypeError(
                    "Cash register receipt "
                    "must be "
                    "BarReceiptState."
                )

        return self.receipts

    def receipt_records(self):
        return tuple(
            self._require_receipts()
        )

    def _store_receipt(
        self,
        receipt,
    ):
        if not isinstance(
            receipt,
            BarReceiptState,
        ):
            raise TypeError(
                "Cash register receipt "
                "must be "
                "BarReceiptState."
            )

        self._require_receipts().append(
            receipt
        )

        return receipt

    def print_open_tab_receipt(
        self,
        entity,
    ):
        (
            entity_name,
            entity_type,
        ) = self._entity_identity(
            entity
        )

        tab = self.open_tab(
            entity
        )

        self.receipt_count += 1

        receipt = BarReceiptState(
            receipt_number=
                self.receipt_count,
            type=
                "bar_open_tab_receipt",
            guest=
                entity_name,
            guest_type=
                entity_type,
            status=
                "open_unpaid",
            paid=False,
            items=[
                BarTabItem(
                    drink=
                        item.drink,
                    drink_category=
                        item.drink_category,
                )
                for item
                in tab.items
            ],
            payment=None,
            message=(
                "ACCOUNT OPEN - "
                "PAY ON DEPARTURE"
            ),
        )

        self._store_receipt(
            receipt
        )

        tab.latest_receipt_number = (
            receipt.receipt_number
        )

        UniverseLogger.event(
            "CASH REGISTER PRINTED "
            "OPEN TAB: "
            f"{receipt.receipt_number} "
            f"FOR={entity_name} "
            f"ITEMS={len(receipt.items)}"
        )

        return receipt

    def print_staff_purchase_receipt(
        self,
        entity,
        drinks,
    ):
        (
            entity_name,
            entity_type,
        ) = self._entity_identity(
            entity
        )

        self.receipt_count += 1
        items = []

        for drink in drinks:
            (
                drink_name,
                drink_category,
            ) = self._drink_identity(
                drink
            )

            items.append(
                BarTabItem(
                    drink=drink_name,
                    drink_category=
                        drink_category,
                )
            )

        receipt = BarReceiptState(
            receipt_number=
                self.receipt_count,
            type=
                "bar_receipt",
            receipt_kind=
                "staff_purchase",
            guest=
                entity_name,
            guest_type=
                entity_type,
            items=items,
            payment=None,
            paid=False,
            charge=0,
            message=
                "PERSONALNI NAKUP",
        )

        self._store_receipt(
            receipt
        )

        UniverseLogger.event(
            "CASH REGISTER PRINTED "
            "STAFF PURCHASE: "
            f"{self.receipt_count} "
            f"FOR={entity_name} "
            f"ITEMS={len(items)}"
        )

        return receipt

    def print_receipt(
        self,
        entity,
        drink,
        payment: BarPaymentState,
    ):
        if not isinstance(payment, BarPaymentState):
            raise TypeError("Cash register payment must be BarPaymentState.")

        self.receipt_count += 1

        entity_name = getattr(
            entity,
            "name",
            None,
        )

        entity_type = getattr(
            entity,
            "type",
            None,
        )

        (
            drink_name,
            drink_category,
        ) = self._drink_identity(
            drink
        )

        if entity_type == "god":
            receipt_kind = (
                "god_free_drink_note"
            )
            message = (
                "BOHOV? ZDE PIJ? ZDARMA."
            )

        else:
            receipt_kind = (
                "payment_receipt"
            )
            message = (
                "D?KUJEME ZA N?V?T?VU."
            )

        receipt = BarReceiptState(
            receipt_number=
                self.receipt_count,
            type="bar_receipt",
            receipt_kind=
                receipt_kind,
            guest=entity_name,
            guest_type=
                entity_type,
            drink=drink_name,
            drink_category=
                drink_category,
            payment=replace(
                payment
            ),
            message=message,
        )

        self._store_receipt(
            receipt
        )

        UniverseLogger.event(
            "CASH REGISTER PRINTED "
            "RECEIPT: "
            f"{self.receipt_count} "
            f"FOR={entity_name} "
            f"DRINK={drink_name}"
        )

        return receipt
