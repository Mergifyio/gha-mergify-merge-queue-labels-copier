# gha-mergify-merge-queue-labels-copier

Copies pull request labels to merge queue draft pull requests

To use:

```yaml
name: Mergify merge-queue labels copier
on:
  pull_request_target:
    types:
      - opened

jobs:
  mergify-merge-queue-labels-copier:
    runs-on: ubuntu-20.04
    steps:
      - name: Copying labels
        uses: Mergifyio/gha-mergify-merge-queue-labels-copier
        with:
          labels: docker
          additional-labels: merge-queue-pr
          token: ${{ github.token }}
```
