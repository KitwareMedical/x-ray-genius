from django.contrib.auth.models import User
import factory.django

from xray_genius.core.models import CTInputFile, InputParameters, OutputImage, Session


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.SelfAttribute('email')
    email = factory.Faker('safe_email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class CTInputFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CTInputFile

    file = factory.django.FileField(filename='test_file.nrrd', data=b'fakefile')


class SessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Session

    owner = factory.SubFactory(UserFactory)
    parameters = factory.RelatedFactory(
        factory='xray_genius.core.tests.factories.InputParametersFactory',
        factory_related_name='session',
    )
    input_scan = factory.SubFactory(CTInputFileFactory)


class InputParametersFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InputParameters

    session = factory.SubFactory(factory=SessionFactory)

    carm_alpha = factory.Faker('pyint', min_value=0, max_value=360)
    carm_beta = factory.Faker('pyint', min_value=0, max_value=360)
    source_to_detector_distance = factory.Faker('pyfloat', min_value=0.0, max_value=500.0)


class OutputImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OutputImage

    session = factory.SubFactory(SessionFactory)
    image = factory.django.ImageField(filename='test_image.png', data=b'fakeimage')
