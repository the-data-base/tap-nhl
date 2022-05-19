import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class PeopleObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("fullName", th.StringType),
        th.Property("link", th.StringType),
        th.Property("firstName", th.StringType),
        th.Property("lastName", th.StringType),
        th.Property("primaryNumber", th.StringType),
        th.Property("birthDate", th.StringType),
        th.Property("birthCity", th.StringType),
        th.Property("birthStateProvince", th.StringType),
        th.Property("birthCountry", th.StringType),
        th.Property("nationality", th.StringType),
        th.Property("height", th.StringType),
        th.Property("weight", th.IntegerType),
        th.Property("active", th.BooleanType),
        th.Property("alternateCaptain", th.BooleanType),
        th.Property("captain", th.BooleanType),
        th.Property("rookie", th.BooleanType),
        th.Property("shootsCatches", th.StringType),
        th.Property("rosterStatus", th.StringType),
        th.Property("primaryPosition", th.ObjectType(
            th.Property("code", th.StringType),
            th.Property("name", th.StringType),
            th.Property("type", th.StringType),
            th.Property("abbreviation", th.StringType),
        )),
        th.Property("seasonId", th.StringType),
        th.Property("teamId", th.IntegerType),
    )
