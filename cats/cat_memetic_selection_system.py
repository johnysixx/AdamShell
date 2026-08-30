from copy import deepcopy

class CatMemeticSelectionSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def expose_myth(self, group_id, cats, myth_id):
        group = self.group_system._group(group_id)
        myth = group.myths.get(myth_id)
        if myth is None:
            return {'name': 'cat_meme_exposure_denied', 'reason': 'unknown_myth', 'exposed': False}
        adopted = []
        rejected = []
        for cat in self.group_system._member_objects(group, cats):
            score = self._myth_score(cat, myth)
            cat.culture['exposures'] += 1
            if score >= 0.45:
                cat.culture['myths'][myth_id] = {'score': score, 'group_id': group_id}
                adopted.append(cat.name)
            else:
                rejected.append(cat.name)
        fitness = self._fitness(exposures=len(adopted) + len(rejected), adoptions=len(adopted), retellings=int(getattr(myth, 'retellings', 0)), credibility=float(getattr(myth, 'credibility', 0.0)))
        myth.memetic_fitness = fitness
        myth.adoption_count = int(getattr(myth, 'adoption_count', 0)) + len(adopted)
        myth.rejection_count = int(getattr(myth, 'rejection_count', 0)) + len(rejected)
        return {'name': 'cat_myth_memetic_exposure', 'group_id': group_id, 'myth_id': myth_id, 'adopted': adopted, 'rejected': rejected, 'fitness': fitness, 'exposed': True}

    def expose_innovation(self, group_id, cats, innovation_id):
        group = self.group_system._group(group_id)
        innovation = group.innovations.get(innovation_id)
        if innovation is None:
            return {'name': 'cat_meme_exposure_denied', 'reason': 'unknown_innovation', 'exposed': False}
        adopted = []
        rejected = []
        for cat in self.group_system._member_objects(group, cats):
            intellect = self._number(cat.intellect.get('normalized', 0.5))
            curiosity = self._number(cat.personality.get('traits', {}).get('curiosity', 0.5))
            confidence = self._number(getattr(innovation, 'confidence', 0.0))
            verified_bonus = 0.15 if getattr(innovation, 'verified', False) else 0.0
            score = intellect * 0.35 + curiosity * 0.25 + confidence * 0.3 + verified_bonus + 0.1
            if score >= 0.5:
                cat.culture['innovations'][innovation_id] = {'score': round(score, 4), 'group_id': group_id}
                adopted.append(cat.name)
            else:
                rejected.append(cat.name)
        fitness = self._fitness(exposures=len(adopted) + len(rejected), adoptions=len(adopted), retellings=0, credibility=float(getattr(innovation, 'confidence', 0.0)))
        innovation.memetic_fitness = fitness
        innovation.adoption_count = int(getattr(innovation, 'adoption_count', 0)) + len(adopted)
        innovation.rejection_count = int(getattr(innovation, 'rejection_count', 0)) + len(rejected)
        return {'name': 'cat_innovation_memetic_exposure', 'group_id': group_id, 'innovation_id': innovation_id, 'adopted': adopted, 'rejected': rejected, 'fitness': fitness, 'exposed': True}

    def select_myths(self, group_id, minimum_fitness=0.2):
        group = self.group_system._group(group_id)
        surviving = []
        fading = []
        for myth_id, myth in group.myths.items():
            fitness = self._number(getattr(myth, 'memetic_fitness', 0.0))
            if fitness >= minimum_fitness:
                surviving.append(myth_id)
            else:
                fading.append(myth_id)
        return {'group_id': group_id, 'surviving': surviving, 'fading': fading}

    def select_innovations(self, group_id, minimum_fitness=0.2):
        group = self.group_system._group(group_id)
        surviving = []
        fading = []
        for innovation_id, innovation in group.innovations.items():
            fitness = self._number(getattr(innovation, 'memetic_fitness', 0.0))
            if fitness >= minimum_fitness:
                surviving.append(innovation_id)
            else:
                fading.append(innovation_id)
        return {'group_id': group_id, 'surviving': surviving, 'fading': fading}

    def _myth_score(self, cat, myth):
        curiosity = self._number(cat.personality.get('traits', {}).get('curiosity', 0.5))
        sociability = self._number(cat.personality.get('traits', {}).get('sociability', 0.5))
        credibility = self._number(getattr(myth, 'credibility', 0.0))
        return curiosity * 0.25 + sociability * 0.2 + credibility * 0.45 + 0.1

    def _fitness(self, exposures, adoptions, retellings, credibility):
        adoption_rate = adoptions / exposures if exposures else 0.0
        retelling_bonus = min(0.25, retellings * 0.04)
        fitness = adoption_rate * 0.55 + float(credibility) * 0.3 + retelling_bonus
        return round(max(0.0, min(1.0, fitness)), 4)

    def _number(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
