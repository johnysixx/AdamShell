class ConflictEngine:

    def resolve(self, effects):

        result = {}
        conflicts = []

        for effect in effects:
            if not effect:
                continue

            for k, v in effect.items():

                if k in result and result[k] != v:
                    conflicts.append({
                        "key": k,
                        "old": result[k],
                        "new": v,
                        "strength": 1  # základní energie konfliktu
                    })

                result[k] = v

        return result, conflicts