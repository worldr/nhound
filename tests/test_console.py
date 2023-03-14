# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
from click.testing import CliRunner

from nhound import __version__
from nhound.console import main


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "Setupr ships the Worldr infrastructure" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0, f"CLI output: {result.output}"
    assert __version__ in result.output
