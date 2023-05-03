# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Email tests.

https://red-mail.readthedocs.io/en/stable/tutorials/testing.html
"""
from unittest.mock import Mock

import pendulum
import pytest

from nhound.email import IEMail
from nhound.user import Page

fake_page = Page(
    "uuid", "fake title", "http://fake.com", pendulum.now("UTC"), pendulum.now("UTC")
)


@pytest.fixture()
def sut() -> IEMail:
    m_email = Mock()
    m_email.__enter__ = Mock()
    m_email.__exit__ = Mock()
    sender = "test user"
    sut = IEMail(m_email, sender)
    assert sut is not None
    return sut


def test_send_no_need(sut: IEMail) -> None:
    sut.send([], {"pages": []})
    assert not sut._email.send.called


def test_send_no_server(sut: IEMail) -> None:
    sut._email.send.side_effect = [ConnectionRefusedError]
    sut._email.__exit__.return_value = False
    ret = sut.send(["fu@bar.com"], {"pages": [fake_page]})
    assert ret is False


def test_send_email(sut: IEMail) -> None:
    ret = sut.send(["fu@bar.com"], {"pages": [fake_page, fake_page]})
    assert ret is True
    assert sut._email.send.called
