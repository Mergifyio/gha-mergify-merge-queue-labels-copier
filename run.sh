#!/bin/bash

set -Eeo pipefail

die() {
    echo "$@"
    exit 1;
}

[ -n "$MERGE_QUEUE_PR_URL" ] || die "MERGE_QUEUE_PR_URL is not set"
[ -n "$REPOSITORY_URL" ] || die "REPOSITORY_URL is not set"

MERGE_QUEUE_METADATA="$(gh pr view --json body -q ".body" "$MERGE_QUEUE_PR_URL" | sed -n -e "/\`\`\`yaml/,/\`\`\`/p" | sed -e '1d;$d')"
mapfile -t PR_NUMBERS < <(echo "$MERGE_QUEUE_METADATA" | yq -r '.pull_requests[].number')

echo "Copying labels from ${PR_NUMBERS[*]} to $MERGE_QUEUE_PR_URL"

LABELS_TO_ADD="$ADDITIONAL_LABELS"

for pr_number in "${PR_NUMBERS[@]}"; do

  mapfile -t pr_labels < <(gh pr view --json labels -q '.labels[]|.name' "${REPOSITORY_URL}/pull/$pr_number")
  echo "Found labels: ${pr_labels[*]} on PR #$pr_number"
  for pr_label in "${pr_labels[@]}"; do
    if [[ -z "$LABELS_TO_COPY" ]] || [[ ",$LABELS_TO_COPY," =~ ,"$pr_label", ]]; then
      LABELS_TO_ADD="$LABELS_TO_ADD,$pr_label"
    fi
  done

done

# strip leading and trailing commas, and remove duplicates
LABELS_TO_ADD=${LABELS_TO_ADD%%,}
LABELS_TO_ADD=${LABELS_TO_ADD##,}
LABELS_TO_ADD=${LABELS_TO_ADD//,,/,}

echo "Adding labels $LABELS_TO_ADD to $MERGE_QUEUE_PR_URL"
if [ -n "$LABELS_TO_ADD" ]; then
    gh pr edit "$MERGE_QUEUE_PR_URL" --add-label "$LABELS_TO_ADD"
fi
