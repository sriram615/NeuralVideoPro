#!/usr/bin/env bash
#
# promote_and_archive.sh
#
# One-time repo cleanup for CV-Hackathon.
#
# What it does:
#   1. Moves everything at the repo root EXCEPT NEURALVIDEO-Hackathon-2026/
#      (the old dev-history scripts, the first-draft src/api.py/app.py,
#      duplicate venvs, etc.) into archive/.
#   2. Promotes the contents of NEURALVIDEO-Hackathon-2026/ up to the repo
#      root, so the clean, documented project becomes the actual repo.
#   3. Removes the now-empty NEURALVIDEO-Hackathon-2026/ directory.
#
# This uses `git mv` so history is preserved for tracked files, and falls
# back to plain `mv` for anything git doesn't track (venvs, caches, etc).
#
# SAFETY:
#   - Run this from the repo root (the folder containing NEURALVIDEO-Hackathon-2026/).
#   - Commit or stash any in-progress work first — this script refuses to run
#     if there are uncommitted changes, so you always have a clean point to
#     revert to with `git reset --hard` if something looks wrong afterward.
#   - Read through the MOVE LIST below before running. It was written by
#     inspecting a directory listing, not by running against your actual
#     working tree, so double check nothing important got missed or
#     mis-targeted before you trust it blindly.
#   - This does not touch git history rewriting or anything remote — it's
#     just file moves, so it's easy to undo with `git reset --hard` +
#     `git clean -fd` if you run it before committing the result.

set -euo pipefail

REPO_ROOT="$(pwd)"
NESTED="NEURALVIDEO-Hackathon-2026"
ARCHIVE="archive"

if [ ! -d "$NESTED" ]; then
  echo "Error: $NESTED not found in $REPO_ROOT. Run this from the repo root." >&2
  exit 1
fi

if [ -d .git ] && [ -n "$(git status --porcelain)" ]; then
  echo "Error: you have uncommitted changes. Commit or stash them first," >&2
  echo "so this move is easy to undo with 'git reset --hard' if needed." >&2
  exit 1
fi

move() {
  # git mv if tracked, else plain mv. $1 = source, $2 = dest dir
  local src="$1" dest_dir="$2"
  [ -e "$src" ] || return 0
  mkdir -p "$dest_dir"
  if [ -d .git ] && git ls-files --error-unmatch "$src" >/dev/null 2>&1; then
    git mv "$src" "$dest_dir/"
  else
    mv "$src" "$dest_dir/"
  fi
}

echo "== Step 1: archiving outer dev-history files into $ARCHIVE/ =="
mkdir -p "$ARCHIVE"

# Old first-draft project code (superseded by NESTED/backend/)
for item in api.py app.py schemas.py src tests reports data frontend scripts docs \
            requirements.txt "Video Retrieval System Roadmap.pdf"; do
  move "$item" "$ARCHIVE"
done

# One-off data-collection / exploration scripts from the hackathon
for item in check_urls.py fetch_news.py find_archive_news.py find_clean_news.py \
            ingest_and_test_steve_jobs.py ingest_expanded_news.py ingest_real_news.py \
            test_historical_news.py test_news_urls.py verify_pipeline_test.py \
            wikimedia_news.py eval_suite.py; do
  move "$item" "$ARCHIVE"
done

# Local envs/caches — not git-tracked (already in .gitignore), just relocate
# so they're out of the way; feel free to delete these instead.
for item in venv .venv __pycache__ .pytest_cache; do
  move "$item" "$ARCHIVE"
done

echo "== Step 2: promoting $NESTED/ contents to repo root =="
shopt -s dotglob nullglob
for item in "$NESTED"/*; do
  base="$(basename "$item")"
  if [ -e "$REPO_ROOT/$base" ]; then
    echo "  Skipping $base — already exists at repo root, resolve by hand." >&2
    continue
  fi
  move "$item" "$REPO_ROOT"
done
shopt -u dotglob nullglob

echo "== Step 3: removing now-empty $NESTED/ =="
rmdir "$NESTED" 2>/dev/null || echo "  $NESTED not empty — check what's left in it." >&2

echo
echo "Done. Review with 'git status', then:"
echo "  git add -A"
echo "  git commit -m 'Promote NEURALVIDEO-Hackathon-2026 to repo root, archive dev history'"
echo
echo "Old dev-history scripts and the first-draft src/ are now under archive/."
echo "The old eval_suite.py from the repo root also moved to archive/ — the"
echo "canonical one now lives under scripts/evaluation/ inside the promoted project."
