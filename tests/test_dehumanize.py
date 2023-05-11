# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Test suite for reversing humanize strings."""
# pyright: reportGeneralTypeIssues=false
from unittest.mock import patch

import pendulum
import pytest

from nhound.dehumanize import dehumanize

_now = pendulum.parse(  # pyright: ignore [reportPrivateImportUsage]
    "2077-05-21T22:00:00",
    tz="UTC",
)


@pytest.mark.parametrize(
    ("humanized", "expected"),
    [
        ("", _now),
        ("something wrong", _now),
        ("WrOnG", _now),
        ("a things-that-should-not-be", _now),
        ("things that should not be", _now),
        ("Now!", _now),
        ("?Now.", _now),
        ("now", _now),
        ("a day", _now.subtract(days=1)),
        ("3 days", _now.subtract(days=3)),
        ("53 days", _now.subtract(days=53)),
        ("a week", _now.subtract(weeks=1)),
        ("7 weeks", _now.subtract(weeks=7)),
        ("63 weeks", _now.subtract(weeks=63)),
        ("a month", _now.subtract(months=1)),
        ("11 months", _now.subtract(months=11)),
        ("101 months", _now.subtract(months=101)),
        ("a year", _now.subtract(years=1)),
        ("13 years", _now.subtract(years=13)),
        ("666 years", _now.subtract(years=666)),
    ],
)
@patch("nhound.dehumanize.NOW", _now)
def test_dehumanize(humanized, expected) -> None:
    assert dehumanize(humanized) == expected
