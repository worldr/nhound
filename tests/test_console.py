# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from nhound import __version__
from nhound.console import main
from nhound.utils import VersionCheck


def create_env() -> None:
    root = Path(__file__).parent.parent
    dst = root / ".env"
    if not dst.exists():  # pragma: no cover
        # We do not need to worry about this in normal user testing.
        # CI will need this code to work as there is no default .env file commited.
        src = root / "env-example"
        assert src.exists()
        dst.write_text(src.read_text())


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "Setupr ships the Worldr infrastructure" in result.output


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_env()
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
@patch("nhound.console._do_stuff")
def test_nhound_version_status(m_stuff, ask, check):
    with patch("nhound.console.check_if_latest_version") as mock_check, patch(
        "nhound.console.Confirm.ask"
    ) as mock_ask:
        mock_ask.return_value = ask
        mock_check.return_value = check
        m_stuff.return_value = ask  # This is a gross above of the ask variable!

        runner = CliRunner()
        result = runner.invoke(main, ["--verbose"])

        assert result is not None
