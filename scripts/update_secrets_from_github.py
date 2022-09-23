#!/usr/bin/env python3
#TODO: NEED SHEBANG?

import glob
import os
import sys
import csv #@@@ WHAT IS PANDAS?
# from github import Github

# g = Github(os.getenv('GITHUB_TOKEN'))
# for repo in g.get_user().get_repos():
#     print(repo.name)

ENVIRONMENT_NAME = sys.argv[1];
GITHUB_SECRETS_FILE_PATH = sys.argv[2];

secrets_map_files = glob.glob(f'kubernetes/*/*{ENVIRONMENT_NAME}/secrets_map*.csv');

for secrets_map_file in secrets_map_files:
    print(f'@@@ READING {secrets_map_file}')
    csv_reader = csv.reader(secrets_map_file, delimiter=',')
