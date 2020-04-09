"""Module for generating test data of various types, send data to Cloudwatch."""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List
from functools import lru_cache

import boto3

# from mypy_boto3 import logs
# from mypy_boto3_logs.type_defs import ClientPutLogEventsResponseTypeDef


# class LogEventResponseReal(ClientPutLogEventsResponseTypeDef):
#     ResponseMetadata: dict


@lru_cache(maxsize=None)
# def logs_client() -> logs.CloudWatchLogsClient:
def logs_client():
    return boto3.client("logs")


@lru_cache()  # type: ignore
def log_formats() -> List[str]:
    """Logging output formats"""
    return [*log_lines().logs]


@dataclass
class LogStream:
    name: str
    timestamp_ms: int


def log_stream_name() -> LogStream:
    """Generate an appropriately named log group of the format
    '{timestamp_ms}-nessus-scan'
    """
    timestamp_seconds = datetime.now().replace(tzinfo=timezone.utc).timestamp()
    timestamp_ms = int(timestamp_seconds * 1000)
    timestamp = datetime.fromtimestamp(timestamp_seconds)
    human_readable_timestamp = timestamp.strftime("%Y-%m-%d/%H-%M-%S")
    name = f"{human_readable_timestamp}-nessus-scan"
    return LogStream(name, timestamp_ms)


def create_log_stream(group_name: str) -> LogStream:
    """Create a log stream with the a name genreated by log_stream_name()"""
    log_stream = log_stream_name()
    logs_client().create_log_stream(
        logGroupName=group_name, logStreamName=log_stream.name
    )
    return log_stream


@dataclass
class CloudWatchLogResult:
    timestamp_ms: int
    log_group_name: str
    log_line: str
    log_stream_name: str
    payload: str


def send_logs_to_cloudwatch(csv_text: str) -> Dict[str, CloudWatchLogResult]:
    """Send logs to Cloudwatch, creating a new logstream for those events"""

    group_name = "/gds/nessus-data"
    stream = create_log_stream(group_name)

    logs_client().put_log_events(
        logGroupName=group_name,
        logStreamName=stream.name,
        logEvents=[{"timestamp": stream.timestamp_ms, "message": csv_text}],
    )