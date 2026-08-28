class QuantumDirector:

    def __init__(self, universe, god, gods):
        self.universe = universe
        self.god = god
        self.gods = gods
        self.mask = self.gods.assume_mask(god=self.god, mask_name='director', role='quantum_director')
        self.name = 'director'
        self.type = 'god_mask'
        self.layer = 'quantum_layer'
        self.zone = 'stable_zone'
        self.research_book = self.god.research_book
        self.knowledge = self.god.knowledge
        self.corporation_state = 'one_person_operation'

    def observe(self, observation):
        entry = dict(observation)
        self.research_book.append(entry)
        return entry

    def study_nebula(self, nebula):
        amount = nebula.elemental_potentials.get('liquid_hydrocarbons', 0.0)
        if amount <= 0.0:
            finding = 'no_liquid_hydrocarbons_identified'
        else:
            finding = 'liquid_hydrocarbons_identified'
            self.knowledge.add(finding)
        entry = {'event': 'primordial_nebula_studied', 'subject': nebula, 'finding': finding, 'amount': amount}
        self.observe(entry)
        return entry

    def invent_mining_method(self, nebula):
        if 'liquid_hydrocarbons_identified' not in self.knowledge:
            raise RuntimeError('Liquid hydrocarbons must be identified first.')
        invention = 'liquid_hydrocarbon_mining'
        self.knowledge.add(invention)
        entry = {'event': 'mining_method_invented', 'subject': nebula, 'invention': invention, 'mining_limit_rule': 'maximum_10_percent_of_growth'}
        self.observe(entry)
        return entry

    def mine_nebula(self, nebula, amount):
        if 'liquid_hydrocarbon_mining' not in self.knowledge:
            raise RuntimeError('Mining method has not been invented.')
        mined = nebula.mine_liquid_hydrocarbons(amount)
        entry = {'event': 'primordial_nebula_mined', 'subject': nebula, 'material': 'liquid_hydrocarbons', 'mined': mined, 'miner': self.name}
        self.observe(entry)
        return entry

    def arrive_at_bar(self, meeting_place, sample):
        if self not in meeting_place.entities:
            meeting_place.entities.append(self)
        present_serpent = next(
            (
                entity
                for entity
                in meeting_place.entities
                if getattr(
                    entity,
                    "name",
                    None
                ) == "serpent"
            ),
            None
        )
        taught_cocktail = None
        if sample.get('material') == 'liquid_hydrocarbons' and float(sample.get('amount', 0.0)) > 0.0:
            book = meeting_place.how_to_mix_drinks
            was_hidden = 'raspberry_rum' in book.hidden_recipes
            recipe = book.reveal_hidden_recipe(name='raspberry_rum', teacher='god')
            if was_hidden:
                meeting_place.bartender.learn_cocktail(drink='raspberry_rum', teacher='god', ingredients=list(recipe['ingredients'].keys()))
                taught_cocktail = 'raspberry_rum'
            meeting_place.refresh_basic_drinks()
        entry = {'event': 'director_arrived_at_bar', 'sample': dict(sample), 'serpent_present': present_serpent is not None, 'met': present_serpent, 'taught_cocktail': taught_cocktail}
        self.observe(entry)
        return entry

    def observe_star_explosion(self, star, remnant):
        return self.observe({'event': 'primordial_idea_star_exploded', 'subject': star, 'remnant': remnant})

    def observe_nebula_birth(self, nebula):
        return self.observe({'event': 'primordial_nebula_created', 'subject': nebula})
