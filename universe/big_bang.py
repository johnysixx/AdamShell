class BigBang:

    def __init__(self, universe):
        self.universe = universe
        self.name = "big_bang"
        self.type = "cosmic_origin_process"
        self.state = "ready"

        self.phases = []

        self.primordial_elements = {}

        self.cosmic_state = {
            "spacetime_expanded": False,
            "primordial_plasma_formed": False,
            "light_nuclei_conditions_prepared": False,
            "light_separated_from_darkness": False,
            "darkness_present": True
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "phases": self.phases,
            "primordial_elements": self.primordial_elements,
            "cosmic_state": self.cosmic_state
        }

    def explode(self):
        return self.run_process()

    def run_process(self):
        self.begin()
        self.expand_spacetime()
        self.form_primordial_plasma()
        self.form_light_elements()
        self.separate_light_from_darkness()
        self.complete()
        self.write_to_world()

        return self.public_state

    def begin(self):
        self.state = "in_progress"
        self.public_state["state"] = self.state

        self.record_phase(
            name="primordial_void",
            description="Before form, stars, worlds, or drink foundations, the universe begins as primordial potential."
        )

        print("💥 BIG BANG PROCESS STARTED")

    def expand_spacetime(self):
        self.cosmic_state["spacetime_expanded"] = True

        self.record_phase(
            name="spacetime_expansion",
            description="Space and time begin expanding from the primordial origin."
        )

        print("SPACETIME BEGINS TO EXPAND")

    def form_primordial_plasma(self):
        self.cosmic_state["primordial_plasma_formed"] = True

        self.primordial_elements["energy"] = {
            "name": "energy",
            "type": "primordial_force",
            "state": "released"
        }

        self.primordial_elements["matter"] = {
            "name": "matter",
            "type": "primordial_substance",
            "state": "forming"
        }

        self.record_phase(
            name="primordial_plasma",
            description="Energy and early matter exist as a hot primordial plasma."
        )

        print("PRIMORDIAL PLASMA FORMED")

    def form_light_elements(self):
        self.cosmic_state["light_nuclei_conditions_prepared"] = True

        self.primordial_elements["hydrogen"] = {
            "name": "hydrogen",
            "type": "element",
            "state": "formed",
            "origin": "big_bang_nucleosynthesis"
        }

        self.primordial_elements["helium"] = {
            "name": "helium",
            "type": "element",
            "state": "formed",
            "origin": "big_bang_nucleosynthesis"
        }

        self.primordial_elements["trace_lithium"] = {
            "name": "trace_lithium",
            "type": "element",
            "state": "trace",
            "origin": "big_bang_nucleosynthesis"
        }

        self.record_phase(
            name="light_nuclei_conditions_prepared",
            description="Conditions for light nuclei formation are prepared in the early universe."
        )

        print("LIGHT NUCLEI CONDITIONS PREPARED")

    def separate_light_from_darkness(self):
        self.cosmic_state["light_separated_from_darkness"] = True

        self.record_phase(
            name="light_separated_from_darkness",
            description="Light becomes distinct from darkness. The Big Bang process reaches completion."
        )

        print("LIGHT SEPARATED FROM DARKNESS")

    def complete(self):
        self.state = "completed"
        self.public_state["state"] = self.state

        self.record_phase(
            name="big_bang_completed",
            description="The origin process is complete. The universe now contains spacetime, primordial plasma, and light elements."
        )

        print("BIG BANG PROCESS COMPLETED")

    def record_phase(self, name, description):
        phase = {
            "name": name,
            "description": description
        }

        self.phases.append(phase)

    def write_to_world(self):
        self.universe.world["big_bang"] = self.public_state
        self.universe.world["cosmic_history"] = self.phases
        self.universe.world["primordial_elements"] = self.primordial_elements
        self.universe.world["cosmic_state"] = self.cosmic_state
