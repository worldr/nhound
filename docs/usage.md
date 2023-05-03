# Usage

## Environment variables

As per [the 12-factor app](https://12factor.net/), `nhound` uses environment
variables as configuration. You can create a `.env` file yourself, or copy and
edit the `env-example` one. Of course, [`direnv`](https://direnv.net/)'s
`dotenv` feature is really useful, but it remains optional.

Here is what they mean:

- `NHOUND_NOTION_ADMIN_EMAIL` is the admin email for Notion.
- `NHOUND_NOTION_ADMIN_NAME` is the name of the admin for Notion.
- `NHOUND_NOTION_TOKEN` is the Notion API token. _Keep this safe!_
- `NHOUND_PAGES_ARE_STALE_AFTER_X_WEEKS` is the number of weeks after `nhound`
  will start hounding you.
- `NHOUND_PAGES_UUIDS` is a list (`JSON`) of all the page UUIDs that will be
  scanned. Those must have the `nhound` integration enabled.
- `NHOUND_SMTP_EMAIL_SENDER` is the email address the emails will come from.
- `NHOUND_SMTP_EMAIL_SUBJECT` is the subject line of the emails.
- `NHOUND_SMTP_HOST` is the SMTP relay host name.
- `NHOUND_SMTP_PORT` is the SMTP relay port number.
- `NHOUND_SMTP_USE_STARTTLS` is whether or not we use `STARTTLS`.
