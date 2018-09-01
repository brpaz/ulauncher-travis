
import requests
from datetime import datetime
from cache import Cache

TRAVIS_API_URL = "https://api.travis-ci.org"
REPOS_CACHE_KEY = "travis_repos"
REPOS_CACHE_TTL = 300


class TravisCLient(object):
    """ Client for interacting with Travis API """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Ulauncher-Travis/1.0.0',
            'Accept': 'application/vnd.travis-ci.2+json',
            'Travis-API-Version': "3"
        }

    def set_access_token(self, access_token):
        """ Sets the access token required to authenticate in the Travis API """
        self.headers['Authorization'] = "token %s" % access_token
        Cache.purge()

    def get_repos(self, query=None):
        """ Returns a list of projects enabled in Travis """

        if Cache.get(REPOS_CACHE_KEY):
            repos = Cache.get(REPOS_CACHE_KEY)
        else:
            url = "%s/repos" % TRAVIS_API_URL
            payload = {"limit": 200, "active": "1", "sort_by": "name"}
            r = requests.get(url, params=payload, headers=self.headers)
            r.raise_for_status()

            response = r.json()
            repos = response['repositories']

        result = []
        for repo in repos:

            if query and query.lower() not in repo['name']:
                continue

            result.append({
                'id': repo['id'],
                'name': repo['name'],
                'description': repo['description'],
                'url': "https://travis-ci.org/%s" % repo['slug']
            })

            Cache.set(REPOS_CACHE_KEY, repos, REPOS_CACHE_TTL)

        return result

    def get_builds_for_repo(self, repo_id):
        """ Returns the latest builds for the specified repository """

        url = "%s/repo/%s/builds" % (TRAVIS_API_URL, repo_id)
        payload = {"limit": 5}
        r = requests.get(url, params=payload, headers=self.headers)
        r.raise_for_status()
        response = r.json()
        result = []

        for build in response['builds']:
            result.append({
                'id': build['id'],
                'commit_message': build['commit']['message'],
                'branch': build['branch']['name'],
                'state': build['state'],
                'number': build['number'],
                'updated_at': build['updated_at'],
                'triggered_by': build['created_by']['login'],
                'url': "https://travis-ci.org/%s/builds/%s" % (build['repository']['slug'], build['id'])
            })

        return result
