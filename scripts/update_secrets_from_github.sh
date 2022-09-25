#!/usr/bin/env bash
#@@@ REMOVE THIS FILE
set -xeu -o pipefail
#TODO: MOVE TO SHARED WORKFLOW
#TODO: REWRITE IN PYTHON?

#TODO: RENAME FILE?
MAPPING_FILE_NAME=secrets_map.csv

#TODO: CHECK FOR ARGUMENTS
ENVIRONMENT_NAME="$1"
GITHUB_SECRETS_FILE_PATH="$2"

#TODO: SHOULD MAPPING FILES BE IN ENV DIRECTORY?  OR SUPPORT BOTH?
    #TODO: DECIDED ONLY ENV DIR, BUT SUPPORT MULTIPLE FILES, AND ALLOW USE OF SYMLINK
#TODO: SUPPORT HELM?
#TODO: TEST WITH MULTILINE SECRET VALUE (E.G. TLS CERTIFICATE)
#TODO: AVOID REWRITING PREVIOUS VALUE OF SECRET (BE SURE TO HANDLE CASE IF SEALED SECRET WAS MODIFIED MANUALLY, PROBABLY SHOULD FAIL NOISILY)
for mapping_file_path in kubernetes/*/$MAPPING_FILE_NAME; do
    app_dir_path="$(dirname "$mapping_file_path")"
    #TODO: HANDLE COMMENT LINES IN CSV
    while IFS=, read -r github_secret_name kube_secret_name kube_secret_field_name; do
        if [[ "$github_secret_name" != "#"* ]]; then
            echo "$github_secret_name and $kube_secret_name and $kube_secret_field_name" #TODO: REMOVE
            #TODO: ESCAPE GITHUB SECRET NAMES WITH SPECIAL CHARACTERS?
            github_secret_value="$(jq -r ".$github_secret_name" <"$GITHUB_SECRETS_FILE_PATH")"
            for overlay_dir_path in $app_dir_path/overlays/*$ENVIRONMENT_NAME; do
                pushd "$overlay_dir_path"
                #TODO: INLINE THE seal_secret LOGIC?
                ../../../../scripts/seal_secret "$kube_secret_name" --from-literal="$kube_secret_field_name=$github_secret_value"
                popd
            done
        fi
    done <"$mapping_file_path"
done
