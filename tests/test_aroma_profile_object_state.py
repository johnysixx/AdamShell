import unittest
from universe.aroma_composition import AromaComposition

from universe.aroma_profile import (
    AromaProfile,
    AromaSurfaceResidue,
)
from universe.aroma_residue import AromaResidue


class AromaProfileObjectStateTests(unittest.TestCase):

    def test_profile_is_live_object_state(self):
        profile = AromaProfile(
            identity="cat:pazuzu",
            base_components=(
                AromaComposition.from_pairs(
                    ("cat", 1.0),
                    ("fur", 0.8),
                )
            ),
        )

        self.assertEqual(
            profile.identity,
            "cat:pazuzu",
        )
        self.assertEqual(
            profile.base_components.amount("cat"),
            1.0,
        )
        self.assertEqual(
            profile.surface_residues,
            [],
        )

    def test_surface_residue_is_object_state(self):
        profile = AromaProfile(
            identity="cat:pazuzu",
            base_components=AromaComposition.from_pairs(("cat", 1.0)),
        )

        residue = profile.add_surface(
            source="raspberry_rum",
            components=(
                AromaComposition.from_pairs(
                    ("raspberry", 1.0),
                )
            ),
            intensity=0.8,
            decay_rate=0.1,
        )

        self.assertIsInstance(
            residue,
            AromaSurfaceResidue,
        )
        self.assertIs(
            profile.surface_residues[0],
            residue,
        )
        self.assertEqual(
            residue.source,
            "raspberry_rum",
        )

    def test_profile_rejects_dict_surface_residue(self):
        with self.assertRaises(TypeError):
            AromaProfile(
                identity="legacy",
                base_components=AromaComposition.empty(),
                surface_residues=[
                    {
                        "source": "fish",
                        "components": {"fish": 1.0},
                    }
                ],
            )

    def test_aroma_residue_rejects_dict_profile(self):
        class Target:
            pass

        with self.assertRaises(TypeError):
            AromaResidue.transfer(
                source_profile={
                    "identity": "legacy",
                    "base_components": {
                        "cat": 1.0,
                    },
                },
                target=Target(),
                source_identity="legacy",
            )

    def test_aroma_residue_rejects_dict_target(self):
        profile = AromaProfile(
            identity="cat:pazuzu",
            base_components=AromaComposition.from_pairs(("cat", 1.0)),
        )

        with self.assertRaises(TypeError):
            AromaResidue.transfer(
                source_profile=profile,
                target={},
                source_identity="pazuzu",
            )

    def test_to_dict_returns_detached_snapshot(self):
        profile = AromaProfile(
            identity="cat:pazuzu",
            base_components=AromaComposition.from_pairs(("cat", 1.0)),
        )
        residue = profile.add_surface(
            source="fish",
            components=(
                AromaComposition.from_pairs(
                    ("fish", 0.5),
                )
            ),
        )

        snapshot = profile.to_dict()
        snapshot["base_components"]["cat"] = 99.0
        snapshot["surface_residues"][0]["components"]["fish"] = 99.0

        self.assertEqual(
            profile.base_components.amount("cat"),
            1.0,
        )
        self.assertEqual(
            residue.components.amount("fish"),
            0.5,
        )


if __name__ == "__main__":
    unittest.main()
