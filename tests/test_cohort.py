# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Cohort tests."""
import os
from unittest.mock import patch

import pendulum
import pytest

from nhound.cohort import NOW, Cohort
from nhound.user import Page, User

uuid = "17ceeff0-e5a5-11ed-aa7f-2cf05d7be51f"
name = "Malenia Blade Of Miquella"
email = "malenia@haligate.tree"
usr = User(uuid, name, email)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", 13),  # Variable is empty.
        ("7", 7),  # Variable is correctly set, below the default.
        ("53", 53),  # Variable is correctly set, above the default.
        ("SeVeN", 13),  # Variable is nonesense.
    ],
)
def test_cohort_stale(value, expected) -> None:
    with patch.dict(os.environ, {"NHOUND_PAGES_ARE_STALE_AFTER_X_WEEKS": value}):
        sut = Cohort()
        date = pendulum.now("UTC").subtract(weeks=expected)
        assert sut.stale.year == date.year
        assert sut.stale.month == date.month
        assert sut.stale.day == date.day


@pytest.fixture()
def sut() -> Cohort:
    sut = Cohort()
    sut.add_user(usr)
    assert len(sut._users) == 1
    return sut


def test_cohort_time(sut) -> None:
    assert sut.now.year == NOW.year
    assert sut.now.month == NOW.month
    assert sut.now.day == NOW.day


def test_cohort_add_user(sut) -> None:
    with pytest.raises(ValueError, match=f"User with uuid {uuid} already exists"):
        assert sut.add_user(usr) is None


def test_cohort_size(sut) -> None:
    assert sut.size == 1


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        (uuid, usr),
        ("", None),
    ],
)
def test_cohort_get_by_uuid(sut, key, expected) -> None:
    assert sut.get_by_uuid(key) == expected


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        (name, (usr,)),
        ("", ()),
    ],
)
def test_cohort_get_by_name(sut, key, expected) -> None:
    assert sut.get_by_name(key) == expected


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        (email, (usr,)),
        ("", ()),
    ],
)
def test_cohort_get_by_email(sut, key, expected) -> None:
    assert sut.get_by_email(key) == expected


def test_get_data_for_email_nothing(sut) -> None:
    assert sut.get_data_for_email() == []


def test_get_data_for_email_has_pages() -> None:
    sut = Cohort()
    old = sut.stale.subtract(months=13)
    new = sut.stale.add(months=13)
    page = Page("UUID", "TITLE", "URL", old, old, sut.stale)
    usr.pages.add(page)
    usr.pages.add(Page("UUID", "TITLE", "URL", new, new, sut.stale))
    sut.add_user(usr)
    assert sut.get_data_for_email() == [
        (usr, [page]),
    ]
