import singer_sdk.typing as th

class ShiftsObject():
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType()),
        th.Property("detailCode", th.IntegerType()),
        th.Property("duration", th.StringType()),
        th.Property("endTime", th.StringType()),
        th.Property("eventDescription", th.StringType()),
        th.Property("eventDetails", th.StringType()),
        th.Property("eventNumber", th.IntegerType()),
        th.Property("firstName", th.StringType()),
        th.Property("gameId", th.IntegerType()),
        th.Property("hexValue", th.StringType()),
        th.Property("lastName", th.StringType()),
        th.Property("period", th.IntegerType()),
        th.Property("playerId", th.IntegerType()),
        th.Property("shiftNumber", th.IntegerType()),
        th.Property("startTime", th.StringType()),
        th.Property("teamAbbrev", th.StringType()),
        th.Property("teamId", th.IntegerType()),
        th.Property("teamName", th.StringType()),
        th.Property("typeCode", th.IntegerType())
    ).to_dict()
