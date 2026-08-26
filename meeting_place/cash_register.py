from universe.logger import UniverseLogger


class CashRegister:

    def __init__(self):
        self.name = "cash_register"
        self.type = "bar_cash_register"
        self.location = "on_bar_counter"

        self.receipts = []
        self.receipt_count = 0

        UniverseLogger.boot(
            "CASH REGISTER PLACED ON BAR COUNTER"
        )

    def print_receipt(
        self,
        entity,
        drink,
        payment
    ):
        self.receipt_count += 1

        if isinstance(entity, dict):
            entity_name = entity.get(
                "name"
            )
            entity_type = entity.get(
                "type"
            )
        else:
            entity_name = getattr(
                entity,
                "name",
                None
            )
            entity_type = getattr(
                entity,
                "type",
                None
            )

        receipt = {
            "receipt_number": self.receipt_count,
            "type": "bar_receipt",
            "guest": entity_name,
            "guest_type": entity_type,
            "drink": drink["name"],
            "drink_category": drink.get(
                "category"
            ),
            "payment": dict(
                payment
            )
        }

        if entity_type == "god":
            receipt[
                "receipt_kind"
            ] = "god_free_drink_note"

            receipt[
                "message"
            ] = "BOHOV? ZDE PIJ? ZDARMA."

        else:
            receipt[
                "receipt_kind"
            ] = "payment_receipt"

            receipt[
                "message"
            ] = "D?KUJEME ZA N?V?T?VU."

        self.receipts.append(
            receipt
        )

        UniverseLogger.event(
            "CASH REGISTER PRINTED RECEIPT: "
            f"{self.receipt_count} "
            f"FOR={entity_name} "
            f"DRINK={drink['name']}"
        )

        return receipt
