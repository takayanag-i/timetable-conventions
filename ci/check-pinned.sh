#!/bin/sh
set -eu

path=${1:-.agents/conventions}

url=$(git config -f .gitmodules --get "submodule.$path.url" || true)
if [ -z "$url" ]; then
  echo "check-pinned: .gitmodules に submodule.$path.url が無い" >&2
  exit 1
fi

pinned=$(git ls-tree HEAD "$path" | awk '$2 == "commit" { print $3 }')
if [ -z "$pinned" ]; then
  echo "check-pinned: HEAD が $path を submodule として固定していない" >&2
  exit 1
fi

head=$(git ls-remote "$url" refs/heads/main | awk '{ print $1 }')
if [ -z "$head" ]; then
  echo "check-pinned: $url の refs/heads/main を読めない" >&2
  exit 1
fi

if [ "$pinned" != "$head" ]; then
  echo "check-pinned: $path が古い" >&2
  echo "  固定: $pinned" >&2
  echo "  正本: $head" >&2
  echo "  git submodule update --remote $path で進め、コミットする" >&2
  exit 1
fi

echo "check-pinned: $path は $url の main と一致している"
