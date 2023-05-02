# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""User model tests."""
import pytest

from nhound.user import User

uuid = "17ceeff0-e5a5-11ed-aa7f-2cf05d7be51f"
name = "Malenia Blade Of Miquella"
email = "malenia@haligate.tree"


@pytest.fixture()
def sut() -> User:
    return User(uuid, name, email)


def test_user_repr(sut) -> None:
    """Test the repr method.

    This includes all current properties.
    """
    assert str(sut) == (
        "User(uuid=17ceeff0-e5a5-11ed-aa7f-2cf05d7be51f, "
        "name=Malenia Blade Of Miquella, "
        "email=malenia@haligate.tree, )"
    )


def test_user_page(sut) -> None:
    x = "Test"
    sut.pages.add(x)
    sut.pages.add(x)  # Yes, we want to add it twice.
    sut.pages.add(x)  # Yes. We want to add it thrice.
    assert len(sut.pages) == 1  # This is them main we are testing.
    assert x in sut.pages
