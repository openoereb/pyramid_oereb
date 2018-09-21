# -*- coding: utf-8 -*-
from pyramid_oereb.standard.xtf_import.util import parse_ref


class BaseRefinement(object):

    TAG_BASE = 'Grundlage'
    TAG_REFINEMENT = 'Verfeinerung'

    def __init__(self, session, model_base, model_refinement):
        self._session = session
        self._model_base = model_base
        self._model_refinement = model_refinement

    def parse(self, base_refinement):  # pragma: no cover
        base_id = parse_ref(base_refinement, self.TAG_BASE)
        refinement_id = parse_ref(base_refinement, self.TAG_REFINEMENT)
        instance_base = self._model_base(
            id='{0}-{1}'.format(refinement_id, base_id),
            public_law_restriction_id=refinement_id,
            public_law_restriction_base_id=base_id
        )
        self._session.add(instance_base)
        instance_refinement = self._model_refinement(
            id='{0}-{1}'.format(base_id, refinement_id),
            public_law_restriction_id=base_id,
            public_law_restriction_refinement_id=refinement_id
        )
        self._session.add(instance_refinement)
