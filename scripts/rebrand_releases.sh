#!/usr/bin/env bash
# Rename release assets in-place; never touch downloaded APK bytes.
set -euo pipefail
: "${GH_TOKEN:?GitHub token is required}"
: "${GITHUB_REPOSITORY:?Repository is required}"
command -v gh >/dev/null
command -v jq >/dev/null

mapfile -t releases < <(
  gh api "repos/$GITHUB_REPOSITORY/releases?per_page=100" --paginate \
    --jq '.[] | select(.tag_name | startswith("morphe-")) | [.id, .tag_name] | @tsv'
)
if (( ${#releases[@]} == 0 )); then
  echo "No upstream-versioned Youtobe Patched releases found."
  exit 0
fi

notes="$(mktemp)"
trap 'rm -f "$notes"' EXIT

for record in "${releases[@]}"; do
  IFS=$'\t' read -r rid tag <<< "$record"
  release_json="$(gh api "repos/$GITHUB_REPOSITORY/releases/$rid")"

  while IFS=$'\t' read -r aid old_name; do
    [[ -n "$aid" ]] || continue
    new_name=""
    if [[ "$old_name" =~ ^Youtube-([0-9.]+)-morphe-([0-9.]+)-([0-9]{6})[.]apk$ ]]; then
      new_name="Youtobe-Patched-YouTube-${BASH_REMATCH[1]}-patch-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}.apk"
    elif [[ "$old_name" =~ ^YoutubeMusic-([0-9.]+)-morphe-([0-9.]+)-([0-9]{6})[.]apk$ ]]; then
      new_name="Youtobe-Patched-YouTube-Music-${BASH_REMATCH[1]}-patch-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}.apk"
    fi
    if [[ -n "$new_name" ]]; then
      echo "Renaming Release asset: $old_name -> $new_name"
      gh api --method PATCH "repos/$GITHUB_REPOSITORY/releases/assets/$aid" \
        -f name="$new_name" >/dev/null
    fi
  done < <(jq -r '.assets[]? | [.id, .name] | @tsv' <<< "$release_json")

  release_json="$(gh api "repos/$GITHUB_REPOSITORY/releases/$rid")"
  {
    echo "# Youtobe Patched"
    echo
    echo "Stable YouTube / YouTube Music APKs for CorePatch ROMs."
    echo "Upstream patch engine: Morphe v${tag#morphe-}."
    echo "Original app packages, signatures and launcher icons are preserved."
    echo
    echo "## Youtobe Patched APKs"
    jq -r '.assets[]? | select(.name | endswith(".apk")) | .name' \
      <<< "$release_json" | sort | sed 's/^/- /'
  } > "$notes"

  gh api --method PATCH "repos/$GITHUB_REPOSITORY/releases/$rid" \
    -f name="Youtobe Patched v${tag#morphe-}" -F body=@"$notes" >/dev/null
  echo "Rebranded Youtobe Patched Release $tag"
done
