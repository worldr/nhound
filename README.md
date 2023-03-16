# nhound

<img src="https://github.com/worldr/nhound/blob/main/docs/assets/logo.png" width=25% height=25% >

[![PyPi status](https://img.shields.io/pypi/status/Setupr)](https://img.shields.io/pypi/status/Setupr)
[![PyPi version](https://img.shields.io/pypi/v/nhound)](https://img.shields.io/pypi/v/nhound)
[![PyPi python versions](https://img.shields.io/pypi/pyversions/Setupr)](https://img.shields.io/pypi/pyversions/Setupr)
[![PyPi downloads](https://img.shields.io/pypi/dm/nhound)](https://img.shields.io/pypi/dm/Setupr)

[![Release](https://img.shields.io/github/v/release/worldr/nhound)](https://img.shields.io/github/v/release/worldr/nhound)
[![Build status](https://img.shields.io/github/actions/workflow/status/worldr/nhound/codeql.yml?branch=main)](https://img.shields.io/github/actions/workflow/status/worldr/nhound/codeql.yml?branch=main)
[![Commit activity](https://img.shields.io/github/commit-activity/m/worldr/nhound)](https://img.shields.io/github/commit-activity/m/worldr/nhound)
[![Code style with black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports with isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

---

## Documentation

- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Development](docs/development.md)

---

## What is this?

How to keep content on Notion up to date and avoid rot?

The answer is with `nhound`, you can. It's a bot. It will hound (aka nag) the
authors of pages on Notion to keep those pages up to date.

## Features

### Main Features

This is a feature list for version 1.

- [ ] Reads all the pages on Notion via the API.
- [ ] By default, it sets a reminder to the owner every 3 months.
      [Redis](https://pypi.org/project/redis/)?
- [ ] By default, it picks either the last person who edited the page or its
      creator.
- [ ] Reminder template.
- [ ] Notifications are sent via email.
- [ ] If there is `/callout` block,
  - [ ] Pick the owners from that block only.
  - [ ] Owners can override this time (1w, 6m, whatever), the bot will use that.
- [ ] If there is either no owner or the owner is no longer on Notion, it whines
      at the admins.

The bot runs once per day. This is a DevOps problem…

### Stretch goals

- [ ] Notifications are sent as Notion notifications. Is this possible?
- [ ] Notifications are sent to Slack.
- [ ] Notifications are sent to Microsoft Teams.
- [ ] Random elements in the message template to make it more
      fun[⸮](https://en.wikipedia.org/wiki/Irony_punctuation)
