# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from nhound import __version__
from nhound.console import main
from nhound.utils import VersionCheck


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "Setupr ships the Worldr infrastructure" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0, f"CLI output: {result.output}"
    assert __version__ in result.output


@pytest.mark.parametrize(
    ("ask", "check"),
    [
        (True, VersionCheck.LATEST),
        (True, VersionCheck.UNKNOWN),
        (True, VersionCheck.LAGGING),
        (False, VersionCheck.LAGGING),
    ],
)
@patch("nhound.console.INotion")
def test_nhound_version_status(get_m_inotion, ask, check):
    with patch("nhound.console.check_if_latest_version") as mock_check, patch(
        "nhound.console.Confirm.ask"
    ) as mock_ask:
        mock_ask.return_value = ask
        mock_check.return_value = check

        runner = CliRunner()
        result = runner.invoke(main, ["--verbose"])

        assert result is not None
        assert not get_m_inotion.called
