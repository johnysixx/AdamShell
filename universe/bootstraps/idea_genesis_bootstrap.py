from idea_universe.idea_genesis_runtime_state import (
    IdeaCanonicalCosmicOrderEvent,
    IdeaCosmicOrderEvent,
    IdeaDivineAuthorityEvent,
    IdeaDivineConflictEvent,
    IdeaDivineConfrontationResult,
    IdeaDivineFunctionAssignment,
    IdeaDivineGenealogyEvent,
    IdeaDivineManifestationEvent,
    IdeaDivineOrderEvent,
    IdeaFirstDivineGenerationResult,
    IdeaGenesisBootstrapResult,
    IdeaGenesisLifeEvent,
    IdeaGenesisWordEvent,
    IdeaSecondDivineGenerationResult,
)


class IdeaGenesisBootstrap:

    def __init__(
        self,
        universe,
        idea_universe,
        gods,
        idea_entities=None,
    ):
        self.universe = universe
        self.idea_universe = idea_universe
        self.gods = gods
        self.idea_entities = idea_entities
        self.day0_phases = []

    def _record(
        self,
        event,
    ):
        self.idea_universe.events.append(
            event
        )

        return event

    def let_there_be_light(self):
        nebula = (
            self.idea_universe
            .primordial_waters
        )

        nebula.light = True
        nebula.order_started = True

        self._record(
            IdeaGenesisWordEvent(
                word="let_there_be_light",
            )
        )

        return nebula

    def let_there_be_space(self):
        waters = (
            self.idea_universe
            .primordial_waters
        )

        if not waters.light:
            raise RuntimeError(
                "Day 2 requires Day 1 light."
            )

        waters.space = True
        waters.can_expand = True

        self._record(
            IdeaGenesisWordEvent(
                word="let_there_be_space",
            )
        )

        return waters

    def let_there_be_land_and_vegetation(
        self
    ):
        waters = (
            self.idea_universe
            .primordial_waters
        )

        if not waters.space:
            raise RuntimeError(
                "Day 3 requires space."
            )

        waters.seas = True
        waters.dry_land = True
        waters.vegetation = True

        self._record(
            IdeaGenesisWordEvent(
                word=(
                    "let_there_be_land_and_"
                    "vegetation"
                ),
            )
        )

        return waters

    def let_there_be_heavenly_lights(
        self
    ):
        waters = (
            self.idea_universe
            .primordial_waters
        )

        if not waters.vegetation:
            raise RuntimeError(
                "Day 4 requires Day 3 completion."
            )

        self.idea_universe.heavenly_lights_created = (
            True
        )

        self.idea_universe.stellar_epoch_started = (
            True
        )

        return self._record(
            IdeaGenesisWordEvent(
                word=(
                    "let_there_be_heavenly_"
                    "lights"
                ),
                day=4,
            )
        )

    def let_there_be_life_in_waters_and_sky(
        self
    ):
        if not (
            self.idea_universe
            .heavenly_lights_created
        ):
            raise RuntimeError(
                "Day 5 requires Day 4 completion."
            )

        self.idea_universe.aquatic_life_archetype = (
            True
        )

        self.idea_universe.flying_life_archetype = (
            True
        )

        return self._record(
            IdeaGenesisLifeEvent(
                word=(
                    "let_there_be_life_in_"
                    "waters_and_sky"
                ),
                day=5,
                aquatic_life_archetype=True,
                flying_life_archetype=True,
            )
        )

    def let_there_be_land_life(self):
        if not (
            self.idea_universe
            .aquatic_life_archetype
            and self.idea_universe
            .flying_life_archetype
        ):
            raise RuntimeError(
                "Day 6 requires Day 5 completion."
            )

        self.idea_universe.land_life_archetype = (
            True
        )

        return self._record(
            IdeaGenesisLifeEvent(
                word="let_there_be_land_life",
                day=6,
                created=(
                    "land_life_archetype"
                ),
            )
        )

    def bring_forth_first_divine_generation(
        self,
        tiamat,
        apsu,
    ):
        lahmu = self.gods.create_god(
            name="lahmu",
            role="first_divine_generation",
        )

        lahamu = self.gods.create_god(
            name="lahamu",
            role="first_divine_generation",
        )

        parents = (
            apsu.name,
            tiamat.name,
        )

        lahmu.parents = list(
            parents
        )

        lahamu.parents = list(
            parents
        )

        self.idea_universe.add_entity(
            lahmu
        )

        self.idea_universe.add_entity(
            lahamu
        )

        self._record(
            IdeaDivineGenealogyEvent(
                generation=1,
                parents=parents,
                children=(
                    "lahmu",
                    "lahamu",
                ),
            )
        )

        return (
            IdeaFirstDivineGenerationResult(
                lahmu=lahmu,
                lahamu=lahamu,
            )
        )

    def bring_forth_second_divine_generation(
        self,
        lahmu,
        lahamu,
    ):
        anshar = self.gods.create_god(
            name="anshar",
            role="second_divine_generation",
        )

        kishar = self.gods.create_god(
            name="kishar",
            role="second_divine_generation",
        )

        parents = (
            lahmu.name,
            lahamu.name,
        )

        anshar.parents = list(
            parents
        )

        kishar.parents = list(
            parents
        )

        self.idea_universe.add_entity(
            anshar
        )

        self.idea_universe.add_entity(
            kishar
        )

        self._record(
            IdeaDivineGenealogyEvent(
                generation=2,
                parents=parents,
                children=(
                    "anshar",
                    "kishar",
                ),
            )
        )

        return (
            IdeaSecondDivineGenerationResult(
                anshar=anshar,
                kishar=kishar,
            )
        )

    def bring_forth_anu(
        self,
        anshar,
        kishar,
    ):
        anu = self.gods.create_god(
            name="anu",
            role="third_divine_generation",
        )

        parents = (
            anshar.name,
            kishar.name,
        )

        anu.parents = list(
            parents
        )

        self.idea_universe.add_entity(
            anu
        )

        self._record(
            IdeaDivineGenealogyEvent(
                generation=3,
                parents=parents,
                children=("anu",),
            )
        )

        return anu

    def bring_forth_ea(
        self,
        anu,
    ):
        ea = self.gods.create_god(
            name="ea",
            role="fourth_divine_generation",
        )

        ea.parents = [
            anu.name
        ]

        ea.epithets = [
            "nudimmud"
        ]

        self.idea_universe.add_entity(
            ea
        )

        self._record(
            IdeaDivineGenealogyEvent(
                generation=4,
                parents=(
                    anu.name,
                ),
                children=("ea",),
                epithets=(
                    "nudimmud",
                ),
            )
        )

        return ea

    def bring_forth_damkina(self):
        damkina = self.gods.create_god(
            name="damkina",
            role="mother_of_marduk",
        )

        self.idea_universe.add_entity(
            damkina
        )

        self._record(
            IdeaDivineGenealogyEvent(
                generation="pre_marduk",
                parents=(),
                children=("damkina",),
            )
        )

        return damkina

    def manifest_marduk(
        self,
        god,
        ea,
        damkina,
    ):
        marduk = self.gods.assume_mask(
            god=god,
            mask_name="marduk",
            role="divine_champion",
        )

        marduk.parents = [
            ea.name,
            damkina.name,
        ]

        marduk.mythology = (
            "mesopotamian"
        )

        marduk.manifestation_context = (
            "ea_and_damkina_lineage"
        )

        self._record(
            IdeaDivineManifestationEvent(
                mask="marduk",
                mask_of=god.name,
                parents=(
                    ea.name,
                    damkina.name,
                ),
            )
        )

        return marduk

    def grant_marduk_divine_authority(
        self,
        marduk,
    ):
        marduk.divine_authority_granted = (
            True
        )

        marduk.title = (
            "king_of_the_gods"
        )

        return self._record(
            IdeaDivineAuthorityEvent(
                mask="marduk",
                title="king_of_the_gods",
            )
        )

    def confront_tiamat(
        self,
        marduk,
        tiamat,
    ):
        if not getattr(
            marduk,
            "divine_authority_granted",
            False,
        ):
            raise RuntimeError(
                "Marduk requires divine "
                "authority before confronting "
                "Tiamat."
            )

        return (
            IdeaDivineConfrontationResult(
                marduk=marduk,
                tiamat=tiamat,
            )
        )

    def defeat_tiamat(
        self,
        marduk,
        tiamat,
    ):
        if not getattr(
            marduk,
            "divine_authority_granted",
            False,
        ):
            raise RuntimeError(
                "Marduk lacks authority "
                "to defeat Tiamat."
            )

        god = marduk.mask_of

        tiamat.state = "defeated"

        return self._record(
            IdeaDivineConflictEvent(
                actor_mask="marduk",
                actor=god,
                target=tiamat,
            )
        )

    def order_cosmos_from_tiamat(
        self,
        marduk,
        tiamat,
    ):
        if getattr(
            tiamat,
            "state",
            None,
        ) != "defeated":
            raise RuntimeError(
                "Tiamat must be defeated "
                "before the cosmos can be "
                "ordered."
            )

        if not getattr(
            marduk,
            "divine_authority_granted",
            False,
        ):
            raise RuntimeError(
                "Marduk requires divine "
                "authority to order the cosmos."
            )

        self.idea_universe.heaven_ordered = (
            True
        )

        self.idea_universe.celestial_stations_established = (
            True
        )

        return self._record(
            IdeaCosmicOrderEvent(
                actor_mask="marduk",
                actor=marduk.mask_of,
                source=tiamat,
            )
        )

    def record_cosmic_order_witnesses(
        self,
        genesis_view,
        mesopotamian_view,
    ):
        return self._record(
            IdeaCanonicalCosmicOrderEvent(
                genesis_record=(
                    genesis_view
                ),
                mesopotamian_record=(
                    mesopotamian_view
                ),
            )
        )

    def establish_divine_order(
        self,
        marduk,
        gods,
    ):
        if not (
            self.idea_universe
            .heaven_ordered
        ):
            raise RuntimeError(
                "Cosmic order must be "
                "established first."
            )

        if not getattr(
            marduk,
            "divine_authority_granted",
            False,
        ):
            raise RuntimeError(
                "Marduk requires divine "
                "authority."
            )

        role_map = {
            "anu": "heavens",
            "ea": "wisdom_and_deep",
            "damkina": "divine_motherhood",
            "lahmu": "primordial_generation",
            "lahamu": "primordial_generation",
            "anshar": "upper_cosmic_boundary",
            "kishar": "lower_cosmic_boundary",
        }

        assignments = []

        for god in gods:
            name = getattr(
                god,
                "name",
                None,
            )

            function = role_map.get(
                name,
                "unassigned_divine_function",
            )

            god.divine_function = (
                function
            )

            assignments.append(
                IdeaDivineFunctionAssignment(
                    god_name=name,
                    function=function,
                )
            )

        self.idea_universe.divine_order_established = (
            True
        )

        return self._record(
            IdeaDivineOrderEvent(
                actor_mask="marduk",
                actor=marduk.mask_of,
                assignments=tuple(
                    assignments
                ),
            )
        )

    def run(self):
        self.day0_phases.append(
            "day0_started"
        )

        god = self.gods.create_god(
            name="god",
            role="creator_entity",
        )

        tiamat = self.gods.create_god(
            name="tiamat",
            role="primordial_mother",
        )

        apsu = self.gods.create_god(
            name="apsu",
            role="primordial_father",
        )

        self.day0_phases.append(
            "primordial_parents_created"
        )

        tiamat.primordial_aspect = (
            "salt_water"
        )

        apsu.primordial_aspect = (
            "fresh_water"
        )

        waters = (
            self.idea_universe
            .primordial_waters
        )

        waters.waters = True
        waters.deep = True
        waters.chaos = True
        waters.ordered = False

        self.idea_universe.add_entity(
            tiamat
        )

        self.idea_universe.add_entity(
            apsu
        )

        serpent = None

        if self.idea_entities is not None:
            serpent = (
                self.idea_entities
                .create_idea_entity(
                    name="serpent",
                    role="primordial_serpent",
                    active=True,
                    existence_pct=100.0,
                )
            )

            self.idea_universe.add_entity(
                serpent
            )

            self.day0_phases.append(
                "serpent_created"
            )

        return IdeaGenesisBootstrapResult(
            god=god,
            tiamat=tiamat,
            apsu=apsu,
            serpent=serpent,
        )
