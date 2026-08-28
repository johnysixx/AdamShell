from cats.genotype import CatGenotype
from cats.phenotype_resolver import CatPhenotypeResolver
from cats.kitten_viability_resolver import KittenGeneticViabilityResolver

class KittenEmbryoResolver:

    def __init__(self, universe):
        self.universe = universe
        self.history = []
        self.embryo_count = 0

    def create_embryo(self, mother, father, rng, genotype_override=None):
        self._validate_parents(mother, father)
        self.embryo_count += 1
        embryo_id = f'embryo_{self.embryo_count:04d}'
        genotype = genotype_override if genotype_override is not None else CatGenotype.inherit(mother_genotype=mother.genotype, father_genotype=father.genotype, rng=rng)
        viability = KittenGeneticViabilityResolver.resolve(genotype)
        if not viability['viable']:
            cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError(f'Nonviable kitten genotype replaced embryo {embryo_id}.'), source_component='kitten_embryo_resolver', source_operation='nonviable_embryo')
            event = {'name': 'nonviable_kitten_embryo_replaced_by_cronenberg', 'embryo_id': embryo_id, 'mother': mother.name, 'father': father.name, 'genotype': genotype, 'viability': viability, 'kitten_created': False, 'cronenberg_created': True, 'cronenberg_id': cronenberg.id}
            self.history.append(event)
            self.universe.quantum_events.append(event)
            return {'embryo': None, 'viability': viability, 'cronenberg': cronenberg, 'event': event, 'viable': False}
        phenotype = CatPhenotypeResolver.resolve(genotype)
        embryo = {'id': embryo_id, 'type': 'kitten_embryo', 'state': 'gestating', 'mother_name': mother.name, 'father_name': father.name, 'genotype': genotype, 'phenotype': phenotype, 'profile': dict(phenotype['profile']), 'viability': viability, 'genetic_status': viability['status'], 'rare': viability['rare'], 'special_traits': list(viability['special_traits'])}
        event = {'name': 'kitten_embryo_created', 'embryo_id': embryo_id, 'mother': mother.name, 'father': father.name, 'genetic_status': viability['status'], 'rare': viability['rare'], 'profile': dict(phenotype['profile']), 'kitten_created': False, 'cronenberg_created': False}
        self.history.append(event)
        return {'embryo': embryo, 'viability': viability, 'phenotype': phenotype, 'cronenberg': None, 'event': event, 'viable': True}

    @staticmethod
    def _validate_parents(mother, father):
        if getattr(mother, 'sex', None) != 'female':
            raise ValueError('Embryo mother must be female.')
        if getattr(father, 'sex', None) != 'male':
            raise ValueError('Embryo father must be male.')
        if not hasattr(mother, 'genotype'):
            raise ValueError('Mother has no genotype.')
        if not hasattr(father, 'genotype'):
            raise ValueError('Father has no genotype.')
