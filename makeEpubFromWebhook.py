#!/usr/bin/env python3
# Take an environment variable and turn it into an epub.
# Specifically, assume the environment var webhook_content contains
# the data from "testWebhookContent.json" Output an epub where the
# filename and title are from data.attributes.title, and the content
# is from data.attributes.content
#
# Brian Ballsun-Stanton. GPL v3.

from ebooklib import epub

# cSpell:words dotenv
from dotenv import load_dotenv
from pprint import pformat
from slugify import slugify

import os
import logging
import json
import discord

# cSpell:words levelname
FORMAT = (
    "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

# Setup environment
load_dotenv()  # take environment variables from .env.

# We care about the EPUB_ vars EPUB_LANGUAGE EPUB_AUTHOR EPUB_TITLE_PREFIX EPUB_WEBHOOK


def load_env():
    """Load environment variables and prepare them as needed."""
    keys = {
        "EPUB_LANGUAGE": os.getenv("EPUB_LANGUAGE"),
        "EPUB_AUTHOR": os.getenv("EPUB_AUTHOR"),
        "EPUB_TITLE_PREFIX": os.getenv("EPUB_TITLE_PREFIX"),
        "EPUB_URL": os.getenv("EPUB_URL"),
        "EPUB_TITLE": os.getenv("EPUB_TITLE"),
        "EPUB_CONTENT": os.getenv("EPUB_CONTENT"),
        "DISCORD_WEBHOOK_URL": os.getenv("WEBHOOK_URL"),
        "DISCORD_MESSAGE": os.getenv("MESSAGE"),
    }
    logging.debug(f"{keys['EPUB_AUTHOR']=}")
    logging.debug(f"{keys['EPUB_URL']=}")
    logging.debug(f"{keys['EPUB_TITLE']=}")
    return keys


def make_book(identifier, title_prefix, language, author, title, contents):
    """Takes in necessary data and metadata, writes an epub to disk, returns filename"""
    book = epub.EpubBook()

    # EPUB has some minimal metadata requirements which you need to fulfil.
    # You need to define unique identifier, title of the book and language used inside.
    # When it comes to language code recommended best practice is to use a controlled
    # vocabulary such as RFC 4646 - http://www.ietf.org/rfc/rfc4646.txt.

    book.set_identifier(identifier)
    book.set_title(f"{title_prefix}{title}")
    book.set_language(language)
    book.add_author(author)

    chapter = epub.EpubHtml(title=title, file_name="chapter.xhtml", lang=language)
    chapter.set_content(
        f'<html><head><link rel="stylesheet" href="style/style.css"></head><body class="c5 doc-content"><h1>{title}</h1>{contents}</body></html>'
    )
    css = 'ol{margin:0;padding:0}table td,table th{padding:0}.c1{color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:11pt;font-family:"Arial";font-style:normal}.c2{padding-top:0pt;padding-bottom:10pt;line-height:1.15;orphans:2;widows:2;text-align:left}.c4{padding-top:0pt;padding-bottom:10pt;line-height:1.15;orphans:2;widows:2;text-align:center}.c5{background-color:#ffffff}.c3{height:11pt}.c0{font-style:italic}.title{padding-top:0pt;color:#000000;font-size:26pt;padding-bottom:3pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}.subtitle{padding-top:0pt;color:#666666;font-size:15pt;padding-bottom:16pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}li{color:#000000;font-size:11pt;font-family:"Arial"}p{margin:0;color:#000000;font-size:11pt;font-family:"Arial"}h1{padding-top:20pt;color:#000000;font-size:20pt;padding-bottom:6pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h2{padding-top:18pt;color:#000000;font-size:16pt;padding-bottom:6pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h3{padding-top:16pt;color:#434343;font-size:14pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h4{padding-top:14pt;color:#666666;font-size:12pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h5{padding-top:12pt;color:#666666;font-size:11pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h6{padding-top:12pt;color:#666666;font-size:11pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;font-style:italic;orphans:2;widows:2;text-align:left}'
    ebook_css = epub.EpubItem(
        uid="book_css", file_name="style/style.css", media_type="text/css", content=css
    )
    book.add_item(ebook_css)
    book.add_item(chapter)
    # book.toc = epub.Link("chapter.xhtml", title, "chapter")
    book.spine = [chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    filename = f"{slugify(title_prefix)}-{slugify(title)}.epub"
    epub.write_epub(filename, book)
    return filename


def post_to_discord(title, link, message, webhook, filename):
    """Posts the webhook'd item to discord, prepended by message"""

    # https://discordpy.readthedocs.io/en/stable/api.html#discord.SyncWebhook.send

    # Note that epub doesn't write to a buffer, so we now need to read in the filename
    with open(filename, mode="rb") as epub_file:
        chapter_epub = discord.File(fp=epub_file, filename=filename, description=title)

        webhook.send(
            content=f"{message} {title} https://patreon.com{link}", file=chapter_epub
        )


def main():
    ENV = load_env()
    filename = make_book(
        identifier=ENV["EPUB_URL"],
        title_prefix=ENV["EPUB_TITLE_PREFIX"],
        language=ENV["EPUB_LANGUAGE"],
        author=ENV["EPUB_AUTHOR"],
        title=ENV["EPUB_TITLE"],
        contents=ENV["EPUB_CONTENT"],
    )
    webhook = discord.SyncWebhook.from_url(ENV["DISCORD_WEBHOOK_URL"])
    post_to_discord(
        title=f"{ENV['EPUB_TITLE_PREFIX']}{ENV['EPUB_TITLE']}",
        link=ENV["EPUB_URL"],
        message=ENV["DISCORD_MESSAGE"],
        webhook=webhook,
        filename=filename,
    )


if __name__ == "__main__":
    main()
