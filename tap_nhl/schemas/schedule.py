import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class ScheduleObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("gamePk", th.IntegerType),
        th.Property("link", th.StringType),
        th.Property("gameType", th.StringType),
        th.Property("season", th.StringType),
        th.Property("gameDate", th.DateTimeType),
        th.Property("status", th.ObjectType(
            th.Property("abstractGameState", th.StringType),
            th.Property("codedGameState", th.StringType),
            th.Property("detailedState", th.StringType),
            th.Property("statusCode", th.StringType),
            th.Property("startTimeTBD", th.BooleanType),
        )),
        th.Property("teams", th.ObjectType(
            th.Property("away", th.ObjectType(
                th.Property("leagueRecord", th.ObjectType(
                    th.Property("wins", th.IntegerType),
                    th.Property("losses", th.IntegerType),
                    th.Property("ot", th.IntegerType),
                    th.Property("type", th.StringType),
                )),
                th.Property("score", th.IntegerType),
                th.Property("team", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("link", th.StringType),
                ))
            )),
            th.Property("home", th.ObjectType(
                th.Property("leagueRecord", th.ObjectType(
                    th.Property("wins", th.IntegerType),
                    th.Property("losses", th.IntegerType),
                    th.Property("ot", th.IntegerType),
                    th.Property("type", th.StringType),
                )),
                th.Property("score", th.IntegerType),
                th.Property("team", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("link", th.StringType),
                ))
            )),
        )),
        th.Property("venue", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("content", th.ObjectType(
            th.Property("link", th.StringType)
        ))
    )
