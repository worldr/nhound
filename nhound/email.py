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
<p>The following {{pages|length}} Notion page{% if pages|length > 1 %}s{% endif %} require your attention:</p>
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

The following {{pages|length}} Notion pages{% if pages|length > 1 %}s{% endif %}require your attention:
{% for page in pages %}
    - {{ page.title }} -- {{ page.url }}.
{% endfor %}

Either update them or archive them!

Thank you.

Nhound bot.
{{ company }}
    """

    def __init__(self, email: EmailSender, sender: str) -> None:
        """Initialize."""
        self._email = email
        self._sender = sender

    def send(self, receivers: list, body_params: dict[str, str | list[Page]]) -> bool:
        """Send email."""
        sz = len(body_params["pages"])
        if sz == 0:
            return True
        subject = f"{sz} Notion pages requires your attention"
        if sz == 1:
            subject = f"{sz} Notion page requires your attention"
        try:
            with self._email:
                self._email.send(
                    subject=subject,
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
