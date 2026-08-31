from cats.cat_components import CatFamily, MaternalCare, MaternalCareReceived, SiblingPlay, SiblingRivalry, ParentalTeaching, FamilyBonding, CatGroupMembership, CatCulture, CatGroupRoles, CatMeowInvitations, CatNorms, CatNeeds, CatEmergencyNursing
from core.entity.social_entity import SocialMixin

class Cat(SocialMixin):
    """
    A living cat entity.

    Cat owns its state and behavior.
    Mapping compatibility is temporary so the existing
    feline subsystem can migrate from dictionaries
    without a flag-day rewrite.
    """

    def __init__(self, name, color, pattern, eye_color, fur_length, sex, genotype, reproduction, origin, idea_energy, memory, access, learning, personality, mind, intellect, aroma):
        self.name = name
        self.type = 'cat'
        self.state = 'created'
        self.color = color
        self.pattern = pattern
        self.eye_color = eye_color
        self.fur_length = fur_length
        self.sex = sex
        self.genotype = genotype
        self.reproduction = reproduction
        self.origin = origin
        self.idea_energy = idea_energy
        self.size = 1.0
        self.strength = 1.0
        self.cronenbergs_eaten = 0
        self.cronenberg_mass_eaten = 0.0
        self.memory = memory
        self.access = access
        self.learning = learning
        self.personality = personality
        self.mind = mind
        self.intellect = intellect
        self.knowledge = {}
        self.relationships = {}
        self.social_memory = {}
        self.territories = {}
        self.bonds = {}
        self.family = CatFamily(parents={'mother': None, 'father': None}, children=[], siblings=[], littermates=[], half_siblings=[])
        self.maternal_care = MaternalCare(active=False, kittens={}, care_events=0)
        self.maternal_care_received = MaternalCareReceived(mother=None, foster_mother=None, care_events=0, foster_care_events=0, nursing_events=0, foster_nursing_events=0, cleaning_events=0, warming_events=0, protection_events=0, retrieval_events=0, last_care_day=None, last_phase=None, needs_milk=False, needs_teaching=False, rescued_to_bar=False, garfield_advice_received=False)
        self.emergency_nursing = CatEmergencyNursing.create_state(
            name=name,
            sex=sex
        )
        self.sibling_play = SiblingPlay(play_events=0, partners={}, last_partner=None, last_play_day=None)
        self.sibling_rivalry = SiblingRivalry(events=0, rivals={}, last_rival=None, last_resource=None)
        self.parental_teaching = ParentalTeaching(lessons_received=0, teachers={}, skills={}, last_lesson=None, last_teacher=None)
        self.family_bonding = FamilyBonding(events=0, family_bonds=[])
        self.group = CatGroupMembership(group_id=None, member=False, joined_order=None, shared_scent=0.0, accepted_members=[], group_events=0, influence=0.0, defense_events=0, support_events=0, recruitment_support=0, recruitment_vetoes=0)
        self.culture = CatCulture(adopted_traditions={}, rejected_traditions={}, preferences={}, myths={}, innovations={}, exposures=0)
        self.group_roles = CatGroupRoles(active={}, history=[], role_events=0)
        self.human_bonds = {}
        self.meow_invitations = CatMeowInvitations(offered=0, understood=0, guided_to_bar=0, history=[], suspended_until_tick=0, suspension_reason=None, garfield_training_required=False, garfield_training=None)
        self.norms = CatNorms(violations=[], sanctions=[], warnings=0, trust_penalties=0.0)
        self.special_traits = []
        self.aroma = aroma
        self.social_interactions = []
        self.pet_count = 0
        self.meow_count = 0
        self.needs = CatNeeds(hunger=0.0, thirst=0.0, fatigue=0.0, safety=0.0, social=0.0, curiosity=0.0, dominant=None, tick=0)
        self.position = None
        self.location = None
        self.current_layer = 'quantum_layer'
        self.world_key = None
        self.suggested_intent = None
        self.navigation_target = None
        self.navigation_offer = None
        self.last_navigation_decision = None
        self.hunt_quota = 0
        self.overpopulation_response_available = False
        self.scent_search = None
        self.known_scent_follow = None
        self.scent_box_follow = None
        self.quantum_transfer = None
        self.quantum_exploration = None
        self.quantum_return = None
        self.box_exploration = None
        self.exploration_goal = None
        self.birth_day = None
        self.developmental_stage = None
        self.mother_name = None
        self.birth_profile = None
        self.rolled_birth_profile = None
        self.birth_canonical = None
        self.birth_genetics = None
        self.birth_trait_dice_mapping = None
        self.birth_percentile = None
        self.canonical_identity = None
        self.recipient = None
        self.distribution = None
        self.cat_d20 = None
        self.cat_d20_box = None
        self.type = 'cat'

    def _entity_name(self, entity):
        return getattr(entity, 'name', None)

    def accept_pet(self, by_entity):
        actor_name = self._entity_name(by_entity)
        self.pet_count += 1
        event = {'type': 'cat_pet', 'cat': self.name, 'by': actor_name, 'accepted': True, 'pet_number': self.pet_count}
        self.social_interactions.append(event)
        return event

    def meow_to(self, listener, topic=None):
        meow_knowledge = self.learning.get('meow_knowledge', {})
        if not meow_knowledge.get('can_speak', False):
            return {'type': 'cat_meow', 'cat': self.name, 'listener': self._entity_name(listener), 'spoken': False, 'reason': 'meow_not_learned'}
        known_contents = list(meow_knowledge.get('contains', []))
        if topic is not None and topic not in known_contents:
            return {'type': 'cat_meow', 'cat': self.name, 'listener': self._entity_name(listener), 'spoken': False, 'reason': 'unknown_meow_topic', 'topic': topic}
        self.meow_count += 1
        event = {'type': 'cat_meow', 'cat': self.name, 'listener': self._entity_name(listener), 'spoken': True, 'meow_number': self.meow_count, 'topic': topic, 'contains': [topic] if topic is not None else known_contents}
        self.social_interactions.append(event)
        return event
