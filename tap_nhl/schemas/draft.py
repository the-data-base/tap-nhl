import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class DraftObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("year", th.IntegerType),
        th.Property("round", th.StringType),
        th.Property("pickOverall", th.IntegerType),
        th.Property("pickInRound", th.IntegerType),
        th.Property("team", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("prospect", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("fullName", th.StringType),
            th.Property("link", th.StringType),
        ))
    )
