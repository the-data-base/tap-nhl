import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class LiveLinescoreObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("gameId", th.IntegerType),
        th.Property("periods", th.ArrayType(th.ObjectType(
            th.Property("periodType", th.StringType),
            th.Property("startTime", th.DateTimeType),
            th.Property("endTime", th.DateTimeType),
            th.Property("num", th.IntegerType),
            th.Property("ordinalNum", th.StringType),
            th.Property("home", th.ObjectType(
                th.Property("goals", th.IntegerType),
                th.Property("shotsOnGoal", th.IntegerType),
                th.Property("rinkSide", th.StringType),
            )),
            th.Property("away", th.ObjectType(
                th.Property("goals", th.IntegerType),
                th.Property("shotsOnGoal", th.IntegerType),
                th.Property("rinkSide", th.StringType),
            )),
        ))),
        th.Property("shootoutInfo", th.ObjectType(
            th.Property("away", th.ObjectType(
                th.Property("scores", th.IntegerType),
                th.Property("attempts", th.IntegerType),
            )),
            th.Property("home", th.ObjectType(
                th.Property("scores", th.IntegerType),
                th.Property("attempts", th.IntegerType),
            )),
        )),
        th.Property("teams", th.ObjectType(
            th.Property("home", th.ObjectType(
                th.Property("team", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                )),
                th.Property("goals", th.IntegerType),
                th.Property("shotsOnGoal", th.IntegerType),
                th.Property("goaliePulled", th.BooleanType),
                th.Property("numSkaters", th.IntegerType),
                th.Property("powerPlay", th.BooleanType),
            )),
            th.Property("away", th.ObjectType(
                th.Property("team", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                )),
                th.Property("goals", th.IntegerType),
                th.Property("shotsOnGoal", th.IntegerType),
                th.Property("goaliePulled", th.BooleanType),
                th.Property("numSkaters", th.IntegerType),
                th.Property("powerPlay", th.BooleanType),
            )),
            th.Property("powerPlayStrength", th.StringType),
            th.Property("hasShootout", th.BooleanType),
        ))
    )
