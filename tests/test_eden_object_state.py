import unittest
from dataclasses import FrozenInstanceError

from eden import Eden
from eden.eden_state import EdenPermissions, EdenState
from universe.universe import Universe


class MutableSerializedEdenEntity:

    def __init__(self):
        self.metadata = {
            "nested": {
                "tags": ["original"],
            },
        }

    def to_dict(self):
        return {
            "name": "test_eden_entity",
            "metadata": self.metadata,
        }


class EdenObjectStateTests(unittest.TestCase):

    def _eden(self):
        universe = Universe()
        eden = Eden(universe)

        return universe, eden

    def test_state_is_object_only(self):
        state = EdenState()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(state, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = state["day"]

    def test_initial_values_are_preserved(self):
        _, eden = self._eden()
        state = eden.eden_state

        self.assertIs(eden.state, state)
        self.assertEqual(state.name, "eden")
        self.assertEqual(state.layer_type, "sandbox")
        self.assertEqual(state.status, "initialized")
        self.assertEqual(state.creator, "god")
        self.assertEqual(state.created_by, "god")
        self.assertEqual(state.administrator, "god")
        self.assertEqual(state.day, 0)
        self.assertEqual(state.max_day, 7)
        self.assertEqual(state.tick_count, 0)

    def test_collections_are_owned_by_state_object(self):
        _, eden = self._eden()
        state = eden.eden_state

        self.assertIs(eden.entities, state.entities)
        self.assertIs(eden.plants, state.plants)
        self.assertIs(eden.trees, state.trees)
        self.assertIs(eden.animals, state.animals)
        self.assertIs(eden.rules, state.rules)
        self.assertIs(eden.relations, state.relations)
        self.assertIs(eden.permissions, state.permissions)

    def test_permissions_are_immutable_and_detached(self):
        first = EdenState()
        second = EdenState()

        self.assertIsInstance(
            first.permissions,
            EdenPermissions,
        )
        self.assertIsNot(
            first.permissions,
            second.permissions,
        )

        expected = {
            "can_administer": ["god"],
            "can_modify": ["god"],
        }

        self.assertEqual(
            first.permissions.to_dict(),
            expected,
        )

        with self.assertRaises(FrozenInstanceError):
            first.permissions.can_modify = ("serpent",)

        with self.assertRaises(TypeError):
            _ = first.permissions["can_modify"]

        snapshot = first.to_dict()
        snapshot["permissions"]["can_modify"].append(
            "serpent"
        )

        self.assertEqual(
            first.permissions.can_modify,
            ("god",),
        )

        universe, eden = self._eden()
        public = eden.public_state

        self.assertEqual(public["permissions"], expected)
        self.assertIsInstance(
            universe.world["eden"]["permissions"],
            dict,
        )

        public["permissions"]["can_modify"].append(
            "serpent"
        )

        self.assertEqual(
            eden.permissions.can_modify,
            ("god",),
        )

    def test_permissions_setter_requires_object(self):
        _, eden = self._eden()

        permissions = EdenPermissions(
            can_modify=("god", "serpent"),
        )
        eden.permissions = permissions

        self.assertIs(eden.permissions, permissions)
        self.assertIs(
            eden.eden_state.permissions,
            permissions,
        )

        with self.assertRaises(TypeError):
            eden.permissions = {
                "can_modify": ["god"],
            }

        self.assertIs(eden.permissions, permissions)

    def test_world_keeps_object_and_dict_boundaries(self):
        universe, eden = self._eden()

        self.assertIs(
            universe.world["eden_state"],
            eden.eden_state,
        )
        self.assertIsInstance(universe.world["eden"], dict)
        self.assertIsInstance(
            universe.world["eden"]["eden_state"],
            dict,
        )

    def test_existing_public_metadata_is_preserved(self):
        universe, eden = self._eden()
        boundary = universe.world["eden"]

        self.assertEqual(boundary["name"], "eden")
        self.assertEqual(boundary["type"], "sandbox")
        self.assertEqual(boundary["state"], "initialized")
        self.assertEqual(boundary["creator"], "god")
        self.assertEqual(boundary["created_by"], "god")
        self.assertEqual(boundary["administrator"], "god")
        self.assertEqual(
            boundary["permissions"],
            {
                "can_administer": ["god"],
                "can_modify": ["god"],
            },
        )
        self.assertIsInstance(boundary["permissions"], dict)

    def test_add_entity_mutates_same_state_object(self):
        universe, eden = self._eden()
        state = eden.eden_state
        entity = {"name": "adam"}

        eden.add_entity(entity)

        self.assertIs(eden.eden_state, state)
        self.assertEqual(state.entities, [entity])
        self.assertEqual(
            universe.world["eden"]["eden_state"]["entities"],
            [entity],
        )

    def test_tick_mutates_same_state_object(self):
        universe, eden = self._eden()
        state = eden.eden_state

        eden.tick()

        self.assertIs(eden.eden_state, state)
        self.assertEqual(state.tick_count, 1)
        self.assertEqual(state.day, 1)
        self.assertEqual(
            universe.world["eden"]["eden_state"]["day"],
            1,
        )

    def test_creation_days_keep_live_world_collections(self):
        universe, eden = self._eden()

        eden.tick()
        eden.tick()
        eden.tick()

        self.assertIs(
            universe.world["eden_plants"],
            eden.eden_state.plants,
        )
        self.assertIs(
            universe.world["eden_trees"],
            eden.eden_state.trees,
        )
        self.assertIs(
            universe.world["eden_animals"],
            eden.eden_state.animals,
        )
        self.assertIs(
            universe.world["eden_entities"],
            eden.eden_state.entities,
        )

    def test_public_state_snapshot_is_detached(self):
        _, eden = self._eden()
        snapshot = eden.public_state["eden_state"]

        snapshot["permissions"]["can_modify"].append(
            "serpent"
        )
        snapshot["entities"].append("changed")

        self.assertEqual(
            eden.eden_state.permissions.can_modify,
            ("god",),
        )
        self.assertEqual(eden.eden_state.entities, [])

    def test_serialized_entity_snapshot_detaches_nested_data(self):
        entity = MutableSerializedEdenEntity()

        state = EdenState(
            entities=[entity],
        )

        first = state.to_dict()
        second = state.to_dict()

        first["entities"][0]["metadata"][
            "nested"
        ]["tags"].append("snapshot_only")

        self.assertEqual(
            entity.metadata["nested"]["tags"],
            ["original"],
        )

        self.assertEqual(
            second["entities"][0]["metadata"][
                "nested"
            ]["tags"],
            ["original"],
        )

        self.assertEqual(
            state.to_dict()["entities"][0][
                "metadata"
            ]["nested"]["tags"],
            ["original"],
        )

        self.assertIs(
            state.entities[0],
            entity,
        )

    def test_eden_public_snapshot_ignores_live_entity_changes(self):
        universe, eden = self._eden()
        entity = MutableSerializedEdenEntity()

        eden.add_entity(entity)

        self.assertIs(
            eden.entities[0],
            entity,
        )

        snapshot = eden.public_state["eden_state"]
        world_snapshot = universe.world[
            "eden"
        ]["eden_state"]

        entity.metadata["nested"][
            "tags"
        ].append("live_change")

        self.assertEqual(
            snapshot["entities"][0]["metadata"][
                "nested"
            ]["tags"],
            ["original"],
        )

        self.assertEqual(
            world_snapshot["entities"][0][
                "metadata"
            ]["nested"]["tags"],
            ["original"],
        )

        self.assertEqual(
            eden.public_state["eden_state"][
                "entities"
            ][0]["metadata"]["nested"]["tags"],
            ["original", "live_change"],
        )

        self.assertIs(
            eden.eden_state.entities[0],
            entity,
        )

    def test_all_eden_entity_collections_keep_live_identity(self):
        entity = MutableSerializedEdenEntity()

        state = EdenState(
            entities=[entity],
            plants=[entity],
            trees=[entity],
            animals=[entity],
        )

        snapshot = state.to_dict()

        for collection in (
            "entities",
            "plants",
            "trees",
            "animals",
        ):
            self.assertIs(
                getattr(state, collection)[0],
                entity,
            )

            self.assertEqual(
                snapshot[collection][0][
                    "metadata"
                ]["nested"]["tags"],
                ["original"],
            )

        snapshot["plants"][0]["metadata"][
            "nested"
        ]["tags"].append("snapshot_only")

        self.assertEqual(
            entity.metadata["nested"]["tags"],
            ["original"],
        )

        self.assertEqual(
            snapshot["trees"][0]["metadata"][
                "nested"
            ]["tags"],
            ["original"],
        )

        self.assertEqual(
            state.to_dict()["plants"][0][
                "metadata"
            ]["nested"]["tags"],
            ["original"],
        )

    def test_nested_rules_snapshots_are_independent(self):
        rule = {
            "name": "eden_rule",
            "conditions": {
                "steps": ["original"],
            },
        }

        state = EdenState(
            rules=[rule],
        )

        first = state.to_dict()
        second = state.to_dict()

        first["rules"][0]["conditions"][
            "steps"
        ].append("snapshot_only")

        self.assertEqual(
            rule["conditions"]["steps"],
            ["original"],
        )

        self.assertEqual(
            second["rules"][0][
                "conditions"
            ]["steps"],
            ["original"],
        )

        self.assertEqual(
            state.to_dict()["rules"][0][
                "conditions"
            ]["steps"],
            ["original"],
        )

        self.assertIs(
            state.rules[0],
            rule,
        )

        self.assertIsNot(
            first["rules"][0],
            rule,
        )

    def test_nested_relations_snapshots_are_independent(self):
        relation = {
            "participants": ["adam", "eva"],
            "metadata": {
                "history": ["original"],
            },
        }

        state = EdenState(
            relations=[relation],
        )

        first = state.to_dict()
        second = state.to_dict()

        first["relations"][0]["metadata"][
            "history"
        ].append("snapshot_only")

        self.assertEqual(
            relation["metadata"]["history"],
            ["original"],
        )

        self.assertEqual(
            second["relations"][0][
                "metadata"
            ]["history"],
            ["original"],
        )

        self.assertEqual(
            state.to_dict()["relations"][0][
                "metadata"
            ]["history"],
            ["original"],
        )

        self.assertIs(
            state.relations[0],
            relation,
        )

        self.assertIsNot(
            first["relations"][0],
            relation,
        )

    def test_eden_public_snapshot_preserves_live_registries(self):
        _, eden = self._eden()

        rule = {
            "name": "eden_rule",
            "metadata": {
                "flags": ["original"],
            },
        }

        relation = {
            "name": "eden_relation",
            "metadata": {
                "notes": ["original"],
            },
        }

        eden.rules.append(rule)
        eden.relations.append(relation)

        self.assertIs(
            eden.rules,
            eden.eden_state.rules,
        )

        self.assertIs(
            eden.relations,
            eden.eden_state.relations,
        )

        self.assertIs(
            eden.rules[0],
            rule,
        )

        self.assertIs(
            eden.relations[0],
            relation,
        )

        snapshot = eden.public_state[
            "eden_state"
        ]

        rule["metadata"]["flags"].append(
            "live_change"
        )

        relation["metadata"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["rules"][0][
                "metadata"
            ]["flags"],
            ["original"],
        )

        self.assertEqual(
            snapshot["relations"][0][
                "metadata"
            ]["notes"],
            ["original"],
        )

        current = eden.public_state[
            "eden_state"
        ]

        self.assertEqual(
            current["rules"][0][
                "metadata"
            ]["flags"],
            ["original", "live_change"],
        )

        self.assertEqual(
            current["relations"][0][
                "metadata"
            ]["notes"],
            ["original", "live_change"],
        )

        snapshot["rules"].clear()
        snapshot["relations"].clear()

        self.assertEqual(
            len(eden.rules),
            1,
        )

        self.assertEqual(
            len(eden.relations),
            1,
        )

    def test_to_dict_is_detached_boundary(self):
        state = EdenState()
        snapshot = state.to_dict()

        snapshot["permissions"]["can_administer"].append(
            "serpent"
        )
        snapshot["animals"].append("changed")

        self.assertEqual(
            state.permissions.can_administer,
            ("god",),
        )
        self.assertEqual(state.animals, [])


if __name__ == "__main__":
    unittest.main()
