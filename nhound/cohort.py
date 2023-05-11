# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""A cohort of Notion users."""
import os
from contextlib import suppress

import pendulum
import structlog
from rich import print as rprint

from nhound import NOW
from nhound.user import Page, User
from nhound.utils import wprint

rlog = structlog.get_logger("nhound.cohort")


class Cohort:
    """A collection of users."""

    def __init__(self) -> None:
        """Init.

        We care just the day, we care not about specific times.
        """
        self._users = {}  # type: dict[str, User]
        self.now = pendulum.datetime(NOW.year, NOW.month, NOW.day)
        _interval = 13  # Default to 13 weeks, or 3 months, ish.
        with suppress(ValueError):
            _interval = int(
                os.environ.get("NHOUND_PAGES_ARE_STALE_AFTER_X_WEEKS", f"{_interval}")
            )
        self.stale = NOW.subtract(weeks=_interval)

    @property
    def size(self) -> int:
        """Get size."""
        return len(self._users)

    def add_user(self, user: User) -> None:
        """Add user."""
        if user.uuid in self._users:
            msg = f"User with uuid {user.uuid} already exists"
            rlog.warning(msg)
            raise ValueError(msg)
        self._users[user.uuid] = user

    def get_by_uuid(self, uuid: str) -> User | None:
        """Get user by its uuid.

        This is unique.
        """
        try:
            return self._users[uuid]
        except KeyError:
            msg = f"User with uuid {uuid} not found"
            rlog.warning(msg)
            return None

    def get_by_name(self, name: str) -> tuple[User, ...]:
        """Get user by thier name.

        This is not unique.
        """
        results = []
        for _, user in self._users.items():
            if user.name == name:
                results.append(user)
        return tuple(results)

    def get_by_email(self, email: str) -> tuple[User, ...]:
        """Get user by thier email.

        This is not unique.
        """
        results = []
        for _, user in self._users.items():
            if user.email == email:
                results.append(user)
        return tuple(results)

    def print_data(self) -> None:  # pragma: no cover
        """Bleurgh.

        There is no unit test here since, in all likelyhood, this will
        never be used as is.
        """
        for uuid, user in self._users.items():
            if user.pages:
                rprint(f"{uuid} {user.name} → ")
                for page in user.pages:
                    if page.last_edited_time < page.threashold_time:
                        wprint(
                            f"{page.title} is stale, "
                            f"it was editted {page.last_edited_time.diff_for_humans(NOW)} now. "
                            f"<{page.url}>",
                            level="warning",
                        )
                    else:
                        wprint(f"{page.title} is fresh.", level="info")

    def get_data_for_email(self) -> list[tuple[User, list[Page]]]:
        """Get all the data in a format email can understand."""
        ret = []
        for _, user in self._users.items():
            pages = [x for x in user.pages if x.last_edited_time < x.threashold_time]
            if pages:
                ret.append((user, pages))
        return ret
