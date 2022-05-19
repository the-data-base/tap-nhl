import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class LivePlaysObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("gameId", th.IntegerType),
        th.Property("players", th.ArrayType(th.ObjectType(
            th.Property("player", th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("fullName", th.StringType),
                th.Property("link", th.StringType),
            )),
            th.Property("playerType", th.StringType)
        ))),
        th.Property("result", th.ObjectType(
            th.Property("event", th.StringType),
            th.Property("eventCode", th.StringType),
            th.Property("eventTypeId", th.StringType),
            th.Property("description", th.StringType),
            th.Property("secondaryType", th.StringType),
            th.Property("penaltySeverity", th.StringType),
            th.Property("penaltyMinutes", th.IntegerType),
        )),
        th.Property("about", th.ObjectType(
            th.Property("eventIdx", th.IntegerType),
            th.Property("eventId", th.IntegerType),
            th.Property("period", th.IntegerType),
            th.Property("periodType", th.StringType),
            th.Property("ordinalNum", th.StringType),
            th.Property("periodTime", th.StringType),
            th.Property("periodTimeRemaining", th.StringType),
            th.Property("dateTime", th.StringType),
            th.Property("goals", th.ObjectType(
                th.Property("away", th.IntegerType),
                th.Property("home", th.IntegerType),
            )),
        )),
        th.Property("coordinates", th.ObjectType(
            th.Property("x", th.CustomType({ "type": ["integer", "number"] })),
            th.Property("y", th.CustomType({ "type": ["integer", "number"] })),
        )),
        th.Property("team", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
            th.Property("triCode", th.StringType),
        ))
    )
