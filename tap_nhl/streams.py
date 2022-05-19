"""Stream type classes for tap-nhl."""
import copy
import logging

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, cast

from tap_nhl.client import nhlStream
from tap_nhl.schemas.shifts import ShiftsObject
from tap_nhl.schemas.conferences import ConferencesObject
from tap_nhl.schemas.seasons import SeasonsObject
from tap_nhl.schemas.schedule import ScheduleObject
from tap_nhl.schemas.live_plays import LivePlaysObject
from tap_nhl.schemas.live_boxscore import LiveBoxscoreObject
from tap_nhl.schemas.live_linescore import LiveLinescoreObject
from tap_nhl.schemas.teams import TeamsObject
from tap_nhl.schemas.divisions import DivisionsObject
from tap_nhl.schemas.draft import DraftObject
from tap_nhl.schemas.draft_prospects import DraftProspectsObject
from tap_nhl.schemas.people import PeopleObject

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


class ConferencesStream(nhlStream):
    name = "conferences"
    path = "/conferences"
    primary_keys = ["id"]
    records_jsonpath = "$.conferences[*]"
    replication_key = "id"
    schema = ConferencesObject.schema


class SeasonsStream(nhlStream):
    name = "seasons"
    path = "/seasons"
    primary_keys = ["seasonId"]
    records_jsonpath = "$.seasons[*]"
    replication_key = "seasonId"
    schema = SeasonsObject.schema

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
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

    def get_url(self, context: Optional[dict]) -> str:
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
            "seasonId": record["seasonId"]
        }


class ScheduleStream(nhlStream):
    name = "schedule"
    parent_stream_type = SeasonsStream
    path = "/schedule"
    primary_keys = ["gamePk"]
    records_jsonpath = "$.dates[*].games[*]"
    schema = ScheduleObject.schema

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = super().get_url_params(context, next_page_token)
        params.update(
            {
                "season": context["seasonId"]
            }
        )
        return params

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "gameId": record["gamePk"]
        }


class LivePlaysStream(nhlStream):
    ignore_parent_replication_keys = True
    name = "live_plays"
    parent_stream_type = ScheduleStream
    path = "/game/{gameId}/feed/live"
    primary_keys = ["gameId"]
    records_jsonpath = "$.liveData.plays.allPlays[*]"
    schema = LivePlaysObject.schema


class LiveBoxscoreStream(nhlStream):
    ignore_parent_replication_keys = True
    name = "live_boxscore"
    parent_stream_type = ScheduleStream
    path = "/game/{gameId}/feed/live"
    primary_keys = ["gameId"]
    records_jsonpath = "$.liveData.boxscore"
    replication_key = "gameId"
    schema = LiveBoxscoreObject.schema

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
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
    ignore_parent_replication_keys = True
    name = "live_linescore"
    parent_stream_type = ScheduleStream
    path = "/game/{gameId}/feed/live"
    primary_keys = ["gameId"]
    records_jsonpath = "$.liveData.linescore"
    replication_key = "gameId"
    schema = LiveLinescoreObject.schema


class TeamsStream(nhlStream):
    name = "teams"
    parent_stream_type = SeasonsStream
    path = "/teams"
    primary_keys = ["id"]
    records_jsonpath = "$.teams[*]"
    replication_key = "id"
    schema = TeamsObject.schema

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = super().get_url_params(context, next_page_token)
        params.update(
            {
                "expand": "team.roster",
                "season": context["seasonId"]
            }
        )
        return params

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "roster": record["roster"]["roster"],
            "seasonId": context["seasonId"],
            "teamId": record["id"]
        }


class DivisionsStream(nhlStream):
    name = "divisions"
    path = "/divisions"
    primary_keys = ["id"]
    records_jsonpath = "$.divisions[*]"
    replication_key = None
    schema = DivisionsObject.schema


class DraftStream(nhlStream):
    name = "draft"
    parent_stream_type = SeasonsStream
    path = "/draft"
    primary_keys = ["year", "$.prospect.id"]
    records_jsonpath = "$.drafts[*].rounds[*].picks[*]"
    replication_key = "year"
    schema = DraftObject.schema

    def get_url(self, context: Optional[dict]) -> str:
        url = "".join([self.url_base, self.path or ""])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        url = url + f"/{context['seasonId'][0:4]}"
        return url

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "prospectId": record["prospect"].get("id", "-1") # sometimes the prospect is missing and the fullName is "Void". In that case we pass a dummy prospect ID that doesnt have a corresponding resource.
        }


class DraftProspectsStream(nhlStream):
    name = "draft_prospects"
    parent_stream_type = DraftStream
    path = "/draft/prospects/{prospectId}"
    primary_keys = ["id"]
    records_jsonpath = "$.prospects[*]"
    schema = DraftProspectsObject.schema

    def get_url(self, context: Optional[dict]) -> int:
        url = "".join([self.url_base, self.path or ""])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        logging.info(">>url>> %s", url)
        return url


class PeopleStream(nhlStream):
    name = "people"
    parent_stream_type = TeamsStream
    path = "/people"
    primary_keys = ["id"]
    records_jsonpath = "$.people[*]"
    replication_key = None
    schema = PeopleObject.schema

    def get_url(self, context: Optional[dict]) -> int:
        url = "".join([self.url_base, self.path or ""])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        url = url + f"/{context['current_person_id']}"
        return url

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        context = context if context else {}
        decorated_request = self.request_decorator(self._request)
        for people in context["roster"]:
            person_id = people["person"]["id"]
            context["current_person_id"] = person_id
            prepared_request = self.prepare_request(context, next_page_token=None)
            resp = decorated_request(prepared_request, context)
            for row in self.parse_response(resp):
                yield row


class ShiftsStream(nhlStream):
    name = "shifts"
    parent_stream_type = ScheduleStream
    path = "/shiftcharts?cayenneExp=gameId={gameId}"
    primary_keys = ["id"]
    records_jsonpath = "$.data[*]"
    replication_key = None
    schema = ShiftsObject.schema

    def get_url(self, context: Optional[dict]) -> str:
        url_base = "https://api.nhle.com/stats/rest/en"
        url = "".join([url_base, self.path or ""])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        logging.info(">>>url>>> %s", url)
        return url
