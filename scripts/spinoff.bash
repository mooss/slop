#!/usr/bin/env bash
set -euo pipefail

function usage() {
    echo "Usage: $0 <new-repo>"
    exit 1
}

[[ $# -eq 1 ]] || usage

REPOSITORY="$1"
DIR="../$REPOSITORY"
VISIBILITY="--public"
SOURCE="$PWD"

# git clone --single-branch --branch "$branch" "$orig" "$dir"
git clone --single-branch . "$DIR"
cd "$DIR"
git branch -m main

# Copy working tree (including uncommitted/untracked files).
rsync -a --delete --exclude='.git' "$SOURCE"/ .

# Remove old remote (points to original repo).
git remote remove origin

# Create new GitHub repo and push the single branch.
gh repo create "$REPOSITORY" "$VISIBILITY" --source=. --push
