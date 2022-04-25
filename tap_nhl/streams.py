"""Stream type classes for tap-nhl."""
import copy
import logging
import pendulum
import pytz
from datetime import datetime, timedelta

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, cast

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.helpers._state import (
    get_starting_replication_value,
    write_starting_replication_value
    )

from tap_nhl.client import nhlStream

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


class ConferencesStream(nhlStream):
    name = "conferences"
    path = "/conferences"
    primary_keys = ["id"]
    replication_key = "id"
    records_jsonpath = "$.conferences[*]"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("link", th.StringType),
        th.Property("abbreviation", th.StringType),
        th.Property("shortName", th.StringType),
        th.Property("active", th.BooleanType)
    ).to_dict()

class SeasonsStream(nhlStream):
    name = "seasons"
    path = "/seasons"
    primary_keys = ["seasonId"]
    records_jsonpath = "$.seasons[*]"
    replication_key = "seasonId"
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

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.
        Args:
            context: Stream partition or context dictionary.
        Yields:
            An item for every record in the response.
        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        context = context if context else {}
        start_year = int(self.config.get("start_year"))
        current_year = start_year
        next_year = start_year + 1
        context["current_season"] = str(current_year) + str(next_year)
        context["next_season"] = str(next_year) + str(next_year + 1)
        end_year = int(self.config.get("end_year"))
        finished = False
        decorated_request = self.request_decorator(self._request)

        while not finished:
            prepared_request = self.prepare_request(context, next_page_token=None)
            resp = decorated_request(prepared_request, context)
            for row in self.parse_response(resp):
                yield row
            # Cycle until the next_date is after the specified end date
            current_year = next_year
            next_year = current_year + 1
            context["current_season"] = str(current_year) + str(next_year)
            context["next_season"] = str(next_year) + str(next_year + 1)
            finished = next_year > end_year

    def get_url(self, context: Optional[dict]) -> int:
        """Get stream entity URL.

        Developers override this method to perform dynamic URL generation.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            A URL, optionally targeted to a specific partition or context.
        """
        url = "".join([self.url_base, self.path or ""])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        url = url + f"/{context['current_season']}"
        return url

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "season_id": record["seasonId"],
            "season_start_date": record["regularSeasonStartDate"],
            "season_end_date": record["seasonEndDate"]
        }

class ScheduleStream(nhlStream):
    """Define custom stream."""
    name = "schedule"
    path = "/schedule"
    primary_keys = ["gamePk"]
    records_jsonpath = "$.dates[*].games[*]"
    replication_key = "scheduleDate"
    parent_stream_type = SeasonsStream
    schema = th.PropertiesList(
        th.Property("gamePk", th.IntegerType),
        th.Property("scheduleDate", th.DateTimeType),
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
    ).to_dict()


    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.
        Args:
            context: Stream partition or context dictionary.
        Yields:
            An item for every record in the response.
        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        context = context if context else {}
        season_start_date = datetime.strptime(context["season_start_date"], "%Y-%m-%d") # from parent stream SeasonsStream
        season_end_date = datetime.strptime(context["season_end_date"], "%Y-%m-%d").replace(tzinfo=None) # from parent stream SeasonsStream
        override_end_date = datetime.strptime(self.config.get("override_end_date"), "%Y-%m-%d").replace(tzinfo=None) # override end date
        context["start_date"] = datetime.strptime(season_start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
        context["next_date"] = context["start_date"] + timedelta(days=1)
        end_date = min(season_end_date, override_end_date) # if there is an end date override, use whichever ends sooner

        finished = False
        decorated_request = self.request_decorator(self._request)

        while not finished:
            prepared_request = self.prepare_request(context, next_page_token=None)
            resp = decorated_request(prepared_request, context)
            for row in self.parse_response(resp):
                row["scheduleDate"] = context["start_date"]
                yield row
            # Cycle until the next_date is after the specified end date
            logging.info("start date", context["start_date"])
            context["start_date"] = context["next_date"]
            context["next_date"] = context["start_date"] + timedelta(days=1)
            finished = context["next_date"] > end_date


    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = super().get_url_params(context, next_page_token)
        params.update(
            {
                "date": datetime.strftime(context["start_date"], "%Y-%m-%d")
            }
        )
        return params

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "game_id": record["gamePk"]
        }


class LivePlaysStream(nhlStream):
    name = "live_plays"
    path = "/game"
    primary_keys = ["game_id"]
    replication_key = "game_id"
    records_jsonpath = "$.liveData.plays.allPlays[*]"
    parent_stream_type = ScheduleStream
    ignore_parent_replication_keys = True
    path = "/game/{game_id}/feed/live"
    schema = th.PropertiesList(
        th.Property("game_id", th.IntegerType),
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
    ).to_dict()


class LiveBoxscoreStream(nhlStream):
    name = "live_boxscore"
    primary_keys = ["game_id"]
    records_jsonpath = "$.liveData.boxscore"
    replication_key = "game_id"
    parent_stream_type = ScheduleStream
    ignore_parent_replication_keys = True
    path = "/game/{game_id}/feed/live"
    schema = th.PropertiesList(
        th.Property("game_id", th.IntegerType),
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
    ).to_dict()

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        """As needed, append or transform raw data to match expected structure.

        Optional. This method gives developers an opportunity to "clean up" the results
        prior to returning records to the downstream tap - for instance: cleaning,
        renaming, or appending properties to the raw record result returned from the
        API.

        Developers may also return `None` from this method to filter out
        invalid or not-applicable records from the stream.

        Args:
            row: Individual record in the stream.
            context: Stream partition or context dictionary.

        Returns:
            The resulting record dict, or `None` if the record should be excluded.
        """
        for team_type in ["away", "home"]:
            player_data = list()
            if row["teams"].get(team_type):
                if row["teams"][team_type].get("players"):
                    player_ids = row["teams"][team_type]["players"].keys()
                    for player_id in player_ids:
                        # player stats
                        if row["teams"][team_type]["players"][player_id].get("stats"):
                            player_stats_key = list(row["teams"][team_type]["players"][player_id]["stats"])
                            row["teams"][team_type]["players"][player_id]["stats"]["playerStats"] = row["teams"][team_type]["players"][player_id]["stats"][player_stats_key[0]]
                            row["teams"][team_type]["players"][player_id]["stats"].pop(player_stats_key[0])
                        player_data.append(row["teams"][team_type]["players"][player_id]) # append the nested player_ids into a list
                    row["teams"][team_type]["players"] = player_data # assign back to players
        return row


class LiveLinescoreStream(nhlStream):
    name = "live_linescore"
    primary_keys = ["game_id"]
    replication_key = "game_id"
    records_jsonpath = "$.liveData.linescore"
    ignore_parent_replication_keys = True
    path = "/game/{game_id}/feed/live"
    parent_stream_type = ScheduleStream

    schema = th.PropertiesList(
        th.Property("game_id", th.IntegerType),
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
    ).to_dict()


class TeamsStream(nhlStream):
    name = "teams"
    primary_keys = ["id"]
    records_jsonpath = "$.teams[*]"
    replication_key = "id"
    path = "/teams"
    parent_stream_type = SeasonsStream

    schema = th.PropertiesList(
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
        th.Property("season_id", th.StringType),
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
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = super().get_url_params(context, next_page_token)
        params.update(
            {
                "expand": "team.roster",
                "season": context["season_id"]
            }
        )
        return params

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "roster": record["roster"]["roster"]
        }

class DivisionsStream(nhlStream):
    name = "divisions"
    primary_keys = ["id"]
    records_jsonpath = "$.divisions[*]"
    replication_key = None
    path = "/divisions"

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

class DraftStream(nhlStream):
    def get_url(self, context: Optional[dict]) -> int:
        """Get stream entity URL.

        Developers override this method to perform dynamic URL generation.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            A URL, optionally targeted to a specific partition or context.
        """
        url = "".join([self.url_base, self.path or ""])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        url = url + f"/{context['draft_year_start']}"
        return url

    name = "draft"
    primary_keys = ["year", "$.prospect.id"]
    records_jsonpath = "$.drafts[*].rounds[*].picks[*]"
    replication_key = "year"
    path = "/draft"

    schema = th.PropertiesList(
        th.Property("year", th.IntegerType),
        th.Property("round", th.StringType),
        th.Property("pickOverall", th.IntegerType),
        th.Property("pickInRound", th.IntegerType),
        th.Property("team", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("prospect", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("fullName", th.StringType),
            th.Property("link", th.StringType),
        ))
    ).to_dict()

    def get_starting_replication_key_value(
        self, context: Optional[dict]
    ) -> Optional[int]:
        """Return starting replication key value."""
        if self.replication_key:
            state = self.get_context_state(context)
            replication_key_value = state.get("replication_key_value")
            if replication_key_value and self.replication_key == state.get(
                "replication_key"
            ):
                return replication_key_value
        return None

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.
        Args:
            context: Stream partition or context dictionary.
        Yields:
            An item for every record in the response.
        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        context = context if context else {}
        if self.get_starting_replication_key_value(context):
            context["draft_year_start"] = int(self.get_starting_replication_key_value(context))
        else:
            context["draft_year_start"] = int(self.config.get("draft_year_start"))
        context["draft_year_end"] = context["draft_year_start"] + 1#relativedelta(years=1)
        finished = False
        decorated_request = self.request_decorator(self._request)

        while not finished:
            prepared_request = self.prepare_request(context, next_page_token=None)
            resp = decorated_request(prepared_request, context)
            for row in self.parse_response(resp):
                yield row
            # Cycle until the next end_date of retrieved requests is after the specified end date
            context["draft_year_start"] = context["draft_year_end"]
            context["draft_year_end"] = context["draft_year_start"] + 1
            finished = context["draft_year_end"] > int(self.config.get("draft_year_end"))

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        if record["prospect"].get("id"):
            return {
                "prospect_id": record["prospect"]["id"]
            }



class DraftProspectsStream(nhlStream):
    name = "draft_prospects"
    primary_keys = ["id"]
    records_jsonpath = "$.prospects[*]"
    replication_key = None
    ignore_parent_replication_key = True
    path = "/draft/prospects/{prospect_id}"
    parent_stream_type = DraftStream

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


class PeopleStream(nhlStream):
    name = "people"
    primary_keys = ["id"]
    records_jsonpath = "$.people[*]"
    replication_key = None
    path = "/people"
    parent_stream_type = TeamsStream

    def get_url(self, context: Optional[dict]) -> int:
        """Get stream entity URL.

        Developers override this method to perform dynamic URL generation.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            A URL, optionally targeted to a specific partition or context.
        """
        url = "".join([self.url_base, self.path or ""])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        url = url + f"/{context['current_person_id']}"
        return url

    schema = th.PropertiesList(
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
        th.Property("currentTeam", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
            th.Property("link", th.StringType),
        )),
        th.Property("primaryPosition", th.ObjectType(
            th.Property("code", th.StringType),
            th.Property("name", th.StringType),
            th.Property("type", th.StringType),
            th.Property("abbreviation", th.StringType),
        ))
    ).to_dict()

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.
        Args:
            context: Stream partition or context dictionary.
        Yields:
            An item for every record in the response.
        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        context = context if context else {}
        decorated_request = self.request_decorator(self._request)
        for people in context["roster"]:
            person_id = people["person"]["id"]
            context["current_person_id"] = person_id
            prepared_request = self.prepare_request(context, next_page_token=None)
            resp = decorated_request(prepared_request, context)
            for row in self.parse_response(resp):
                yield row
