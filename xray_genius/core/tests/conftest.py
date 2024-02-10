from pytest_factoryboy import register

from . import factories

register(factories.UserFactory)
register(factories.CTInputFileFactory)
register(factories.SessionFactory)
register(factories.InputParametersFactory)
register(factories.OutputImageFactory)
