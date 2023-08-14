import singer_sdk.typing as th

class DraftProspectsObject():
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("fullName", th.StringType),
        th.Property("link", th.StringType),
        th.Property("firstName", th.StringType),
        th.Property("lastName", th.StringType),
        th.Property("birthDate", th.StringType),
        th.Property("birthCity", th.StringType),
        th.Property("birthStateProvince", th.StringType),
        th.Property("birthCountry", th.StringType),
        th.Property("height", th.StringType),
        th.Property("weight", th.IntegerType),
        th.Property("shootsCatches", th.StringType),
        th.Property("primaryPosition", th.ObjectType(
            th.Property("code", th.StringType),
            th.Property("name", th.StringType),
            th.Property("type", th.StringType),
            th.Property("abbreviation", th.StringType),
        )),
        th.Property("nhlPlayerId", th.IntegerType),
        th.Property("draftStatus", th.StringType),
        th.Property("prospectCategory", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("shortName", th.StringType),
            th.Property("name", th.StringType),
        )),
        th.Property("amateurTeam", th.ObjectType(
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("amateurLeague", th.ObjectType(
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("ranks", th.ObjectType(
            th.Property("midterm", th.IntegerType),
            th.Property("draftYear", th.IntegerType),
        )),
    ).to_dict()
