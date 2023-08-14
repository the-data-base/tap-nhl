import singer_sdk.typing as th

class SeasonsObject():
    schema = th.PropertiesList(
        th.Property("seasonId", th.StringType),
        th.Property("regularSeasonStartDate", th.StringType),
        th.Property("regularSeasonEndDate", th.StringType),
        th.Property("seasonEndDate", th.StringType),
        th.Property("numberOfGames", th.IntegerType),
        th.Property("tiesInUse", th.BooleanType),
        th.Property("olympicsParticipation", th.BooleanType),
        th.Property("conferencesInUse", th.BooleanType),
        th.Property("divisionsInUse", th.BooleanType),
        th.Property("wildCardInUse", th.BooleanType),
    ).to_dict()
