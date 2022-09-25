#!/usr/bin/env python3
# @@@ NEED SHEBANG?
# @@@ BREAK INTO FUNCTIONS
# @@@ SUPPORT BASE64 ENCODED BINARY?

# @@@ TRIM/SORT IMPORTS
import csv
import glob
import json
import os
import subprocess
import sys
import yaml
import hashlib

# from github import Github
# g = Github(os.getenv('GITHUB_TOKEN'))
# for repo in g.get_user().get_repos():
#     print(repo.name)

KUBERNETES_NAMESPACE = os.environ["INPUT_KUBERNETES_NAMESPACE"] #@@@ sys.argv[1]
ENVIRONMENT_NAME = os.environ["INPUT_ENVIRONMENT_NAME"] #@@@ sys.argv[2]
#@@@ ANY LIMIT TO SIZE WE CAN PASS VIA ENVIRONMENT VARIABLE?
GITHUB_SECRETS_JSON = os.environ["INPUT_GITHUB_SECRETS_JSON"] #@@@ sys.argv[3]

# @@@ CHANGE LOCATION?
CERTIFICATE_PATH = f"certificates/{ENVIRONMENT_NAME}_sealedsecrets.crt"

# @@@ READ DIRECTLY FROM GITHUB SOMEHOW?
GITHUB_SECRETS = json.loads(GITHUB_SECRETS_JSON)


def run_kubeseal(sealedsecret_path, sealedsecret_name, kubectl_args, kubeseal_args):
    kubectl_result = subprocess.run(
        [
            "./kubectl",
            "create",
            "secret",
            "generic",
            sealedsecret_name,
            "--dry-run=client",
            "-o",
            "yaml",
        ]
        + kubectl_args,
        check=True,
        capture_output=True,
    )
    print(f"@@@ kubectl_result.stdout={kubectl_result.stdout}")
    # @@@ TAKE KUBERNETES_NAMESPACE AND CERTIFICATE_PATH AS ARGUMENT?
    kubeseal_result = subprocess.run(
        [
            "./kubeseal",
            "--namespace",
            KUBERNETES_NAMESPACE,
            "--scope",
            "namespace-wide",
            "--cert",
            CERTIFICATE_PATH,
            "-o",
            "yaml",
        ]
        + kubeseal_args,
        check=True,
        capture_output=True,
        input=kubectl_result.stdout,
    )
    print(f"@@@ kubeseal_result.stdout={kubeseal_result.stdout}")
    print(f"@@@ kubeseal_result.stderr={kubeseal_result.stderr}")
    # with open(sealedsecret_path, "wb") as sealedsecret_file:
    #     sealedsecret_file.write(kubeseal_result.stdout)
    return kubeseal_result.stdout


def sha256_digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_yaml_file(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


# @@@ RENAME?
def ensure_annotations(yaml):
    metadata = yaml.get("metadata")
    if metadata is None:
        metadata = {}
        yaml["metadata"] = metadata
    annotations = metadata.get("annotations")
    if annotations is None:
        annotations = {}
        yaml["annotations"] = annotations
    return annotations


# @@@ RENAME
def initialize_sealedsecret(
    sealedsecret_path, sealedsecret_name, value_sha256_annotation_key
):
    if os.path.exists(sealedsecret_path):
        sealedsecret_yaml = read_yaml_file(sealedsecret_path)
        print(f"@@@ sealedsecret_yaml={sealedsecret_yaml}")
        return ensure_annotations(sealedsecret_yaml).get(value_sha256_annotation_key)
    else:
        new_sealedsecret_content = run_kubeseal(
            sealedsecret_path, sealedsecret_name, [], ["--allow-empty-data"]
        )
        with open(sealedsecret_path, "wb") as sealedsecret_file:
            sealedsecret_file.write(new_sealedsecret_content)
        return None


def update_sealedsecret(
    sealedsecret_path,
    sealedsecret_name,
    sealedsecret_data_key,
    sealedsecret_data_value,
    value_sha256_annotation_key,
    new_value_sha256,
):
    run_kubeseal(
        sealedsecret_path,
        sealedsecret_name,
        [
            "--from-literal",
            f"{sealedsecret_data_key}={sealedsecret_data_value}",
        ],
        ["--merge-into", sealedsecret_path],
    )
    sealedsecret_yaml = read_yaml_file(sealedsecret_path)
    print(f"@@@ sealedsecret_yaml={sealedsecret_yaml}")
    ensure_annotations(sealedsecret_yaml)[
        value_sha256_annotation_key
    ] = new_value_sha256
    with open(sealedsecret_path, "w") as sealedsecret_file:
        yaml.dump(sealedsecret_yaml, sealedsecret_file)


# @@@ RENAME?
def process_secrets_map_row(
    overlay_dir_path, github_secret_name, sealedsecret_name, sealedsecret_data_key
):
    github_secret_value = GITHUB_SECRETS[github_secret_name]
    value_sha256_annotation_key = (
        f"bbyhealth.com/data/{sealedsecret_data_key}/sha256"
    )
    # @@@ CONSTANT FOR FILE SUFFIX?
    sealedsecret_path = f"{overlay_dir_path}/{sealedsecret_name}_sealedsecret.yaml"
    print(f"@@@ sealedsecret_path={sealedsecret_path}")
    old_value_sha256 = initialize_sealedsecret(
        sealedsecret_path, sealedsecret_name, value_sha256_annotation_key
    )
    print(f"@@@ old_value_sha256={old_value_sha256}")
    new_value_sha256 = sha256_digest(github_secret_value)
    print(f"@@@ new_value_sha256={new_value_sha256}")
    if new_value_sha256 != old_value_sha256:
        print("@@@ HASHES DON'T MATCH; UPDATING SEALED SECRET")
        update_sealedsecret(
            sealedsecret_path,
            sealedsecret_name,
            sealedsecret_data_key,
            github_secret_value,
            value_sha256_annotation_key,
            new_value_sha256,
        )
    else:
        print("@@@ HASHES MATCH; SKIPPING")


def main():
    secrets_map_paths = glob.glob(
        f"kubernetes/*/overlays/*{ENVIRONMENT_NAME}/secrets_map*.csv"
    )
    for secrets_map_path in secrets_map_paths:
        with open(secrets_map_path, mode="r") as secrets_map_file:
            print(f"@@@ READING {secrets_map_file}")
            # @@@ SHOULD WE USE YAML/JSON INSTEAD?
            secrets_map_csv_reader = csv.DictReader(secrets_map_file)
            for secrets_map_row in secrets_map_csv_reader:
                # @@@ SKIP COMMENTS?
                # @@@ INLINE SEAL_SECRET
                print(f"@@@ {secrets_map_row}")
                # @@@ HANDLE MISSING SECRET
                process_secrets_map_row(
                    os.path.dirname(secrets_map_path),
                    secrets_map_row["github_secret_name"],
                    secrets_map_row["sealedsecret_name"],
                    secrets_map_row["sealedsecret_data_key"],
                )


main()
