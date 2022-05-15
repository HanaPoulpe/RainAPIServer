import graphql.validation
import strawberry
import strawberry.extensions
import strawberry.schema.config

from .data_schemas import Location, Measurement, MeasurementType, Sensor
from .mutation import Mutation
from .query import Query

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # extensions=[
    #     strawberry.extensions.AddValidationRules(
    #         [graphql.validation.NoSchemaIntrospectionCustomRule]
    #     ),
    # ],
)
