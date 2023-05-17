# Usage

## On the Notion side

### Setup integration

First, head to the Notion page you want `nhound` to hound you about.

On the top right, there is a ellipse. Clicking on it will reveal a menu. At the
bottom of the menu, there is a Connections section. Click `+ Add Connection` and
add the `nhound` integration.

Note that _all the sub pages of this page will be automatically added to the
integration_. Hopefully, this is something you wanted to do. If not, you can
disable it on sub pages you do not want to be added.

All pages without the integration enabled cannot be scanned.

### Callout

![A callout example.](./docs/assets/callout-example.png)

Each page is automatically scanned and the creator and last person who edited it
being hounded by the default time — set with
`NHOUND_PAGES_ARE_STALE_AFTER_X_WEEKS`.

If this is not what you want, you can create a special callout block.

The formate of this is

- One or more `@user` mentions. These are the users that `nhound` will hound.
- a block `nhound{}` with a duration within. This is the time that has to elapse
  before `nhound` sends messages.
- The during should look something like
  `[a]|[1-9]+ [day[s]?|month[s]?|year[s]?]`. For example:
  - `5 days`
  - `3 weeks`
  - `1 month`
  - `a year`
  - …

## On the runner side

### Runner

### cron

Running `nhound` as part of cron (or cron like) is recommended.

`nhound` should be run at least once per minimal duration set in callouts.
Sadly, it cannot tell that those will be. However, those cannot be less than a
day. Therefore, once a day seems like a reasonable guess.

### Test

It is recommended to test this on just one page (and sub pages) for a start.
Just have a look at the development Tl;DR section.

### Environment variables configuration

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
