#!/usr/bin/env python3
# Due to complexity of environment variables, need to POST from python instead of bash
# Brian Ballsun-Stanton. GPL v3

from dotenv import load_dotenv
import requests
from pprint import pprint
import os
import logging
import contextlib
import json

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

"""
curl \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>"\
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/dispatches \
  -d '{"event_type":"on-demand-test","client_payload":{"unit":false,"integration":true}}'
"""
# Setup environment
load_dotenv()  # take environment variables from .env.


def load_env():
    """Load environment variables and prepare them as needed."""
    keys = {
        "GITHUB_URL": f"https://api.github.com/repos/{os.getenv('GITHUB_REPO_OWNER')}/{os.getenv('GITHUB_REPO_NAME')}/dispatches",
        "GITHUB_TOKEN": os.getenv("GITHUB_ACCESS_TOKEN"),
        "EPUB_URL": os.getenv("EPUB_URL"),
        "EPUB_TITLE": os.getenv("EPUB_TITLE"),
        "EPUB_CONTENT": os.getenv("EPUB_CONTENT"),
    }

    for key in keys:
        print(f"{key} {keys[key]}")
    return keys


def main():
    ENV = load_env()
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {ENV['GITHUB_TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    # Getting event type from .github/workflows/epub-from-webhook
    # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event
    data = {
        "event_type": "generate_epub",
        "client_payload": {
            "url": ENV["EPUB_URL"],
            "title": ENV["EPUB_TITLE"],
            "content": ENV["EPUB_CONTENT"],
        },
    }
    pprint(headers)
    pprint(data)
    r = requests.post(ENV["GITHUB_URL"], headers=headers, data=json.dumps(data))

    pprint(r)

    # print(r.json()["message"])


if __name__ == "__main__":
    main()
