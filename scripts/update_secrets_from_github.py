#!/usr/bin/env python3
#TODO: NEED SHEBANG?

from github import Github

g = Github("access_token")
for repo in g.get_user().get_repos():
    print(repo.name)
