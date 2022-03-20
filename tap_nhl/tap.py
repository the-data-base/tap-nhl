"""nhl tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

# import stream types
from tap_nhl.streams import (
    ConferencesStream,
    SeasonsStream,
    ScheduleStream,
    LivePlaysStream,
    LiveLinescoreStream,
    LiveBoxscoreStream,
    TeamsStream,
    PeopleStream,
    DivisionsStream,
    DraftStream,
    DraftProspectsStream,
)

STREAM_TYPES = [
    ConferencesStream,
    ScheduleStream,
    SeasonsStream,
    LivePlaysStream,
    LiveLinescoreStream,
    LiveBoxscoreStream,
    TeamsStream,
    PeopleStream,
    DivisionsStream,
    DraftStream,
    DraftProspectsStream,
]


class Tapnhl(Tap):
    """nhl tap class."""
    name = "tap-nhl"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync"
        ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://api.mysample.com",
            description="The url for the API service"
        ),
        th.Property("stream_maps", th.ObjectType()),
        th.Property("stream_map_config", th.ObjectType())
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
