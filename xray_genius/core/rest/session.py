from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Router
from pydantic.types import UUID4

from xray_genius.core.models import InputParameters, Session

session_router = Router()


class ParametersRequestSchema(ModelSchema):
    class Config:
        model = InputParameters
        model_fields = [
            'carm_alpha',
            'carm_alpha_kappa',
            'carm_beta',
            'carm_beta_kappa',
            'carm_push_pull',
            'carm_head_foot_translation',
            'carm_raise_lower',
            'source_to_detector_distance',
            'num_samples',
        ]


@session_router.post('/{session_pk}/parameters/')
def set_parameters(
    request: HttpRequest, session_pk: UUID4, parameter_data: ParametersRequestSchema
):
    session = get_object_or_404(Session, pk=session_pk)

    if session.owner != request.user:
        raise Http404()

    InputParameters.objects.create(session=session, **parameter_data.dict())

    # TODO: what do we return to VolView here?
    return 200
