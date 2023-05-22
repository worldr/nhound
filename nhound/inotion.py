# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Interface to Notion."""
import logging
import typing
from re import search

import pendulum
import structlog
from notion_client import APIResponseError, Client
from notion_client.helpers import collect_paginated_api, is_full_page
from pendulum.datetime import DateTime

from nhound import NOW
from nhound.cohort import Cohort
from nhound.dehumanize import dehumanize
from nhound.user import Page, User

rlog = structlog.get_logger("nhound.inotion")


class INotionError(Exception):
    """Base class for Notion errors."""


class INotion:
    """A interface to Notion's API."""

    _nhound_delimiters: typing.ClassVar[str] = "nhound{(.+?)}"

    def __init__(self, token: str, threashold: int = 13) -> None:
        """Init."""
        logger = structlog.wrap_logger(
            logging.getLogger("notion-client"),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
        )
        self._notion = Client(auth=token, logger=logger, log_level=logging.DEBUG)
        self._cohort = Cohort()
        self._nhound_default_threashold = threashold
        rlog.info("Initialized INotion", threashold=self._nhound_default_threashold)

    def get_users(self) -> None:
        """Get users."""
        rlog.debug("get_users")
        try:
            list_users_response = self._notion.users.list()
        except APIResponseError as e:
            rlog.exception(e)
            msg = "Failed to get users from Notion."
            rlog.error(msg)
            raise INotionError(msg) from e
        for item in list_users_response["results"]:  # type: ignore[index]
            if item["type"] == "person":
                self._cohort.add_user(
                    User(item["id"], item["name"], item["person"]["email"])
                )
        rlog.info("Got users from Notion", count=self._cohort.size)

    def _parse_callout_block(
        self, blocks: list[typing.Any]
    ) -> tuple[list[User], DateTime]:
        """Analyse any callout block."""
        users: list[User] = []
        threashold = NOW.subtract(weeks=self._nhound_default_threashold)
        for block in blocks:
            if block["type"] == "callout":
                for item in block["callout"]["rich_text"]:
                    if item["type"] == "mention":
                        if "user" not in item["mention"]:
                            rlog.debug("No user in callout", item=item)
                            continue
                        usr = self._cohort.get_by_uuid(item["mention"]["user"]["id"])
                        if usr is not None:
                            users.append(usr)
                        rlog.debug("Found callout user", user=usr)
                    if item["type"] == "text":
                        try:
                            # This will overwirght the standard threashold.
                            date = search(  # type: ignore [union-attr]
                                self._nhound_delimiters, item["text"]["content"]
                            ).group(  # pyright: ignore [reportOptionalMemberAccess]
                                1
                            )
                            threashold = dehumanize(date)
                            rlog.debug(
                                "Found nhoud callout date",
                                text=item["text"]["content"],
                                date=date,
                                threashold=threashold,
                            )
                        except AttributeError:
                            continue
        return (users, threashold)

    def _get_page_data(self, _id: str) -> None:
        page = self._notion.pages.retrieve(_id)
        title = "UNSET"
        try:
            title = page["url"].rsplit("/", 1)[-1].rsplit("-", 1)[0]  # type: ignore[index]
        except KeyError as e:
            rlog.exception(e)
        blocks = self._notion.blocks.children.list(_id)["results"]  # type: ignore[index]
        users, threashold = self._parse_callout_block(blocks)
        my_page = Page(
            _id,
            title,
            page.get("url"),  # type: ignore[union-attr]
            pendulum.parse(page.get("created_time")),  # type: ignore[union-attr]
            pendulum.parse(page.get("last_edited_time")),  # type: ignore[union-attr]
            threashold,
        )
        if not users:
            # We have users in the callout block.
            for user in users:
                user.pages.add(my_page)  # pyright: ignore [reportOptionalMemberAccess]
        else:
            # Wehave no users in the callout block.
            usr = self._cohort.get_by_uuid(page.get("created_by")["id"])  # type: ignore[union-attr]
            if usr is not None:
                usr.pages.add(my_page)
            usr = self._cohort.get_by_uuid(page.get("last_edited_by")["id"])  # type: ignore[union-attr]
            if usr is not None:
                usr.pages.add(my_page)

        for block in blocks:
            if block["type"] == "child_page":
                self._get_page_data(block["id"])
            if (
                block["type"] == "child_database"
                and "meeting" not in block.get("child_database").get("title").lower()
            ):
                self._get_database_data(block["id"])

    def _get_database_data(self, _id: str) -> None:
        """Get database data."""
        full_or_partial_pages = collect_paginated_api(
            self._notion.databases.query, database_id=_id
        )
        for page in full_or_partial_pages:
            if not is_full_page(page):
                continue
            title = "UNSET"
            try:
                title = page["url"].rsplit("/", 1)[-1].rsplit("-", 1)[0]
            except KeyError as e:
                rlog.exception(e)
            _tmp = Page(
                _id,
                title,
                page.get("url"),
                pendulum.parse(  # pyright: ignore [reportPrivateImportUsage]
                    page.get("created_time")
                ),
                pendulum.parse(  # pyright: ignore [reportPrivateImportUsage]
                    page.get("last_edited_time")
                ),  # pyright: ignore [reportPrivateImportUsage]
                NOW.subtract(weeks=self._nhound_default_threashold),
            )
            usr = self._cohort.get_by_uuid(page.get("created_by")["id"])
            if usr is not None:
                usr.pages.add(_tmp)
            usr = self._cohort.get_by_uuid(page.get("last_edited_by")["id"])
            if usr is not None:
                usr.pages.add(_tmp)
            rlog.info("Found a database entry", page=_tmp)

    def stuff(self, uuids: tuple[typing.Any, ...]) -> None:
        """Stuff."""
        rlog.debug("stuff start")
        self._get_users()
        self._get_pages(uuids)
        self._cohort.print_data()
        rlog.debug("stuff end")

    def _get_users(self) -> None:
        """Get all the Notion users."""
        try:
            self.get_users()
        except APIResponseError as e:
            msg = "Failed to get pages from Notion."
            rlog.error(msg)
            raise INotionError(msg) from e

    def _get_pages(self, uuids: tuple[typing.Any, ...]) -> None:
        """Get all the Notion pages."""
        for _id in uuids:
            try:
                self._get_page_data(_id)
            except APIResponseError as e:
                msg = "Failed to get page from Notion."
                rlog.error(msg, uuid=_id, error=e)
                continue

    def get_email_data(
        self, uuids: tuple[typing.Any, ...]
    ) -> list[tuple[User, list[Page]]]:
        """Get data suitable for sending emails."""
        rlog.debug("stuff start")
        self._get_users()
        self._get_pages(uuids)
        self._cohort.print_data()
        return self._cohort.get_data_for_email()
