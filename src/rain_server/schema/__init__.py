import graphql.validation
import strawberry
import strawberry.extensions
import strawberry.schema.config

from .data_schemas import Location, Measurement, MeasurementType, Sensor
from .query import Query
from .mutation import Mutation


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
#    extensions=[
#        strawberry.extensions.AddValidationRules(
#            [graphql.validation.NoSchemaIntrospectionCustomRule]
#        ),
#    ],
)
