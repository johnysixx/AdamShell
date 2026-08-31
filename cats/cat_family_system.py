from cats.cat import Cat

class CatFamilySystem:

    def __init__(self, cats_layer=None):
        self.cats_layer = cats_layer

    def register_birth(self, mother, kittens, cats=None):
        self._require_cat(mother)
        cats = list(cats) if cats is not None else list(getattr(self.cats_layer, 'cats', []))
        by_name = {cat.name: cat for cat in cats if isinstance(cat, Cat)}
        by_name[mother.name] = mother
        for kitten in kittens:
            self._require_cat(kitten)
            father_name = getattr(kitten, 'father_name', None)
            self._set_parents(kitten=kitten, mother=mother.name, father=father_name)
            self._add_unique(mother.family.children, kitten.name)
            father = by_name.get(father_name)
            if father is not None:
                self._add_unique(father.family.children, kitten.name)
        self._link_littermates(kittens)
        return {'name': 'cat_family_registered', 'mother': mother.name, 'kittens': [kitten.name for kitten in kittens], 'registered': True}

    def relation(self, cat, other_cat):
        self._require_cat(cat)
        self._require_cat(other_cat)
        if other_cat.name in cat.family.children:
            return 'child'
        parents = cat.family.parents
        if parents.get('mother') == other_cat.name:
            return 'mother'
        if parents.get('father') == other_cat.name:
            return 'father'
        if other_cat.name in cat.family.littermates:
            if other_cat.name in cat.family.half_siblings:
                return 'half_sibling_littermate'
            return 'sibling_littermate'
        if other_cat.name in cat.family.half_siblings:
            return 'half_sibling'
        if other_cat.name in cat.family.siblings:
            return 'sibling'
        return None

    def are_related(self, cat, other_cat):
        return self.relation(cat, other_cat) is not None

    def _set_parents(self, kitten, mother, father):
        kitten.family.parents['mother'] = mother
        kitten.family.parents['father'] = father

    def _link_littermates(self, kittens):
        for index, first in enumerate(kittens):
            for second in kittens[index + 1:]:
                self._link_siblings(first, second)
                self._add_unique(first.family.littermates, second.name)
                self._add_unique(second.family.littermates, first.name)

    def _link_siblings(self, first, second):
        first_parents = first.family.parents
        second_parents = second.family.parents
        same_mother = first_parents.get('mother') is not None and first_parents.get('mother') == second_parents.get('mother')
        same_father = first_parents.get('father') is not None and first_parents.get('father') == second_parents.get('father')
        if same_mother and same_father:
            self._add_unique(first.family.siblings, second.name)
            self._add_unique(second.family.siblings, first.name)
            return
        if same_mother or same_father:
            self._add_unique(first.family.half_siblings, second.name)
            self._add_unique(second.family.half_siblings, first.name)

    def _add_unique(self, values, value):
        if value is not None and value not in values:
            values.append(value)

    def _require_cat(self, cat):
        if not isinstance(cat, Cat):
            raise TypeError('CatFamilySystem requires Cat.')
