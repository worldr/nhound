# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Simple Notion user model."""
from collections import namedtuple

import structlog

rlog = structlog.get_logger("nhound.user")

Page = namedtuple(
    "Page",
    [
        "uuid",
        "title",
        "url",
        "created_time",
        "last_edited_time",
        "threashold_time",
    ],
)


class User:
    """A Notion user model."""

    def __init__(self, uuid: str, name: str, email: str) -> None:
        """Init."""
        self._uuid = uuid
        self._name = name
        self._email = email
        self.pages: set[Page] = set()

    def __repr__(self) -> str:
        """Repr."""
        return (
            f"User("
            f"uuid={self.uuid}, "
            f"name={self.name}, "
            f"email={self.email}, "
            ")"
        )

    @property
    def uuid(self) -> str:
        """Get uuid."""
        return self._uuid

    @property
    def name(self) -> str:
        """Get name."""
        return self._name

    @property
    def email(self) -> str:
        """Get email."""
        return self._email
