
from github import Github
from os import getenv, path
import json
import requests
from dotenv import load_dotenv

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

def send_notification(repo, tag, url):
    data = {
        'token': getenv('PO_TOKEN'),
        'user': getenv('PO_USER'),
        'device': getenv('PO_DEVICE'),
        'title': "New version of {} ({})".format(repo, tag),
        'message': url
    }
    r = requests.post(' https://api.pushover.net/1/messages.json', json=data)
    if r.status_code != 200:
        print(r.text)
        raise Exception('Something wrong')

def main():
    load_dotenv()
    g = Github(getenv('GH_TOKEN'))
    h = History()

    with open('repos') as f:
        for l in f.readlines():
            l = l.rstrip()
            if len(l) == 0:
                continue
            repo = g.get_repo(l)
            print(l)
            try:
                r = repo.get_latest_release()
            except:
                continue
            if h.update(l, r.tag_name):
                send_notification(l, r.tag_name, r.html_url)
    h.save()

main()
