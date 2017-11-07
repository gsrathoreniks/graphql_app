#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import json
import os

__VERSION__ = "0.0.6"

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
if GITHUB_API_TOKEN is None:
    print("""
    To communicate with Github GraphQL server, you'll need an OAuth token with the right scopes.

    Please set your personal access token to request.

    export GITHUB_API_TOKEN="<your token here>"

    - Creating a personal access token for the command line
    https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/
    """)
    exit(0)


def cli(args):
    if args.version:
        print(__VERSION__)
        return

    first_num = args.count
    qs = ["sort:stars", "stars:>1"]
    if args.repo:
        qs += [args.repo]
    if args.lang:
        qs += ["language:" + args.lang]

    if args.new_created:
        from datetime import datetime, timedelta
        qs += ["created:>={:%Y-%m-%d}".format(datetime.now() + timedelta(weeks=-1))]
    if args.new_pushed:
        from datetime import datetime, timedelta
        qs += ["pushed:>={:%Y-%m-%d}".format(datetime.now() + timedelta(weeks=-1))]
    
    if args.verbose:
        print(qs)
    query = """
query {
  search(type: REPOSITORY, query: "%s", first: %d) {
    userCount
    edges {
      node {
        ... on Repository {
          name
          description
          stargazers {
            totalCount
          }
          url
        }
      }
    }
  }
}
    """ % (" ".join(qs), first_num)

    if args.verbose:
        print(query)

    req = Request("https://api.github.com/graphql", json.dumps({"query": query}).encode('utf-8'))
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer {}".format(GITHUB_API_TOKEN))

    response = urlopen(req)
    try:
        for edge in json.loads(response.read())["data"]["search"]["edges"]:
            node = edge["node"]
            result = "⭐ {} {}".format(
                node["stargazers"]["totalCount"],
                node["name"]
            )
            if args.url and node.get("url"):
                result += " ({})".format(node["url"])
            if args.desc and node.get("description"):
                result += "\n- {}\n".format(node["description"].encode("utf8"))
           
            print(result)
    except Exception as e:
        print(e)
        print("something went wrong!")


def main():
    parser = argparse.ArgumentParser(prog="githubstars", description="List repository stars and info through Github v4 GraphQL API")
    parser.add_argument("repo", help="repository name to search", nargs="?")
    parser.add_argument("--count", help="number of repositories to show", default=10, type=int, metavar="")
    parser.add_argument("--desc", help="show repo description", action="store_true")
    parser.add_argument("--lang", help="search based on language", metavar="")
    parser.add_argument("--new-created", help="created this week", action="store_true")
    parser.add_argument("--new-pushed", help="pushed this week", action="store_true")
    parser.add_argument("--url", help="show repo url", action="store_true")
    parser.add_argument("--verbose", help="show request detail", action="store_true")
    parser.add_argument("--version", help="show version", action="store_true")

    args = parser.parse_args()
    cli(args)

if __name__ == "__main__":
    main()
