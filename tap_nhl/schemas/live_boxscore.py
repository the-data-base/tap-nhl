import singer_sdk.typing as th
from tap_nhl.schemas.stream_schema_object import StreamSchemaObject

class LiveBoxscoreObject(StreamSchemaObject):
    properties = th.PropertiesList(
        th.Property("gameId", th.IntegerType),
        th.Property("teams", th.ObjectType(
            th.Property("away", th.ObjectType(
                th.Property("team", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("link", th.StringType),
                    th.Property("abbreviation", th.StringType),
                    th.Property("triCode", th.StringType),
                )),
                th.Property("teamStats", th.ObjectType(
                    th.Property("teamSkaterStats", th.ObjectType(
                        th.Property("goals", th.IntegerType),
                        th.Property("pim", th.IntegerType),
                        th.Property("shots", th.IntegerType),
                        th.Property("powerPlayPercentage", th.StringType),
                        th.Property("powerPlayGoals", th.NumberType),
                        th.Property("powerPlayOpportunities", th.NumberType),
                        th.Property("faceOffWinPercentage", th.StringType),
                        th.Property("blocked", th.IntegerType),
                        th.Property("takeaways", th.IntegerType),
                        th.Property("giveaways", th.IntegerType),
                        th.Property("hits", th.IntegerType),
                    ))
                )),
                th.Property("players", th.ArrayType(th.ObjectType(
                    # th.Property("player", th.ObjectType(
                        th.Property("person", th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("fullName", th.StringType),
                            th.Property("link", th.StringType),
                            th.Property("shootsCatches", th.StringType),
                            th.Property("rosterStatus", th.StringType),
                        )),
                        th.Property("jerseyNumber", th.StringType),
                        th.Property("position", th.ObjectType(
                            th.Property("code", th.StringType),
                            th.Property("name", th.StringType),
                            th.Property("type", th.StringType),
                            th.Property("abbreviation", th.StringType),
                        )),
                        th.Property("stats", th.ObjectType(
                            th.Property("playerStats", th.ObjectType(
                                th.Property("timeOnIce", th.StringType),
                                th.Property("assists", th.IntegerType),
                                th.Property("goals", th.IntegerType),
                                th.Property("shots", th.IntegerType),
                                th.Property("hits", th.IntegerType),
                                th.Property("powerPlayGoals", th.IntegerType),
                                th.Property("powerPlayAssists", th.IntegerType),
                                th.Property("penaltyMinutes", th.IntegerType),
                                th.Property("faceOffWins", th.IntegerType),
                                th.Property("faceoffTaken", th.IntegerType),
                                th.Property("takeaways", th.IntegerType),
                                th.Property("giveaways", th.IntegerType),
                                th.Property("shortHandedGoals", th.IntegerType),
                                th.Property("shortHandedAssists", th.IntegerType),
                                th.Property("blocked", th.IntegerType),
                                th.Property("plusMinus", th.IntegerType),
                                th.Property("evenTimeOnIce", th.StringType),
                                th.Property("powerPlayTimeOnIce", th.StringType),
                                th.Property("shortHandedTimeOnIce", th.StringType),
                                th.Property("pim", th.IntegerType),
                                th.Property("saves", th.IntegerType),
                                th.Property("powerPlaySaves", th.IntegerType),
                                th.Property("shortHandedSaves", th.IntegerType),
                                th.Property("evenSaves", th.IntegerType),
                                th.Property("shortHandedShotsAgainst", th.IntegerType),
                                th.Property("evenShotsAgainst", th.IntegerType),
                                th.Property("powerPlayShotsAgainst", th.IntegerType),
                                th.Property("decision", th.StringType),
                                th.Property("savePercentage", th.NumberType),
                                th.Property("powerPlaySavePercentage", th.NumberType),
                                th.Property("evenStrengthSavePercentage", th.NumberType),
                            ))
                        ))
                ))),
                # th.Property("goalies", th.ArrayType(th.IntegerType)),
                # th.Property("skaters", th.ArrayType(th.IntegerType)),
                th.Property("onIce", th.ArrayType(th.IntegerType)),
                th.Property("onIcePlus", th.ArrayType(th.ObjectType(
                    th.Property("playerId", th.IntegerType),
                    th.Property("shiftDuration", th.IntegerType),
                    th.Property("stamina", th.IntegerType),
                ))),
                th.Property("scratches", th.ArrayType(th.IntegerType)),
                th.Property("penaltyBox", th.ArrayType(th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("timeRemaining", th.StringType),
                    th.Property("active", th.BooleanType),
                ))),
                th.Property("coaches", th.ArrayType(th.ObjectType(
                    th.Property("person", th.ObjectType(
                        th.Property("fullName", th.StringType),
                        th.Property("link", th.StringType),
                    )),
                    th.Property("position", th.ObjectType(
                        th.Property("code", th.StringType),
                        th.Property("name", th.StringType),
                        th.Property("type", th.StringType),
                        th.Property("abbreviation", th.StringType),
                    ))
                )))
            )),
            th.Property("home", th.ObjectType(
                th.Property("team", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("link", th.StringType),
                    th.Property("abbreviation", th.StringType),
                    th.Property("triCode", th.StringType),
                )),
                th.Property("teamStats", th.ObjectType(
                    th.Property("teamSkaterStats", th.ObjectType(
                        th.Property("goals", th.IntegerType),
                        th.Property("pim", th.IntegerType),
                        th.Property("shots", th.IntegerType),
                        th.Property("powerPlayGoals", th.NumberType),
                        th.Property("powerPlayOpportunities", th.NumberType),
                        th.Property("faceOffWinPercentage", th.StringType),
                        th.Property("blocked", th.IntegerType),
                        th.Property("takeaways", th.IntegerType),
                        th.Property("giveaways", th.IntegerType),
                        th.Property("hits", th.IntegerType),
                    ))
                )),
                th.Property("players", th.ArrayType(th.ObjectType(
                        th.Property("person", th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("fullName", th.StringType),
                            th.Property("link", th.StringType),
                            th.Property("shootsCatches", th.StringType),
                            th.Property("rosterStatus", th.StringType),
                        )),
                        th.Property("jerseyNumber", th.StringType),
                        th.Property("position", th.ObjectType(
                            th.Property("code", th.StringType),
                            th.Property("name", th.StringType),
                            th.Property("type", th.StringType),
                            th.Property("abbreviation", th.StringType),
                        )),
                        th.Property("stats", th.ObjectType(
                            th.Property("playerStats", th.ObjectType(
                                th.Property("timeOnIce", th.StringType),
                                th.Property("assists", th.IntegerType),
                                th.Property("goals", th.IntegerType),
                                th.Property("shots", th.IntegerType),
                                th.Property("hits", th.IntegerType),
                                th.Property("powerPlayPercentage", th.StringType),
                                th.Property("powerPlayGoals", th.IntegerType),
                                th.Property("powerPlayAssists", th.IntegerType),
                                th.Property("penaltyMinutes", th.IntegerType),
                                th.Property("faceOffWins", th.IntegerType),
                                th.Property("faceoffTaken", th.IntegerType),
                                th.Property("takeaways", th.IntegerType),
                                th.Property("giveaways", th.IntegerType),
                                th.Property("shortHandedGoals", th.IntegerType),
                                th.Property("shortHandedAssists", th.IntegerType),
                                th.Property("blocked", th.IntegerType),
                                th.Property("plusMinus", th.IntegerType),
                                th.Property("evenTimeOnIce", th.StringType),
                                th.Property("powerPlayTimeOnIce", th.StringType),
                                th.Property("shortHandedTimeOnIce", th.StringType),
                                th.Property("pim", th.IntegerType),
                                th.Property("saves", th.IntegerType),
                                th.Property("powerPlaySaves", th.IntegerType),
                                th.Property("shortHandedSaves", th.IntegerType),
                                th.Property("evenSaves", th.IntegerType),
                                th.Property("shortHandedShotsAgainst", th.IntegerType),
                                th.Property("evenShotsAgainst", th.IntegerType),
                                th.Property("powerPlayShotsAgainst", th.IntegerType),
                                th.Property("decision", th.StringType),
                                th.Property("savePercentage", th.NumberType),
                                th.Property("powerPlaySavePercentage", th.NumberType),
                                th.Property("evenStrengthSavePercentage", th.NumberType),
                            ))
                        ))
                ))),
                # th.Property("goalies", th.ArrayType(th.IntegerType)),
                # th.Property("skaters", th.ArrayType(th.IntegerType)),
                th.Property("onIce", th.ArrayType(th.IntegerType)),
                th.Property("onIcePlus", th.ArrayType(th.ObjectType(
                    th.Property("playerId", th.IntegerType),
                    th.Property("shiftDuration", th.IntegerType),
                    th.Property("stamina", th.IntegerType),
                ))),
                th.Property("scratches", th.ArrayType(th.IntegerType)),
                th.Property("penaltyBox", th.ArrayType(th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("timeRemaining", th.StringType),
                    th.Property("active", th.BooleanType),
                ))),
                th.Property("coaches", th.ArrayType(th.ObjectType(
                    th.Property("person", th.ObjectType(
                        th.Property("fullName", th.StringType),
                        th.Property("link", th.StringType),
                    )),
                    th.Property("position", th.ObjectType(
                        th.Property("code", th.StringType),
                        th.Property("name", th.StringType),
                        th.Property("type", th.StringType),
                        th.Property("abbreviation", th.StringType),
                    ))
                )))
            )),
        )),
        # th.Property("officials", th.ArrayType(th.ObjectType(
        #     th.Property("official", th.ObjectType(
        #         th.Property("id", th.IntegerType),
        #         th.Property("fullName", th.StringType),
        #         th.Property("link", th.StringType),
        #     )),
        #     th.Property("officialType", th.StringType)
        # )))
    )
