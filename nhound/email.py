# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.id
"""Email sending module."""
import structlog
from redmail import EmailSender  # pyright: ignore [reportPrivateImportUsage]

from nhound.user import Page

rlog = structlog.get_logger("nhound.email")


class IEMail:
    """Interface for email."""

    # Template for email body in HTML format.
    html = """
        <h1>Hi {{ name }},</h1>
        <p>The following Notion page(s) require your attension:</p>
        <dl>
        {% for page in pages %}
            <dt>{{ page.title }}</dt>
            <dd>{{ page.url }}</dd>
        {% endfor %}
        </dl>
        <p>Either update them or archive them!</p>

        <p>Thank you.</p>

        <p>Nhound bot.</p>
    """

    # Template for email body in text format.
    text = """
        Hi {{ name }},

        The following Notion page(s) require your attension:
        {% for page in pages %}
            - {{ page.title }} ({{ page.url }})
        {% endfor %}

        Either update them or archive them!

        Thank you.

        Nhound bot.
        {{ company }}
    """

    def __init__(self, email: EmailSender, subject: str, sender: str) -> None:
        """Initialize."""
        self._email = email
        self._subject = subject
        self._sender = sender

    def send(self, receivers: list, body_params: dict[str, str | list[Page]]) -> bool:
        """Send email."""
        try:
            with self._email:
                self._email.send(
                    subject=self._subject,
                    sender=self._sender,
                    receivers=receivers,
                    text=self.text,
                    html=self.html,
                    body_params=body_params,
                )
        except ConnectionRefusedError as e:
            rlog.error(
                "Failed to send email",
                error=e,
                host=self._email.host,
                port=self._email.port,
                receivers=receivers,
            )
            return False
        else:
            return True
