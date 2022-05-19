import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class ConferencesObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("link", th.StringType),
        th.Property("abbreviation", th.StringType),
        th.Property("shortName", th.StringType),
        th.Property("active", th.BooleanType)
    )
