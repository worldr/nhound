# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Dehumanize a date string."""
import string
from typing import Any

import structlog

from nhound import NOW

rlog = structlog.get_logger("nhound.dehumanize")


def dehumanize(text: str) -> Any:
    """Dehumanize a date string."""
    # Clean up the input text.
    text = text.lower().translate(str.maketrans("", "", string.punctuation))

    # Try to split into value and unit.
    try:
        span, unit = text.split(" ")
    except ValueError as e:
        rlog.exception(e)
        rlog.error("Failed to parse humanized text", text=text)
        return NOW

    # Value must be an interger.
    try:
        value = int(span)
    except ValueError as e:
        if span == "a":
            value = 1
        else:
            rlog.exception(e)
            rlog.error("Failed to cast span of humanized text", text=text, span=span)
            return NOW

    # Parse the unit.
    if unit in ["day", "days"]:
        return NOW.subtract(days=int(value))
    if unit in ["week", "weeks"]:
        return NOW.subtract(weeks=int(value))
    if unit in ["month", "months"]:
        return NOW.subtract(months=int(value))
    if unit in ["year", "years"]:
        return NOW.subtract(years=int(value))

    # Default is now.
    return NOW
