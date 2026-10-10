from cats.cat import Cat
from copy import deepcopy
from core.entity.components import SpatialVector3, require_spatial_vector

from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)
from cats.cat_olfaction_state import (
    CatAromaMatch,
    CatAromaRecognition,
)
from cats.cat_knowledge_objects import (
    CatKnownAroma,
    CatKnownPlace,
    CatKnownPrinciples,
    CatKnowledgeState,
    CatScentPlaceMemory,
)
from cats.cat_legend_knowledge_system import (
    CatLegendKnowledgeSystem,
)

class CatKnowledge:

    LEGEND_SYSTEM = (
        CatLegendKnowledgeSystem
    )

    @classmethod
    def ensure_cat_knowledge(
        cls,
        cat,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            raise TypeError(
                'CatKnowledge requires Cat.'
            )

        if not isinstance(
            cat.knowledge,
            CatKnowledgeState,
        ):
            raise TypeError(
                'Cat knowledge must be '
                'CatKnowledgeState.'
            )

        return cat.knowledge


    @classmethod
    def ensure_universe_legends(
        cls,
        universe,
    ):
        return (
            cls.LEGEND_SYSTEM
            .ensure_universe_legends(
                universe
            )
        )

    @classmethod
    def publish_legend(
        cls,
        universe,
        cat,
        place,
        claim_type='place_discovered',
    ):
        return (
            cls.LEGEND_SYSTEM
            .publish_legend(
                universe=universe,
                cat=cat,
                place=place,
                claim_type=claim_type,
            )
        )

    @classmethod
    def hear_legend(
        cls,
        listener,
        storyteller,
        legend,
    ):
        return (
            cls.LEGEND_SYSTEM
            .hear_legend(
                listener=listener,
                storyteller=storyteller,
                legend=legend,
            )
        )

    @classmethod
    def verify_heard_legend(
        cls,
        cat,
        place,
    ):
        return (
            cls.LEGEND_SYSTEM
            .verify_heard_legend(
                cat=cat,
                place=place,
            )
        )

    @classmethod
    def choose_legend_to_share(
        cls,
        storyteller,
        listener,
        universe,
    ):
        return (
            cls.LEGEND_SYSTEM
            .choose_legend_to_share(
                storyteller=storyteller,
                listener=listener,
                universe=universe,
            )
        )

    @classmethod
    def evaluate_legend_sharing(
        cls,
        storyteller,
        listener,
        legend,
    ):
        return (
            cls.LEGEND_SYSTEM
            .evaluate_legend_sharing(
                storyteller=storyteller,
                listener=listener,
                legend=legend,
            )
        )

    @classmethod
    def share_legend(
        cls,
        storyteller,
        listener,
        universe,
    ):
        return (
            cls.LEGEND_SYSTEM
            .share_legend(
                storyteller=storyteller,
                listener=listener,
                universe=universe,
            )
        )

    @classmethod
    def adjust_storyteller_trust(
        cls,
        listener,
        storyteller_name,
        delta,
        reason,
        legend_id=None,
    ):
        return (
            cls.LEGEND_SYSTEM
            .adjust_storyteller_trust(
                listener=listener,
                storyteller_name=
                    storyteller_name,
                delta=delta,
                reason=reason,
                legend_id=legend_id,
            )
        )

    @classmethod
    def contradict_heard_legend(
        cls,
        cat,
        legend_id,
        reason=(
            'personal_observation_'
            'contradicted'
        ),
    ):
        return (
            cls.LEGEND_SYSTEM
            .contradict_heard_legend(
                cat=cat,
                legend_id=legend_id,
                reason=reason,
            )
        )

    @staticmethod
    def _trust_in_cat(
        listener,
        storyteller_name,
    ):
        return (
            CatKnowledge
            .LEGEND_SYSTEM
            ._trust_in_cat(
                listener,
                storyteller_name,
            )
        )

    @classmethod
    def remember_place(
        cls,
        cat,
        layer,
        position,
        source='direct_exploration',
        safe=None,
        danger=None,
        universe_tick=None,
        details=None,
    ):
        knowledge = cls.ensure_cat_knowledge(cat)
        normalized_position = cls._position(position)

        place = cls._find_place(
            knowledge.known_places,
            layer=layer,
            position=normalized_position,
        )

        if place is None:
            place = CatKnownPlace(
                place_id=cls._place_id(
                    layer,
                    normalized_position,
                ),
                layer=str(layer),
                position=normalized_position,
                discovered_by=cat.name,
                first_source=source,
                last_source=source,
                first_seen_tick=universe_tick,
                last_seen_tick=universe_tick,
                details=deepcopy(
                    details or {}
                ),
            )

            knowledge.known_places.append(place)

        else:
            place.record_visit(
                source=source,
                universe_tick=universe_tick,
                details=details,
            )

        place.record_safety(
            safe=safe,
            danger=danger,
        )

        return deepcopy(place)




    @classmethod
    def learn_aroma(
        cls,
        cat,
        identity,
        components,
        source='direct_experience',
    ):
        knowledge = (
            cls.ensure_cat_knowledge(
                cat
            )
        )

        known = next(
            (
                item
                for item in knowledge.known_aromas
                if item.identity
                == identity
            ),
            None,
        )

        if known is None:
            known = CatKnownAroma.create(
                identity=identity,
                components=components,
                source=source,
            )

            knowledge.known_aromas.append(
                known
            )

        else:
            known.record_encounter(
                components=components,
                source=source,
            )

        return deepcopy(
            known
        )

    @classmethod
    def recognize_aroma(
        cls,
        cat,
        components,
        minimum_similarity=0.55,
    ):
        knowledge = (
            cls.ensure_cat_knowledge(
                cat
            )
        )

        matches = []

        for known in knowledge.known_aromas:
            similarity = (
                known.similarity_to(
                    components
                )
            )

            if (
                similarity
                < minimum_similarity
            ):
                continue

            matches.append(
                CatAromaMatch(
                    identity=known.identity,
                    similarity=similarity,
                    confidence=known.confidence,
                    encounters=known.encounters,
                )
            )

        matches.sort(
            key=lambda item: (
                item.similarity,
                item.confidence,
            ),
            reverse=True,
        )

        if not matches:
            return CatAromaRecognition()

        winner = matches[0]

        return CatAromaRecognition(
            recognized=True,
            identity=winner.identity,
            similarity=winner.similarity,
            matches=matches,
        )

    @classmethod
    def remember_scent_place(
        cls,
        cat,
        layer,
        position,
        source_id,
        recognized_identity=None,
        components=None,
        perceived_intensity=0.0,
        universe_tick=None,
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        position = cls._position(
            position
        )

        place_id = cls._place_id(
            layer,
            position,
        )

        identity = (
            recognized_identity
            or 'unknown_aroma'
        )

        memory = next(
            (
                item
                for item in knowledge.known_scent_places
                if item.place_id == place_id
                and item.identity == identity
                and item.source_id == source_id
            ),
            None,
        )

        if memory is None:
            intensity = float(
                perceived_intensity
            )

            memory = CatScentPlaceMemory(
                place_id=place_id,
                layer=layer,
                position=position,
                source_id=source_id,
                identity=identity,
                confidence=(
                    0.6
                    if recognized_identity
                    else 0.3
                ),
                last_intensity=intensity,
                strongest_intensity=intensity,
                components=deepcopy(
                    components or {}
                ),
                first_seen_tick=universe_tick,
                last_seen_tick=universe_tick,
            )

            knowledge.known_scent_places.append(memory)

        else:
            memory.record_observation(
                recognized_identity=(
                    recognized_identity
                ),
                components=components,
                perceived_intensity=(
                    perceived_intensity
                ),
                universe_tick=universe_tick,
            )

        return deepcopy(memory)

    @classmethod
    def remember_olfaction(cls, cat, olfaction, current_layer, universe_tick=None):
        remembered = []
        knowledge = cls.ensure_cat_knowledge(cat)
        if universe_tick is not None:
            knowledge.scent_clock_tick = universe_tick
        for item in olfaction.detected_aromas:
            recognition = item.recognition
            identity = (
                recognition.identity
                if recognition.recognized
                else None
            )
            position = item.position
            if not isinstance(position, SpatialVector3):
                continue
            remembered.append(cls.remember_scent_place(cat=cat, layer=current_layer, position=position, source_id=item.entity_id, recognized_identity=identity, components=item.raw_components, perceived_intensity=item.perceived_intensity, universe_tick=universe_tick))
        ambient = olfaction.ambient_aroma

        if ambient is not None:
            recognition = (
                ambient.recognition
            )

            identity = (
                recognition.identity
                if recognition.recognized
                else ambient.source
            )

            remembered.append(
                cls.remember_scent_place(
                    cat=cat,
                    layer=current_layer,
                    position=cat.position,
                    source_id='ambient',
                    recognized_identity=identity,
                    components=(
                        ambient.components
                    ),
                    perceived_intensity=sum(
                        float(value)
                        for value
                        in ambient.components.values()
                    ),
                    universe_tick=(
                        universe_tick
                    ),
                )
            )
        return remembered

    @classmethod
    def infer_scent_direction(
        cls,
        cat,
        identity,
        layer,
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        memories = [
            memory
            for memory in knowledge.known_scent_places
            if memory.identity == identity
            and memory.layer == layer
            and isinstance(
                memory.position,
                SpatialVector3,
            )
            and memory.last_seen_tick
            is not None
        ]

        if len(memories) < 2:
            return CatScentTrailDirection(
                inferred=False,
                reason='not_enough_scent_points',
            )

        memories.sort(
            key=lambda memory: int(
                memory.last_seen_tick
            )
        )

        newest = memories[-1]

        older = next(
            (
                memory
                for memory in reversed(
                    memories[:-1]
                )
                if memory.position
                != newest.position
            ),
            None,
        )

        if older is None:
            return CatScentTrailDirection(
                inferred=False,
                reason='no_distinct_scent_positions',
            )

        start = older.position
        end = newest.position

        vector = SpatialVector3(
            x=end.x - start.x,
            y=end.y - start.y,
            z=end.z - start.z,
        )
        distance = SpatialVector3.zero().distance_to(vector)

        if distance <= 0.0:
            return CatScentTrailDirection(
                inferred=False,
                reason='zero_length_scent_direction',
            )

        tick_delta = (
            int(
                newest.last_seen_tick
            )
            - int(
                older.last_seen_tick
            )
        )

        if tick_delta <= 0:
            return CatScentTrailDirection(
                inferred=False,
                reason='scent_order_not_temporal',
            )

        unit_vector = SpatialVector3(
            x=vector.x / distance,
            y=vector.y / distance,
            z=vector.z / distance,
        )

        current_tick = knowledge.scent_clock_tick

        if current_tick is None:
            newest_age = 0
        else:
            newest_age = max(
                0,
                int(current_tick)
                - int(
                    newest.last_seen_tick
                ),
            )

        freshness = (
            0.5
            ** (
                newest_age
                / 50.0
            )
        )

        confidence = min(
            1.0,
            (
                float(
                    older.confidence
                )
                + float(
                    newest.confidence
                )
            )
            / 2.0
            * freshness,
        )

        return CatScentTrailDirection(
            inferred=True,
            identity=identity,
            layer=layer,
            from_position=start,
            to_position=end,
            vector=vector,
            unit_vector=unit_vector,
            distance=distance,
            tick_delta=tick_delta,
            newest_age_ticks=newest_age,
            freshness=freshness,
            confidence=confidence,
            from_source_id=(
                older.source_id
            ),
            to_source_id=(
                newest.source_id
            ),
        )







    @classmethod
    def _find_place(cls, places, layer, position):
        place_id = cls._place_id(layer, position)
        return next((place for place in places if place.place_id == place_id), None)

    @staticmethod
    def _position(position):
        return require_spatial_vector(position, field_name="cat knowledge position")

    @classmethod
    def _place_id(cls, layer, position):
        position = cls._position(position)
        return f"{layer}:{position.x:.2f}:{position.y:.2f}:{position.z:.2f}"
