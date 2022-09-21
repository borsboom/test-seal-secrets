#!/usr/bin/env bash
set -xeu -o pipefail
#TODO: MOVE TO SHARED WORKFLOW
#TODO: REWRITE IN PYTHON?

MAPPING_FILE_NAME=secret_mapping.csv

#TODO: SHOULD MAPPING FILES BE IN ENV DIRECTORY?  OR SUPPORT BOTH?
#TODO: SUPPORT HELM?
#TODO: TEST WITH MULTILINE SECRET VALUE (E.G. TLS CERTIFICATE)
#TODO: AVOID REWRITING PREVIOUS VALUE OF SECRET (BE SURE TO HANDLE CASE IF SEALED SECRET WAS MODIFIED MANUALLY, PROBABLY SHOULD FAIL NOISILY)
for mapping_file_path in kubernetes/*/$MAPPING_FILE_NAME; do
    app_dir_path="$(dirname "$mapping_file_path")"
    app_name="$(basename "$app_dir_path")" #TODO: NEED?
    #TODO: HANDLE COMMENT LINES IN CSV
    while IFS=, read -r github_secret_name kube_secret_name kube_secret_field_name; do
        echo "$github_secret_name and $kube_secret_name and $kube_secret_field_name"
        for overlay_dir_path in $app_dir_path/overlays/*$ENVIRONMENT_NAME; do
        done
    done < "$mapping_file_path"
done
