# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Console entry point."""
from __future__ import annotations

import logging
import logging.config
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping  # pragma: no cover

from typing import Any

import click
import semver  # type: ignore[import]
import structlog
from click_help_colors import HelpColorsCommand  # type: ignore[import]
from rich.console import Console
from rich.prompt import Confirm
from rich.traceback import install

from nhound import __version__
from nhound.utils import (
    COLOUR_INFO,
    VersionCheck,
    check_if_latest_version,
    wprint,
)

# Rich.
install(show_locals=True)

EXIT_CODE_SUCCESS = 0
EXIT_CODE_OPERATION_FAILED = 1
EXIT_CODE_SCRIPT_FAILED = 2
EXIT_CODE_SERVICE_ACCOUNT_FAILED = 3
EXIT_CODE_YAML_DATA_FAILED = 4


pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    # Add extra attributes of LogRecord objects to the event dictionary
    # so that values passed in the extra parameter of log methods pass
    # through to log output.
    structlog.stdlib.ExtraAdder(),
]


def configure_logging(log_level: str, verbose: bool) -> None:
    """Configure all the logging."""
    # Logging levels
    # https://www.structlog.org/en/stable/_modules/structlog/_log_levels.html?highlight=log%20level  # noqa: E501
    _lvl = {
        "critical": 50,
        "error": 40,
        "warning": 30,
        "info": 20,
        "debug": 10,
        "notset": 0,
    }

    # Structlog processors. Order appears to matter…
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
    ]

    class VerboseFilter(logging.Filter):
        """Filter log entries on verbose flag."""

        def __init__(self, param: str = "") -> None:
            """Initialise."""
            self.param = param
            super()

        def filter(self, _: logging.LogRecord) -> bool:  # noqa: A003
            # We have no choice in the method's name.
            # We do not care about record thus mark it as _.
            return verbose

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,  # tabula raza.
            "filters": {
                "myfilter": {
                    "()": VerboseFilter,
                    "param": "noshow",
                }
            },
            "formatters": {
                "plain": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        *shared_processors,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,  # noqa: E501
                        structlog.processors.JSONRenderer(),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                "colored": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        *shared_processors,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,  # noqa: E501
                        structlog.dev.ConsoleRenderer(colors=True),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": _lvl[log_level],
                    "class": "logging.StreamHandler",
                    "filters": ["myfilter"],
                    "formatter": "colored",
                },
                "file": {
                    "level": _lvl[log_level],
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "nhound.log",
                    "formatter": "plain",
                },
            },
            # Define all the loggers you want!
            "loggers": {
                "nhound": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "gnupg": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "concurrent": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "plumbum": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "urllib3": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "requests": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "rich": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "asyncio": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
            },
        }
    )
    structlog.configure(
        processors=[
            *shared_processors,  # type: ignore[list-item]
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(_lvl[log_level]),
        cache_logger_on_first_use=True,
    )


class MutuallyExclusiveOption(click.Option):
    """Mutually Exclusive Option.

    This is a click option that can be used to make sure that only one
    of a
    set of options can be used at the same time.

    Note that there is no type hinting… I tried and failed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize."""
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        _help = kwargs.get("help", "")
        if self.mutually_exclusive:  # pragma: no cover
            ex_str = ", ".join(self.mutually_exclusive)
            kwargs["help"] = _help + (
                " NOTE: This argument is mutually exclusive with "
                " arguments: [" + ex_str + "]."
            )
        super().__init__(*args, **kwargs)

    def handle_parse_result(
        self, ctx: click.Context, opts: Mapping[str, Any], args: list[str]
    ) -> tuple[Any, list[str]]:
        """Handle parse result."""
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            msg = (
                f"Illegal usage: `{self.name}` is mutually exclusive with "
                f"arguments `{', '.join(self.mutually_exclusive)}`."
            )
            raise click.UsageError(msg)
        return super().handle_parse_result(ctx, opts, args)


def validate_semver(
    ctx: click.core.Context, param: click.Option, value: str
) -> Any | None:
    """Validate the option is semver compliante.

    If the option is None, do nothing.
    """
    if value is None:
        return None
    try:
        ver = semver.VersionInfo.parse(value.lstrip("v"))
    except ValueError as ex:
        # We do want to wrap `ex` in a new exception
        # so that click can handle it properly.
        rlog = structlog.get_logger("validate_semver")
        rlog.debug("Debug info.", ctx=ctx, param=param, value=value, error=ex)
        raise click.UsageError(f"{value}: {ex}") from ex  # noqa: EM102, TRY003
    else:
        return ver


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="blue",
    help_options_color="magenta",
)
@click.option(
    "-l",
    "--log-level",
    default="info",
    show_default=True,
    type=click.Choice(
        ["notset", "debug", "info", "warning", "error", "critical"],
        case_sensitive=False,
    ),
    help="Chose the logging level from the available options. "
    "This affect the file logs as well.",
)
@click.option(
    "-v", "--version", is_flag=True, help="Print the version and exit"
)
@click.option("--verbose", is_flag=True, help="Print the logs to stdout")
def main(
    log_level: str,
    version: bool,
    verbose: bool,
) -> None:
    """Setupr ships the Worldr infrastructure.

    Note that <semver> must be a valid semantic version. This is
    different for all the scripts. Please check the user documentation
    for the exact values.
    """
    # Prints the current version and exits.
    if version:
        click.echo(__version__)
        sys.exit(EXIT_CODE_SUCCESS)

    # Configure logging.
    configure_logging(log_level, verbose)
    logger = structlog.get_logger("nhound")
    logger.debug(
        "All the loggers",
        loggers=list(logging.root.manager.loggerDict),
    )

    # Configure the console.
    console = Console()
    console.rule(f"[{COLOUR_INFO}]Notion Hound bot")

    # Check latest version.
    _version_check()

    # Run commands.

    # We should be done…
    wprint("Operation was successful.", level="success")
    sys.exit(EXIT_CODE_SUCCESS)


def _version_check() -> None:
    """Check if we are running the latest verion from GitHub."""
    check = check_if_latest_version()
    if check == VersionCheck.LATEST:
        wprint(f"This is the latest version {__version__}.", level="info")
    elif check == VersionCheck.LAGGING:
        wprint(
            "there is a new version available: please update.", level="warning"
        )
        if Confirm.ask("Exit and update?", default=True):
            wprint(
                "Please run [i]python -m pip install -U nhound[/i]",
                level="info",
            )
            sys.exit(EXIT_CODE_SUCCESS)
        wprint("Proceeding with old version…", level="warning")
    elif check == VersionCheck.UNKNOWN:
        wprint("Could not check for newer versons.", level="warning")
    else:  # pragma: no cover
        # This should never, ever happen!
        wprint("This is bug, please report!", level="error")


if __name__ == "__main__":  # pragma: no cover
    main()
