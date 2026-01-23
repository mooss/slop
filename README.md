# Collection of low to high effort AI-enhanced projects

This repo gather small projects that were made with the help of LLMs (one project per branch).
The goal is to test new workflows, get familiar with new technologies, have fun and make some tools that will be useful to me.

## Published branches

Projects in a somewhat clean state where I'm satisfied with the outcome.

### Bulk Markdown to PDF compiler (native pandoc)
[`pub/documentr.native-eisvogel`](https://github.com/mooss/slop/tree/pub/documentr.native-eisvogel)

## Experimental branches

Projects being more of an ongoing/exploratory/unfinished work.

### Bulk Markdown to PDF compiler (podman, no parallelism, not tested)
[`exp/documentr.podman-eisvogel`](https://github.com/mooss/slop/tree/exp/documentr.podman-eisvogel)
### JSON lexer (starting point, profiling, no lexing)
[`exp/jsonlexer`](https://github.com/mooss/slop/tree/exp/jsonlexer)

## Slop branches

Low-effort, mostly proofs of concept or silly ideas with a lot of AI assistance.

### JSON lexer (vaguely functional, barely tested)
[`slop/jsonlexer.naive-qwco`](https://github.com/mooss/slop/tree/slop/jsonlexer.naive-qwco)

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
