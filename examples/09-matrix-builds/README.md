# Example 09 — Matrix Builds

## What This Teaches

A matrix strategy lets you run the same job N times in parallel, each with different variable values. This is the idiomatic way to test across multiple Python versions, operating systems, or any other dimension — without copy-pasting job definitions.

## Concepts Covered

| Concept | Key |
|---|---|
| Run N copies of a job | `strategy: matrix: key: [v1, v2, v3]` |
| Reference the current value | `${{ matrix.key }}` |
| Multi-dimensional matrix | two variables → N × M combinations |
| Add extra keys to a cell | `include:` |
| Remove a specific combination | `exclude:` |
| Cancel all if one fails | `fail-fast: true` |
| Limit parallel jobs | `max-parallel: N` |

## How to Try It

1. Copy `.github/workflows/matrix-builds.yml` into your repo and push to `main`.
2. In the **Actions tab**, open the run and watch `test-matrix` expand into **3 parallel jobs** (one per Python version).
3. The `multi-var-matrix` job expands into a 2×2 grid minus the excluded cell, plus the extra included cell.

## Key Concepts Explained

### Basic matrix

```yaml
strategy:
  matrix:
    python-version: ["3.12", "3.13", "3.14"]

steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

This creates **3 jobs** running in parallel. Each job gets a different `matrix.python-version` value.

### Multi-variable matrix (Cartesian product)

```yaml
matrix:
  python-version: ["3.12", "3.14"]
  os: [ubuntu-latest, macos-latest]
```

Creates **4 jobs**: 3.12/ubuntu, 3.12/macos, 3.14/ubuntu, 3.14/macos.

### `include` — add extra data or extra cells

```yaml
include:
  # Add a "label" key to a specific existing cell
  - os: ubuntu-latest
    python-version: "3.14"
    label: "primary"

  # Add a brand-new cell not in the Cartesian product
  - os: windows-latest
    python-version: "3.13"
    label: "windows-extra"
```

### `exclude` — remove specific cells

```yaml
exclude:
  - os: macos-latest
    python-version: "3.12"
```

Removes the macos + 3.12 combination from the matrix.

### `fail-fast`

```yaml
strategy:
  fail-fast: false   # let all matrix jobs finish even if one fails
```

Default is `true` (one failure cancels the rest). Set to `false` when you want the full picture of which versions break.

### Matrix job name

```yaml
name: "Test / Python ${{ matrix.python-version }}"
```

Use the matrix variable in the job name so you can identify each run at a glance in the UI.

## ASCII Diagram

```
matrix:
  python-version: [3.12, 3.13, 3.14]

─────────────────────────────────────────────
  Job A           Job B           Job C
  Python 3.12     Python 3.13     Python 3.14
  (parallel)      (parallel)      (parallel)
─────────────────────────────────────────────
```

## Common Mistakes

**Mistake:** Quoting Python version numbers without quotes — YAML may parse `3.12` as the float `3.1` (dropping the trailing zero). Always quote: `"3.12"`.

**Mistake:** Leaving `fail-fast: true` (default) when debugging — if version 3.12 fails first, you never see whether 3.13 and 3.14 also fail.

## What's Next

See [Example 10](../10-dependency-caching/) to learn how to cache pip packages so your builds run faster.
