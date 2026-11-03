from idea_entities import IdeaEntities
from core.entity.social_entity import SocialEntity
from universe.universe import Universe


def test_canonical_masculine_energy_conversion():
    universe = Universe()
    entities = IdeaEntities(universe)

    actor = entities.create_idea_entity(
        name="pazuzu",
        role="archetype_principle",
        active=True,
    )
    assert isinstance(actor, SocialEntity)

    actor.energy_j = 100.0
    universe.world["pazuzu_masculine_principle"] = actor

    event = (
        entities.prefysical_fire_origin
        ._convert_masculine_energy_to_heat()
    )

    assert universe.world["pazuzu_masculine_principle"] is actor
    assert actor.energy_j == 95.0
    assert event.source_energy_before_j == 100.0
    assert event.source_energy_after_j == 95.0
    assert event.converted_to_friction_heat_j == 5.0
