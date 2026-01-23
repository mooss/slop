#!/usr/bin/env bash
# Generate README from git branches with specific prefixes.

#############
# Functions #

function list-branches() {
    local -r prefix="$1"
    git branch -a | sed -rn "s|^ +remotes/origin/$prefix|$prefix|p" | sort
}

function branch-title() {
    local -r branch="$1"
    git show "origin/$branch:README.md" | head -n1 | sed 's/^#* *//'
}

function branch-section() {
    local -r branch="$1"
    echo "### $(branch-title $branch) (\`$branch\`)"
}

function foreach() {
    while IFS= read -r line; do
        "$@" "$line"
    done
}

#################
# Script proper #

cat <<EOF
# Collection of low to high effort AI-enhanced projects

This repo gather small projects that were made with the help of LLMs (one project per branch).
The goal is to test new workflows, get familiar with new technologies, have fun and make some tools that will be useful to me.

## Published branches

Projects in a somewhat clean state where I'm satisfied with the outcome.

$(list-branches pub | foreach branch-section)

## Experimental branches

Projects being more of an ongoing/exploratory/unfinished work.

$(list-branches exp | foreach branch-section)

## Slop branches

Low-effort, mostly proofs of concept or silly ideas with a lot of AI assistance.

$(list-branches slop | foreach branch-section)

## Main tools used

 - [Aider](https://github.com/Aider-AI/aider)
 - [Aidermacs](https://github.com/MatthewZMD/aidermacs)
 - [AIChat](https://github.com/sigoden/aichat)
 - [jenai](https://github.com/mooss/jen) (personal project, small wrapper around AIChat)
 - [gptel](https://github.com/karthink/gptel)

## Branch workflow

Right now there are two separate workflows:
 1. Start with an experimental branch, with most work being done by hand.
    Experimental branches can then be polished and moved to a published branch.
 2. Start with a slop branch, with much more unsupervised AI work.

I might eventually add a slop to experimental workflow.
EOF
