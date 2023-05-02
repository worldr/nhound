# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Email tests.

https://red-mail.readthedocs.io/en/stable/tutorials/testing.html
"""
from unittest.mock import Mock

import pytest

from nhound.email import IEMail


@pytest.fixture()
def sut() -> IEMail:
    m_email = Mock()
    m_email.__enter__ = Mock()
    m_email.__exit__ = Mock()
    subject = "Test emails"
    sender = "test user"
    sut = IEMail(m_email, subject, sender)
    assert sut is not None
    return sut


def test_send(sut: IEMail) -> None:
    sut.send([], {})
    sut._email.send.assert_called_once()


def test_send_no_server(sut: IEMail) -> None:
    sut._email.send.side_effect = [ConnectionRefusedError]
    sut._email.__exit__.return_value = False
    ret = sut.send(["fu@bar.com"], {})
    assert ret is False
