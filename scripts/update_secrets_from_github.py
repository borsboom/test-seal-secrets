#!/usr/bin/env python3
#TODO: NEED SHEBANG?

#@@@ TRIM/SORT IMPORTS
import csv
import glob
import json
import os
import subprocess
import sys
import yaml

# from github import Github
# g = Github(os.getenv('GITHUB_TOKEN'))
# for repo in g.get_user().get_repos():
#     print(repo.name)

K8S_NAMESPACE = sys.argv[1]
ENVIRONMENT_NAME = sys.argv[2]
GITHUB_SECRETS_JSON = sys.argv[3]

#@@@ CHANGE LOCATION?
CERT_PATH = f'{os.path.dirname(sys.argv[0])}/data/{ENVIRONMENT_NAME}_sealedsecrets.crt'

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
            #@@@ CONSTANT FOR FILE SUFFIX?
            sealedsecret_path = f'{os.path.dirname(secrets_map_path)}/{secrets_map_row["sealedsecret_name"]}_sealedsecret.yaml'
            if not os.path.exists(sealedsecret_path):
                kubectl_result = subprocess.run(['kubectl', 'create', 'secret', 'generic', secrets_map_row['sealedsecret_name'], '--dry-run=client', '-o', 'yaml'], check=True, capture_output=True)
                print(f'@@@ kubectl_result.stdout={kubectl_result.stdout}')
                kubeseal_result = subprocess.run(['kubeseal', '--namespace', K8S_NAMESPACE, '--scope', 'namespace-wide', '--cert', CERT_PATH, '-o', 'yaml', '--allow-empty-data'], check=False, capture_output=True, input=kubectl_result.stdout)
                print(f'@@@ kubeseal_result.stdout={kubeseal_result.stdout}')
                print(f'@@@ kubeseal_result.stderr={kubeseal_result.stderr}')
                with open(sealedsecret_path, "wb") as sealedsecret_file:
                    sealedsecret_file.write(kubeseal_result.stdout)
            # old_cwd = os.getcwd()
            # #@@@ SUPPORT HELM SEALED SECRETS TOO (IN TEMPLATES SUBDIR)
            # os.chdir(os.path.dirname(secrets_map_path))
            # subprocess.run([
            #     f'{old_cwd}/scripts/seal_secret',
            #     secrets_map_row['sealedsecret_name'],
            #     f'--from-literal={secrets_map_row["sealedsecret_data_key"]}={github_secrets[secrets_map_row["github_secret_name"]]}'
            # ], check=True)
            # os.chdir(old_cwd)
            with open(sealedsecret_path, 'r') as sealedsecret_file:
                sealedsecret_yaml = yaml.safe_load(sealedsecret_file)
            #@@@ COMPARE SHA TO NEW VALUE
            sealedsecret_yaml['metadata']['annotations']['update-secrets-from-github-sha256'] = "@@@ SETME"
            with open(sealedsecret_path, 'w') as sealedsecret_file:
                yaml.dump(sealedsecret_yaml, sealedsecret_file)
