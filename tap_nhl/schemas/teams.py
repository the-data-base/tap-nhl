import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class TeamsObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("link", th.StringType),
        th.Property("venue", th.ObjectType(
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
            th.Property("city", th.StringType),
            th.Property("timeZone", th.ObjectType(
                th.Property("id", th.StringType),
                th.Property("offset", th.IntegerType),
                th.Property("tz", th.StringType)
            )),
        )),
        th.Property("abbreviation", th.StringType),
        th.Property("teamName", th.StringType),
        th.Property("locationName", th.StringType),
        th.Property("firstYearOfPlay", th.StringType),
        th.Property("division", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("nameShort", th.StringType),
            th.Property("link", th.StringType),
            th.Property("abbreviation", th.StringType),
        )),
        th.Property("conference", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("franchise", th.ObjectType(
            th.Property("franchiseId", th.IntegerType),
            th.Property("teamName", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("seasonId", th.StringType),
        th.Property("roster", th.ObjectType(
            th.Property("roster", th.ArrayType(th.ObjectType(
                th.Property("person", th.ObjectType(
                    th.Property("id", th.IntegerType)
                ))
            )))
        )),
        th.Property("shortName", th.StringType),
        th.Property("officialSiteUrl", th.StringType),
        th.Property("franchiseId", th.IntegerType),
        th.Property("active", th.BooleanType)
    )
