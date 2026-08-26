import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_memory_system import (
    CatGroupMemorySystem
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem
)
from cats.cat_group_federation_system import (
    CatGroupFederationSystem
)
from cats.cat_group_diplomatic_lifecycle import (
    CatGroupDiplomaticLifecycle
)


class CatGroupFederationKnowledgeTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first_cat = self.cats.create_cat(
            name="first_cat",
            color="black",
            fur_length="short"
        )

        self.second_cat = self.cats.create_cat(
            name="second_cat",
            color="white",
            fur_length="short"
        )

        self.third_cat = self.cats.create_cat(
            name="third_cat",
            color="gray",
            fur_length="short"
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first_cat,
                name="first"
            )[
                "group_id"
            ]
        )

        self.second_group = (
            self.groups.create_group(
                self.second_cat,
                name="second"
            )[
                "group_id"
            ]
        )

        self.third_group = (
            self.groups.create_group(
                self.third_cat,
                name="third"
            )[
                "group_id"
            ]
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

    def test_cat_can_contribute_personal_knowledge(
        self
    ):
        result = self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="safe_back_room",
            content={
                "layer": "meeting_place",
                "location": "back_room",
                "safe": True
            },
            category="place",
            confidence=1.0,
            verified=True
        )

        self.assertTrue(
            result["contributed"]
        )

        record = (
            self.groups.groups[
                self.first_group
            ][
                "knowledge"
            ][
                "safe_back_room"
            ]
        )

        self.assertEqual(
            record[
                "origin_cat"
            ],
            self.first_cat.name
        )

        self.assertTrue(
            record[
                "verified"
            ]
        )

    def test_group_information_is_not_personal_verification(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="box_warning",
            content={
                "danger": "cronenberg"
            },
            category="danger",
            confidence=0.9,
            verified=True
        )

        listener = self.cats.create_cat(
            name="listener_cat",
            color="orange",
            fur_length="short"
        )

        joined = self.groups.add_member(
            self.first_group,
            listener,
            self.cats.cats
        )

        self.assertTrue(
            joined["joined"]
        )

        self.knowledge.share_with_group_members(
            self.first_group,
            self.cats.cats,
            "box_warning"
        )

        received = (
            listener
            .knowledge[
                "group_received_knowledge"
            ][
                "box_warning"
            ]
        )

        self.assertFalse(
            received[
                "verified"
            ]
        )

        self.assertEqual(
            received[
                "received_via"
            ],
            "own_group"
        )

    def test_transmission_reduces_confidence(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="safe_route",
            content={
                "route": "bar_to_library"
            },
            category="navigation",
            confidence=1.0
        )

        self.knowledge.transmit_between_groups(
            self.first_group,
            self.second_group,
            "safe_route"
        )

        received = (
            self.groups.groups[
                self.second_group
            ][
                "knowledge"
            ][
                "safe_route"
            ]
        )

        self.assertLess(
            received[
                "confidence"
            ],
            1.0
        )

        self.assertFalse(
            received[
                "verified"
            ]
        )

    def test_verification_can_raise_confidence(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="safe_route",
            content={
                "route": "bar_to_library"
            },
            category="navigation",
            confidence=0.5,
            verified=False
        )

        before = (
            self.groups.groups[
                self.first_group
            ][
                "knowledge"
            ][
                "safe_route"
            ][
                "confidence"
            ]
        )

        self.knowledge.verify(
            self.first_group,
            self.first_cat,
            "safe_route",
            confirmed=True
        )

        after = (
            self.groups.groups[
                self.first_group
            ][
                "knowledge"
            ][
                "safe_route"
            ][
                "confidence"
            ]
        )

        self.assertGreater(
            after,
            before
        )

    def test_contradiction_reduces_confidence(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="box_warning",
            content={
                "danger": "cronenberg"
            },
            category="danger",
            confidence=0.8
        )

        self.knowledge.verify(
            self.first_group,
            self.first_cat,
            "box_warning",
            confirmed=False
        )

        record = (
            self.groups.groups[
                self.first_group
            ][
                "knowledge"
            ][
                "box_warning"
            ]
        )

        self.assertLess(
            record[
                "confidence"
            ],
            0.8
        )

    def test_groups_can_form_knowledge_federation(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        memory.record_cooperation(
            self.first_group,
            self.second_group,
            "knowledge_exchange"
        )

        federation = (
            CatGroupFederationSystem(
                self.groups
            )
        )

        created = federation.create(
            self.first_group,
            name="cat_knowledge_network"
        )

        result = federation.admit(
            created[
                "federation_id"
            ],
            self.second_group
        )

        self.assertTrue(
            result["admitted"]
        )

    def test_federation_propagates_knowledge_between_groups(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="cronenberg_scent",
            content={
                "aroma": "cronenberg"
            },
            category="aroma",
            confidence=1.0
        )

        federation = (
            CatGroupFederationSystem(
                self.groups
            )
        )

        created = federation.create(
            self.first_group
        )

        federation.admit(
            created[
                "federation_id"
            ],
            self.second_group
        )

        result = federation.share_knowledge(
            created[
                "federation_id"
            ],
            self.first_group,
            "cronenberg_scent"
        )

        self.assertTrue(
            result["shared"]
        )

        self.assertIn(
            "cronenberg_scent",
            self.groups.groups[
                self.second_group
            ][
                "knowledge"
            ]
        )

    def test_ordinary_conflict_memory_can_decay(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        event = {
            "conflict": True,
            "winner": self.first_group,
            "loser": self.second_group
        }

        memory.remember_encounter(
            self.first_group,
            self.second_group,
            event
        )

        lifecycle = (
            CatGroupDiplomaticLifecycle(
                self.groups
            )
        )

        lifecycle.advance_relation(
            self.second_group,
            self.first_group
        )

        remembered = (
            memory.relation_memory(
                self.second_group,
                self.first_group
            )
        )

        self.assertEqual(
            remembered[
                "conflicts"
            ],
            0
        )

    def test_betrayal_does_not_decay_automatically(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        memory.record_betrayal(
            self.first_group,
            self.second_group,
            "false_warning"
        )

        lifecycle = (
            CatGroupDiplomaticLifecycle(
                self.groups
            )
        )

        lifecycle.advance_relation(
            self.second_group,
            self.first_group
        )

        remembered = (
            memory.relation_memory(
                self.second_group,
                self.first_group
            )
        )

        self.assertEqual(
            remembered[
                "betrayals"
            ],
            1
        )


if __name__ == "__main__":
    unittest.main()
