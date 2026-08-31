from universe.logger import UniverseLogger
from meeting_place.bar_objects import BarTab


class CashRegister:

    def __init__(self):
        self.name = "cash_register"
        self.type = "bar_cash_register"
        self.location = "on_bar_counter"
        self.receipts = []
        self.receipt_count = 0
        self.open_tabs = {}
        UniverseLogger.boot("CASH REGISTER PLACED ON BAR COUNTER")

    def _entity_identity(self, entity):
        return (
            getattr(entity, "name", None),
            getattr(entity, "type", None),
        )

    def open_tab(self, entity):
        entity_name, entity_type = self._entity_identity(entity)
        tab = self.open_tabs.get(entity_name)
        if tab is None:
            tab = BarTab(
                guest=entity_name,
                guest_type=entity_type,
            )
            self.open_tabs[entity_name] = tab
        return tab

    def add_to_tab(self, entity, drink):
        tab = self.open_tab(entity)
        tab.add_item(
            drink=drink["name"],
            drink_category=drink.get("category"),
        )
        return tab

    def print_open_tab_receipt(self, entity):
        entity_name, entity_type = self._entity_identity(entity)
        tab = self.open_tab(entity)
        self.receipt_count += 1
        receipt = {
            "receipt_number": self.receipt_count,
            "type": "bar_open_tab_receipt",
            "guest": entity_name,
            "guest_type": entity_type,
            "status": "open_unpaid",
            "paid": False,
            "items": [item.to_dict() for item in tab.items],
            "payment": None,
            "message": "ACCOUNT OPEN - PAY ON DEPARTURE",
        }
        self.receipts.append(receipt)
        tab.latest_receipt_number = receipt["receipt_number"]
        UniverseLogger.event(
            "CASH REGISTER PRINTED OPEN TAB: "
            f"{receipt['receipt_number']} FOR={entity_name} "
            f"ITEMS={len(receipt['items'])}"
        )
        return receipt

    def print_staff_purchase_receipt(self, entity, drinks):
        entity_name, entity_type = self._entity_identity(entity)
        self.receipt_count += 1
        items = []
        for drink in drinks:
            if isinstance(drink, dict):
                drink_name = drink.get("name")
                drink_category = drink.get("category")
            else:
                drink_name = str(drink)
                drink_category = None
            items.append({
                "drink": drink_name,
                "drink_category": drink_category,
            })
        receipt = {
            "receipt_number": self.receipt_count,
            "type": "bar_receipt",
            "receipt_kind": "staff_purchase",
            "guest": entity_name,
            "guest_type": entity_type,
            "items": items,
            "payment": None,
            "paid": False,
            "charge": 0,
            "message": "PERSONALNI NAKUP",
        }
        self.receipts.append(receipt)
        UniverseLogger.event(
            "CASH REGISTER PRINTED STAFF PURCHASE: "
            f"{self.receipt_count} FOR={entity_name} "
            f"ITEMS={len(items)}"
        )
        return receipt

    def print_receipt(self, entity, drink, payment):
        self.receipt_count += 1
        entity_name = getattr(entity, "name", None)
        entity_type = getattr(entity, "type", None)
        receipt = {
            "receipt_number": self.receipt_count,
            "type": "bar_receipt",
            "guest": entity_name,
            "guest_type": entity_type,
            "drink": drink["name"],
            "drink_category": drink.get("category"),
            "payment": dict(payment),
        }
        if entity_type == "god":
            receipt["receipt_kind"] = "god_free_drink_note"
            receipt["message"] = "BOHOV? ZDE PIJ? ZDARMA."
        else:
            receipt["receipt_kind"] = "payment_receipt"
            receipt["message"] = "D?KUJEME ZA N?V?T?VU."
        self.receipts.append(receipt)
        UniverseLogger.event(
            "CASH REGISTER PRINTED RECEIPT: "
            f"{self.receipt_count} FOR={entity_name} "
            f"DRINK={drink['name']}"
        )
        return receipt
