import singer_sdk.typing as th

class DivisionsObject():
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("nameShort", th.StringType),
        th.Property("link", th.StringType),
        th.Property("abbreviation", th.StringType),
        th.Property("conference", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("active", th.BooleanType),
    ).to_dict()
