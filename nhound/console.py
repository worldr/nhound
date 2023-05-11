# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Console entry point."""
from __future__ import annotations

import logging
import logging.config
import os
import sys
from pathlib import Path

import click
import pendulum
import structlog
from click_help_colors import HelpColorsCommand  # type: ignore[import]
from dotenv import load_dotenv
from orjson import loads
from redmail import EmailSender, gmail  # pyright: ignore [reportPrivateImportUsage]
from rich.console import Console
from rich.prompt import Confirm
from rich.traceback import install

from nhound import __version__
from nhound.email import IEMail
from nhound.inotion import INotion, INotionError
from nhound.utils import COLOUR_INFO, VersionCheck, check_if_latest_version, wprint

# Rich.
install(show_locals=True)

EXIT_CODE_SUCCESS = 0
EXIT_CODE_OPERATION_FAILED = 1
EXIT_CODE_NOTION_API_FAILED = 2


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
    # https://www.structlog.org/en/stable/_modules/structlog/_log_levels.html?highlight=log%20level
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
            #
            # The pragam no cover can be removed once we actually use
            # something useful.
            return verbose  # pragma: no cover

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
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.JSONRenderer(),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                "colored": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        *shared_processors,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
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
    "-e",
    "--env",
    default=Path(Path.cwd() / ".env"),
    show_default=True,
    type=click.Path(exists=True),
    help="Which .env file to load.",
)
@click.option("-v", "--version", is_flag=True, help="Print the version and exit")
@click.option("--verbose", is_flag=True, help="Print the logs to stdout")
def main(
    log_level: str,
    env: Path,
    version: bool,
    verbose: bool,
) -> None:
    """Setupr ships the Worldr infrastructure.

    Note that <semver> must be a valid semantic version. This is
    different for all the scripts. Please check the user documentation
    for the exact values.
    """
    # Start time.
    start_time = pendulum.now("UTC")

    # Prints the current version and exits.
    if version:
        click.echo(__version__)
        sys.exit(EXIT_CODE_SUCCESS)

    # Configure logging.
    configure_logging(log_level, verbose)
    rlog = structlog.get_logger("nhound")
    rlog.debug(
        "All the loggers",
        loggers=list(logging.root.manager.loggerDict),
    )

    # Configure the console.
    console = Console()
    console.rule(f"[{COLOUR_INFO}]Notion Hound bot")

    # Check latest version.
    _version_check()

    # Do all the hard work.
    rlog.debug("Starting real work…")
    status = _do_stuff(rlog, env)

    # We should be done…
    if status:
        wprint("Operation was successful.", level="success")
    else:
        wprint("Operation might have failed.", level="warning")
    rlog.info(
        "That's all folks!",
        duration=(
            pendulum.now("UTC") - start_time
        ).in_words(),  # pyright: ignore[reportGeneralTypeIssues]
    )
    sys.exit(EXIT_CODE_SUCCESS)


def _do_stuff(rlog: structlog.BoundLogger, env: Path) -> bool:  # pragma: no cover
    """Do stuff.

    Why not unit tests? Well, this is actually doing work. We could mock
    everything, but is there a point to doing that?

    A functional tests might be better. Again, it would not be trivial
    to set up.
    """
    # Get enviorment variables from .env file.
    rlog.debug("Loading environment variables from .env file.", env=env)
    load_dotenv(env)  # take environment variables from .env.
    token = ""  # There should never be a real value here.  # nosec
    try:
        token = os.environ["NHOUND_NOTION_TOKEN"]
    except KeyError as e:
        rlog.exception("Missing environment variable", var=e)
        wprint("Missing environment variable NHOUND_NOTION_TOKEN.", level="error")
        sys.exit(EXIT_CODE_OPERATION_FAILED)

    # Get UUID of Notion pages from environment variable.
    uuids = loads(os.environ["NHOUND_PAGES_UUIDS"])

    # Set up email forwarding.
    #
    # Note that if NHOUND_SMTP_USERNAME and NHOUND_SMTP_PASSWORD are not set,
    # then the email will be sent without authentication.
    my_sender = EmailSender(
        host=os.environ["NHOUND_SMTP_HOST"],
        port=int(os.environ["NHOUND_SMTP_PORT"]),
        use_starttls=os.environ["NHOUND_SMTP_USE_STARTTLS"].lower().capitalize()
        is False,
    )
    if os.getenv("NHOUND_SMTP_USERNAME", None):
        rlog.info("Using Google SMTP server.")
        gmail.username = os.environ["NHOUND_SMTP_USERNAME"]
        gmail.password = os.environ["NHOUND_SMTP_PASSWORD"]
        my_sender = gmail
    else:
        rlog.warning("Using custom SMTP server. Probably testing…")
        rlog.warning("Run: `python -m smtpd -n -c DebuggingServer localhost:1025`")

    email = IEMail(my_sender, os.environ["NHOUND_SMTP_EMAIL_SENDER"])

    # Do stuff with Notion API.
    status = True
    try:
        inotion = INotion(
            token,
            int(os.getenv("NHOUND_PAGES_ARE_STALE_AFTER_X_WEEKS", 13)),
        )
        for data in inotion.get_email_data(uuids):
            status = status & email.send(
                receivers=[
                    data[0].email,
                ],
                body_params={"name": data[0].name, "pages": data[1]},
            )
    except INotionError as e:
        rlog.exception("INotionError", error=e)
        sys.exit(EXIT_CODE_NOTION_API_FAILED)

    if not status:
        wprint("Email sending failed.", level="warning")
        return False
    return True


def _version_check() -> None:
    """Check if we are running the latest verion from GitHub."""
    check = check_if_latest_version()
    if check == VersionCheck.LATEST:
        wprint(f"This is the latest version {__version__}.", level="info")
    elif check == VersionCheck.LAGGING:
        wprint("there is a new version available: please update.", level="warning")
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
