#!/usr/bin/env python3
# coding: utf-8

from github import Github
from os import getenv, path
from dotenv import load_dotenv
import json
import requests

PATH = path.dirname(path.realpath(__file__))
LOCK_FILE = path.join(PATH, '.repos.json.lock')
REPOS_FILE = path.join(PATH, 'repos')


class History:
    filename = path.join(PATH, LOCK_FILE)
    history = {}

    def __init__(self):
        if path.exists(self.filename):
            with open(self.filename) as f:
                self.history = json.load(f)

    def update(self, repo, release):
        if repo in self.history:
            if release == self.history[repo]:
                return False

        self.history[repo] = release
        return True

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.history, f)


def send_rocket(repo, release):
    data = {
        'username': 'GithubRelease',
        'attachments': [
            {
                'title': "New version of {} ({})".format(repo, release.tag_name),
                'title_link': release.html_url,
                'text': release.body,
                'color': '#764FA5'
            }
        ]
    }

    r = requests.post(getenv('ROCKET_HOOK'), json=data)
    if r.status_code != 200:
        print(r.text)
        raise Exception('Something wrong')


def send_pushover(repo, release):
    data = {
        'token': getenv('PO_TOKEN'),
        'user': getenv('PO_USER'),
        'device': getenv('PO_DEVICE'),
        'title': "New version of {} ({})".format(repo, release.tag_name),
        'message': release.html_url
    }

    r = requests.post('https://api.pushover.net/1/messages.json', json=data)
    if r.status_code != 200:
        print(r.text)
        raise Exception('Something wrong')


def send_notifications(repo, release):
    if getenv('PO_TOKEN') and getenv('PO_USER') and getenv('PO_DEVICE'):
        send_pushover(repo, release)
    if getenv('ROCKET_HOOK'):
        send_rocket(repo, release)


def main():
    load_dotenv()
    g = Github(getenv('GH_TOKEN'))
    h = History()

    with open(REPOS_FILE) as f:
        for l in f.readlines():
            l = l.rstrip()
            if len(l) == 0:
                continue
            repo = g.get_repo(l)
            try:
                r = repo.get_latest_release()
            except:
                continue

            if h.update(l, r.tag_name):
                send_notifications(l, r)
    h.save()


if __name__ == '__main__':
    main()
