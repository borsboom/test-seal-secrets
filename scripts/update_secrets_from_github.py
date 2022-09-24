#!/usr/bin/env python3
#TODO: NEED SHEBANG?

#@@@ TRIM IMPORTS
import csv
import glob
import json
import os
import subprocess
import sys

# from github import Github
# g = Github(os.getenv('GITHUB_TOKEN'))
# for repo in g.get_user().get_repos():
#     print(repo.name)

ENVIRONMENT_NAME = sys.argv[1]
GITHUB_SECRETS_JSON = sys.argv[2]

#@@@ READ DIRECTLY FROM GITHUB SOMEHOW?
print('f@@@ GITHUB_SECRETS_JSON={GITHUB_SECRETS_JSON}')
github_secrets = json.loads(GITHUB_SECRETS_JSON)

secrets_map_paths = glob.glob(f'kubernetes/*/overlays/*{ENVIRONMENT_NAME}/secrets_map*.csv')

for secrets_map_path in secrets_map_paths:
    with open(secrets_map_path, mode='r') as secrets_map_file:
        print(f'@@@ READING {secrets_map_file}')
        #@@@ SHOULD WE USE YAML/JSON INSTEAD?
        secrets_map_csv_reader = csv.DictReader(secrets_map_file)
        for secrets_map_row in secrets_map_csv_reader:
            #@@@ SKIP COMMENTS?
            #@@@ INLINE SEAL_SECRET
            #@@@ HANDLE MISSING SECRET
            print(f'@@@ {secrets_map_row}')
            old_cwd = os.getcwd()
            #@@@ SUPPORT HELM SEALED SECRETS TOO (IN TEMPLATES SUBDIR)
            os.chdir(os.path.parent(secrets_map_path))
            subprocess.run([
                "scripts/seal_secret",
                secrets_map_row['sealedsecret_name'],
                f'--from-literal={secrets_map_row["sealedsecret_data_key"]}={github_secrets[secrets_map_row["github_secret_name"]]}'
            ], check=True)
            os.chdir(old_cwd)
