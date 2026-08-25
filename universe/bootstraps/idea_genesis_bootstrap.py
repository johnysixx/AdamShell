class IdeaGenesisBootstrap:

    def __init__(
        self,
        universe,
        idea_universe,
        gods,
        idea_entities=None
    ):
        self.universe = universe
        self.idea_universe = idea_universe
        self.gods = gods
        self.idea_entities = idea_entities
        self.day0_phases = []

    def let_there_be_light(
        self
    ):
        nebula = (
            self.idea_universe
            .primordial_waters
        )

        nebula.light = True
        nebula.order_started = True

        nebula.state[
            "light"
        ] = True

        nebula.state[
            "order_started"
        ] = True

        self.idea_universe.events.append(
            {
                "kind": "genesis",
                "word": "let_there_be_light"
            }
        )

        return nebula

    def let_there_be_space(
        self
    ):
        waters = (
            self.idea_universe
            .primordial_waters
        )

        if not waters.light:
            raise RuntimeError(
                "Day 2 requires Day 1 light."
            )

        nebula = (
            self.idea_universe
            .primordial_waters
        )

        nebula.space = True
        nebula.can_expand = True

        nebula.state[
            "space"
        ] = True

        nebula.state[
            "can_expand"
        ] = True

        self.idea_universe.events.append(
            {
                "kind": "genesis",
                "word": "let_there_be_space"
            }
        )

        return nebula

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

        waters.state["seas"] = True
        waters.state["dry_land"] = True
        waters.state["vegetation"] = True

        self.idea_universe.events.append(
            {
                "kind": "genesis",
                "word": "let_there_be_land_and_vegetation"
            }
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

        self.idea_universe.heavenly_lights_created = True
        self.idea_universe.stellar_epoch_started = True

        self.idea_universe.events.append(
            {
                "kind": "genesis",
                "word": "let_there_be_heavenly_lights"
            }
        )

        return True

    def let_there_be_life_in_waters_and_sky(
        self
    ):
        if not self.idea_universe.heavenly_lights_created:
            raise RuntimeError(
                "Day 5 requires Day 4 completion."
            )

        self.idea_universe.aquatic_life_archetype = True
        self.idea_universe.flying_life_archetype = True

        self.idea_universe.events.append(
            {
                "kind": "genesis",
                "word": "let_there_be_life_in_waters_and_sky",
                "day": 5
            }
        )

        return {
            "day": 5,
            "aquatic_life_archetype": True,
            "flying_life_archetype": True
        }

    def let_there_be_land_life(
        self
    ):
        if not (
            self.idea_universe.aquatic_life_archetype
            and self.idea_universe.flying_life_archetype
        ):
            raise RuntimeError(
                "Day 6 requires Day 5 completion."
            )

        self.idea_universe.land_life_archetype = True

        self.idea_universe.events.append(
            {
                "kind": "genesis",
                "word": "let_there_be_land_life",
                "day": 6
            }
        )

        return {
            "day": 6,
            "created": "land_life_archetype"
        }

    def bring_forth_first_divine_generation(
        self,
        tiamat,
        apsu
    ):
        lahmu = self.gods.create_god(
            name="lahmu",
            role="first_divine_generation"
        )

        lahamu = self.gods.create_god(
            name="lahamu",
            role="first_divine_generation"
        )

        parents = [
            apsu["name"],
            tiamat["name"]
        ]

        lahmu["parents"] = list(
            parents
        )

        lahamu["parents"] = list(
            parents
        )

        self.idea_universe.add_entity(
            lahmu
        )

        self.idea_universe.add_entity(
            lahamu
        )

        self.idea_universe.events.append(
            {
                "kind": "divine_genealogy",
                "generation": 1,
                "parents": parents,
                "children": [
                    "lahmu",
                    "lahamu"
                ]
            }
        )

        return {
            "lahmu": lahmu,
            "lahamu": lahamu
        }

    def bring_forth_second_divine_generation(
        self,
        lahmu,
        lahamu
    ):
        anshar = self.gods.create_god(
            name="anshar",
            role="second_divine_generation"
        )

        kishar = self.gods.create_god(
            name="kishar",
            role="second_divine_generation"
        )

        parents = [
            lahmu["name"],
            lahamu["name"]
        ]

        anshar["parents"] = list(
            parents
        )

        kishar["parents"] = list(
            parents
        )

        self.idea_universe.add_entity(
            anshar
        )

        self.idea_universe.add_entity(
            kishar
        )

        self.idea_universe.events.append(
            {
                "kind": "divine_genealogy",
                "generation": 2,
                "parents": parents,
                "children": [
                    "anshar",
                    "kishar"
                ]
            }
        )

        return {
            "anshar": anshar,
            "kishar": kishar
        }

    def bring_forth_anu(
        self,
        anshar,
        kishar
    ):
        anu = self.gods.create_god(
            name="anu",
            role="third_divine_generation"
        )

        parents = [
            anshar["name"],
            kishar["name"]
        ]

        anu["parents"] = list(
            parents
        )

        self.idea_universe.add_entity(
            anu
        )

        self.idea_universe.events.append(
            {
                "kind": "divine_genealogy",
                "generation": 3,
                "parents": parents,
                "children": [
                    "anu"
                ]
            }
        )

        return anu

    def bring_forth_ea(
        self,
        anu
    ):
        ea = self.gods.create_god(
            name="ea",
            role="fourth_divine_generation"
        )

        ea["parents"] = [
            anu["name"]
        ]

        ea["epithets"] = [
            "nudimmud"
        ]

        self.idea_universe.add_entity(
            ea
        )

        self.idea_universe.events.append(
            {
                "kind": "divine_genealogy",
                "generation": 4,
                "parents": [
                    anu["name"]
                ],
                "children": [
                    "ea"
                ],
                "epithets": {
                    "ea": [
                        "nudimmud"
                    ]
                }
            }
        )

        return ea

    def bring_forth_damkina(
        self
    ):
        damkina = self.gods.create_god(
            name="damkina",
            role="mother_of_marduk"
        )

        self.idea_universe.add_entity(
            damkina
        )

        self.idea_universe.events.append(
            {
                "kind": "divine_genealogy",
                "generation": "pre_marduk",
                "children": [
                    "damkina"
                ]
            }
        )

        return damkina

    def manifest_marduk(
        self,
        god,
        ea,
        damkina
    ):
        marduk = self.gods.assume_mask(
            god=god,
            mask_name="marduk",
            role="divine_champion"
        )

        marduk["parents"] = [
            ea["name"],
            damkina["name"]
        ]

        marduk["mythology"] = (
            "mesopotamian"
        )

        marduk["manifestation_context"] = (
            "ea_and_damkina_lineage"
        )

        self.idea_universe.events.append(
            {
                "kind": "divine_manifestation",
                "mask": "marduk",
                "mask_of": god["name"],
                "parents": [
                    ea["name"],
                    damkina["name"]
                ]
            }
        )

        return marduk

    def grant_marduk_divine_authority(
        self,
        marduk
    ):
        marduk["divine_authority_granted"] = True
        marduk["title"] = "king_of_the_gods"

        entry = {
            "kind": "divine_authority",
            "mask": "marduk",
            "title": "king_of_the_gods"
        }

        self.idea_universe.events.append(
            entry
        )

        return entry

    def confront_tiamat(
        self,
        marduk,
        tiamat
    ):
        if not marduk.get(
            "divine_authority_granted",
            False
        ):
            raise RuntimeError(
                "Marduk requires divine authority before confronting Tiamat."
            )

        return {
            "event": "marduk_confronts_tiamat",
            "marduk": marduk,
            "tiamat": tiamat
        }

    def defeat_tiamat(
        self,
        marduk,
        tiamat
    ):
        if not marduk.get(
            "divine_authority_granted",
            False
        ):
            raise RuntimeError(
                "Marduk lacks authority to defeat Tiamat."
            )

        god = marduk[
            "mask_of"
        ]

        tiamat["state"] = (
            "defeated"
        )

        entry = {
            "event": "tiamat_defeated",
            "actor_mask": "marduk",
            "actor": god,
            "target": tiamat
        }

        self.idea_universe.events.append(
            {
                "kind": "divine_conflict",
                "event": "tiamat_defeated",
                "actor_mask": "marduk",
                "actor": god["name"],
                "target": tiamat["name"]
            }
        )

        return entry

    def order_cosmos_from_tiamat(
        self,
        marduk,
        tiamat
    ):
        if tiamat.get("state") != "defeated":
            raise RuntimeError(
                "Tiamat must be defeated before the cosmos can be ordered."
            )

        if not marduk.get(
            "divine_authority_granted",
            False
        ):
            raise RuntimeError(
                "Marduk requires divine authority to order the cosmos."
            )

        self.idea_universe.heaven_ordered = True
        self.idea_universe.celestial_stations_established = True

        entry = {
            "event": "cosmos_ordered_from_tiamat",
            "actor_mask": "marduk",
            "actor": marduk["mask_of"],
            "source": tiamat
        }

        self.idea_universe.events.append(
            {
                "kind": "cosmic_order",
                "event": "cosmos_ordered_from_tiamat",
                "actor_mask": "marduk",
                "source": tiamat["name"]
            }
        )

        return entry

    def record_cosmic_order_witnesses(
        self,
        genesis_view,
        mesopotamian_view
    ):
        event = {
            "event": "cosmic_order_established",
            "witnesses": {
                "genesis": {
                    "event": "heavenly_lights_created",
                    "record": genesis_view
                },
                "mesopotamian": {
                    "event": "cosmos_ordered_from_tiamat",
                    "record": mesopotamian_view
                }
            }
        }

        self.idea_universe.events.append(
            {
                "kind": "canonical_event",
                "event": "cosmic_order_established",
                "witnesses": [
                    "genesis",
                    "mesopotamian"
                ]
            }
        )

        return event

    def establish_divine_order(
        self,
        marduk,
        gods
    ):
        if not self.idea_universe.heaven_ordered:
            raise RuntimeError(
                "Cosmic order must be established first."
            )

        if not marduk.get(
            "divine_authority_granted",
            False
        ):
            raise RuntimeError(
                "Marduk requires divine authority."
            )

        assignments = {}

        role_map = {
            "anu": "heavens",
            "ea": "wisdom_and_deep",
            "damkina": "divine_motherhood",
            "lahmu": "primordial_generation",
            "lahamu": "primordial_generation",
            "anshar": "upper_cosmic_boundary",
            "kishar": "lower_cosmic_boundary"
        }

        for god in gods:
            name = god.get("name")

            assignment = role_map.get(
                name,
                "unassigned_divine_function"
            )

            god["divine_function"] = assignment
            assignments[name] = assignment

        self.idea_universe.divine_order_established = True

        entry = {
            "event": "divine_order_established",
            "actor_mask": "marduk",
            "actor": marduk["mask_of"],
            "assignments": assignments
        }

        self.idea_universe.events.append(
            {
                "kind": "divine_order",
                "event": "divine_order_established",
                "actor_mask": "marduk",
                "assignments": dict(assignments)
            }
        )

        return entry

    def run(self):
        self.day0_phases.append(
            "day0_started"
        )

        god = self.gods.create_god(
            name="god",
            role="creator_entity"
        )

        tiamat = self.gods.create_god(
            name="tiamat",
            role="primordial_mother"
        )

        apsu = self.gods.create_god(
            name="apsu",
            role="primordial_father"
        )

        self.day0_phases.append(
            "primordial_parents_created"
        )

        tiamat["primordial_aspect"] = (
            "salt_water"
        )

        apsu["primordial_aspect"] = (
            "fresh_water"
        )

        nebula = (
            self.idea_universe
            .primordial_waters
        )

        nebula.waters = True
        nebula.deep = True
        nebula.chaos = True
        nebula.ordered = False

        nebula.state["waters"] = True
        nebula.state["deep"] = True
        nebula.state["chaos"] = True
        nebula.state["ordered"] = False

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
                    existence_pct=100.0
                )
            )

            self.idea_universe.add_entity(
                serpent
            )

            self.day0_phases.append(
                "serpent_created"
            )


        return {
            "god": god,
            "tiamat": tiamat,
            "apsu": apsu,
            "serpent": serpent
        }









