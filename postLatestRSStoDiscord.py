#!/usr/bin/env python3
# Brian Ballsun-Stanton GPL V3.
# Designed to be used with github actions. Take an environment variable of
#   a JSON list of RSS-compatible feeds, an environment variable of
#   "within duration", and post as embeds to a Discord webhook in an env.

# cSpell:words dotenv
from dotenv import load_dotenv

import os
import logging
import json
from pprint import pformat
from datetime import datetime
from dateutil.tz import tzutc
import discord

# cSpell:words dateutil relativedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser

import feedparser

# cSpell:words levelname
FORMAT = (
    "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

# Setup environment
load_dotenv()  # take environment variables from .env.


def load_env():
    """Load environment variables and prepare them as needed."""
    keys = {
        "WEBHOOK_URL": os.getenv("WEBHOOK_URL"),
        "PAST_DURATION_HOURS": relativedelta(
            hours=int(os.getenv("PAST_DURATION_HOURS"))
        ),
        "RSS_LIST": json.loads(os.getenv("RSS_LIST")),
        "MESSAGE": os.getenv("MESSAGE"),
    }

    logging.debug(f"{pformat(keys)=}")
    return keys


def fetch_rss_feed(feed_url, relative_hours_cutoff=None, max_items=1):
    """Fetch items from an rss feed, with either a relative hours cutoff
    and limit by maximum number of items"""
    feed = feedparser.parse(feed_url)
    returned_items = []
    for entry in feed["entries"]:
        entry["localtime"] = parser.parse(entry["published"])
        if relative_hours_cutoff and entry[
            "localtime"
        ] + relative_hours_cutoff >= datetime.now(tzutc()):
            logging.debug(f"{entry['title']=}\t{entry['localtime']=}\t{entry['link']=}")
            returned_items.append({"title": entry["title"], "link": entry["link"]})
    logging.info(f"Found: {returned_items}")
    return returned_items[:max_items]


def post_to_discord(item, message, webhook):
    """Posts the linked item to discord, prepended by message"""
    title = item["title"]
    link = item["link"]
    # https://discordpy.readthedocs.io/en/stable/api.html#discord.SyncWebhook.send

    webhook.send(content=f"{message} {title} {link}")


def main():
    ENV = load_env()
    # cspell:words syncwebhook
    webhook = discord.SyncWebhook.from_url(ENV["WEBHOOK_URL"])
    logging.debug(webhook)
    for feed_url in ENV["RSS_LIST"]:
        items = fetch_rss_feed(
            feed_url, relative_hours_cutoff=ENV["PAST_DURATION_HOURS"]
        )
        for item in items:
            post_to_discord(item, ENV["MESSAGE"], webhook)


if __name__ == "__main__":
    main()
