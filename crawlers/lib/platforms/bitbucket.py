import logging
import time
import requests
from typing import List, Tuple
from urllib.parse import urljoin
from iso8601 import iso8601

from crawlers.lib.platforms.i_crawler import IResult, ICrawler

logger = logging.getLogger(__name__)


class BitBucketResult(IResult):
    """{
            "created_on": "2011-07-08T08:59:53.298617+00:00",
            "description": "",
            "fork_policy": "allow_forks",
            "full_name": "jwalton/git-scripts",
            "has_issues": false,
            "has_wiki": false,
            "is_private": false,
            "language": "shell",
            "links": {
                "avatar": {
                    "href": "https://bytebucket.org/ravatar/%7B9a355a32-dad9-4efd-9828-ccce80dd3109%7D?ts=default"
                },
                "branches": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/refs/branches"
                },
                "clone": [
                    {
                        "href": "https://bitbucket.org/jwalton/git-scripts.git",
                        "name": "https"
                    },
                    {
                        "href": "git@bitbucket.org:jwalton/git-scripts.git",
                        "name": "ssh"
                    }
                ],
                "commits": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/commits"
                },
                "downloads": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/downloads"
                },
                "forks": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/forks"
                },
                "hooks": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/hooks"
                },
                "html": {
                    "href": "https://bitbucket.org/jwalton/git-scripts"
                },
                "pullrequests": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/pullrequests"
                },
                "self": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts"
                },
                "source": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/src"
                },
                "tags": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/refs/tags"
                },
                "watchers": {
                    "href": "https://api.bitbucket.org/2.0/repositories/jwalton/git-scripts/watchers"
                }
            },
            "mainbranch": {
                "name": "master",
                "type": "branch"
            },
            "name": "git-scripts",
            "owner": {
                "account_id": "557058:8679ff30-e82d-47b5-90f0-94127260782a",
                "display_name": "Joseph Walton",
                "links": {
                    "avatar": {
                        "href": "https://secure.gravatar.com/avatar/cbed2f56195ed90bdebd4feec31ac054?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FJW-1.png"
                    },
                    "html": {
                        "href": "https://bitbucket.org/%7Bc040300f-f69e-4a65-87a6-5a8f3ef1bbf1%7D/"
                    },
                    "self": {
                        "href": "https://api.bitbucket.org/2.0/users/%7Bc040300f-f69e-4a65-87a6-5a8f3ef1bbf1%7D"
                    }
                },
                "nickname": "jwalton",
                "type": "user",
                "uuid": "{c040300f-f69e-4a65-87a6-5a8f3ef1bbf1}"
            },
            "project": {
                "key": "PROJ",
                "links": {
                    "avatar": {
                        "href": "https://bitbucket.org/account/user/jwalton/projects/PROJ/avatar/32?ts=1543459298"
                    },
                    "html": {
                        "href": "https://bitbucket.org/jwalton/workspace/projects/PROJ"
                    },
                    "self": {
                        "href": "https://api.bitbucket.org/2.0/workspaces/jwalton/projects/PROJ"
                    }
                },
                "name": "Untitled project",
                "type": "project",
                "uuid": "{6eed76e0-e831-48d0-83ac-cbbd8ee04173}"
            },
           "scm": "git",
            "size": 394778,
            "slug": "git-scripts",
            "type": "repository",
            "updated_on": "2017-03-19T16:09:30.336053+00:00",
            "uuid": "{9a355a32-dad9-4efd-9828-ccce80dd3109}",
            "website": "",
            "workspace": {
                "links": {
                    "avatar": {
                        "href": "https://bitbucket.org/workspaces/jwalton/avatar/?ts=1543459298"
                    },
                    "html": {
                        "href": "https://bitbucket.org/jwalton/"
                    },
                    "self": {
                        "href": "https://api.bitbucket.org/2.0/workspaces/jwalton"
                    }
                },
                "name": "Joseph Walton",
                "slug": "jwalton",
                "type": "workspace",
                "uuid": "{c040300f-f69e-4a65-87a6-5a8f3ef1bbf1}"
            }
        },
    """

    def __init__(self, platform_id, search_result_item):
        name = search_result_item['name']

        owner_name = search_result_item['owner'].get('nickname', False)
        if not owner_name:
            owner_name = search_result_item['owner'].get('username', False)
        if not owner_name:
            owner_name = search_result_item['workspace']['name']
        description = search_result_item['description']
        last_commit = iso8601.parse_date(
            search_result_item['updated_on'])
        created_at = iso8601.parse_date(search_result_item['created_on'])
        language = None
        license = None

        html_url = search_result_item['links']['html']['href']

        super().__init__(platform_id=platform_id,
                         name=name,
                         description=description,
                         html_url=html_url,
                         owner_name=owner_name,
                         last_commit=last_commit,
                         created_at=created_at,
                         language=language,
                         license=license)


class BitBucketCrawler(ICrawler):
    name = 'bitbucket'

    # https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories

    def __init__(self, id, type, base_url, state=None, auth_data=None, user_agent=None, **kwargs):
        super().__init__(
            _id=id,
            type=type,
            base_url=base_url,
            path='',
            state=state,
            auth_data=auth_data,
            user_agent=user_agent
        )
        self.access_token = None
        self.token_expites_at = 0
        self.refresh_token = None
        self.client_id = auth_data.get('client_id')
        self.client_secret = auth_data.get('client_secret')
        self.request_url = urljoin(self.base_url, self.path)

    def request(self, url):
        if not self.access_token or self.token_expites_at < time.time():
            response = self.requests.post(
                urljoin('https://bitbucket.org', 'site/oauth2/access_token'),
                data=dict(grant_type='client_credentials'),
                auth=(self.client_id, self.client_secret)
            )
            data = response.json()
            self.access_token = data['access_token']
            self.token_expites_at = time.time() + int(data['expires_in'])
            self.refresh_token = data['refresh_token']
            self.requests.headers["Authorization"] = f"Bearer {self.access_token}"

        return self.requests.get(url)

    def crawl(self, state: dict = None) -> Tuple[bool, List[BitBucketResult], dict]:
        url = False
        if state:
            url = state.get('url', False)
            if not url:
                logger.warning('{self} broken state, defaulting to start')

        if not url:
            url = '/2.0/repositories/?pagelen=100&sort=-created_on'

        while url:
            try:
                response = self.request(urljoin(self.base_url, url))
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error(e)
                logger.error(e.response.reason)
                logger.error(e.response.text)
                return False, [], {}

            response_json = response.json()
            repo_page = response_json['values']
            repos = [BitBucketResult(self._id, result) for result in repo_page]
            state = {'url': url}
            yield True, repos, state

            # https://stackoverflow.com/questions/32312758/python-requests-link-headers
            url = response_json.get('next', False)
            if not url:
                # not hit rate limit, and we dont have a next url - finished!
                # reset state
                yield True, [], None
            time.sleep(.1)
