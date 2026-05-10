# Example 10 — Dependency Caching

## What This Teaches

Every GitHub Actions runner starts from scratch. Without caching, `pip install` downloads all packages from the internet on every run — this can take 60–180 seconds. Caching stores the downloaded packages and restores them on the next run, cutting install time to a few seconds when nothing changed.

## Concepts Covered

| Concept | Key |
|---|---|
| Built-in pip cache | `cache: pip` in `actions/setup-python@v5` |
| Manual cache control | `actions/cache@v4` |
| Cache key design | `hashFiles('requirements*.txt')` |
| Fallback keys | `restore-keys:` |
| Check for cache hit | `steps.<id>.outputs.cache-hit == 'true'` |
| Skip install on hit | `if: steps.<id>.outputs.cache-hit != 'true'` |

## How to Try It

1. Create a `requirements.txt` in your repo root with at least one package:
   ```
   requests==2.32.3
   ```
2. Copy `.github/workflows/dependency-caching.yml` into your repo and push to `main`.
3. Watch the first run download the package (cache miss).
4. Push any commit that does **not** change `requirements.txt`.
5. Watch the second run restore from cache (cache hit) — install is instant.

To force a cache miss, change `requirements.txt` and push again.

## Key Concepts Explained

### Easy mode: built-in cache

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.14"
    cache: "pip"              # one line — handles everything
```

`actions/setup-python` with `cache: pip` automatically:
- Computes the cache key from `requirements*.txt`
- Restores on cache hit
- Saves the cache after the job if the key changed

Use this unless you need custom control.

### Manual mode: `actions/cache`

```yaml
- uses: actions/cache@v4
  id: cache-pip
  with:
    path: ~/.cache/pip
    key: pip-${{ runner.os }}-py3.14-${{ hashFiles('requirements*.txt') }}
    restore-keys: |
      pip-${{ runner.os }}-py3.14-
      pip-${{ runner.os }}-
```

### How the cache key works

```
pip-ubuntu-latest-py3.14-a3f9b2c1...
 │        │         │       │
 │        │         │       └── hash of requirements.txt contents
 │        │         └────────── Python version
 │        └──────────────────── OS (caches are OS-specific)
 └─────────────────────────────── prefix for restore-keys fallback
```

- **Primary key match** → cache restored, `cache-hit = true`
- **Restore-key match** → partial cache restored (stale), `cache-hit = false`, cache re-saved after job
- **No match** → fresh install, cache saved after job

### Cache hit output

```yaml
- id: cache-pip
  uses: actions/cache@v4
  with: ...

- name: Install (only on miss)
  if: steps.cache-pip.outputs.cache-hit != 'true'
  run: pip install -r requirements.txt
```

### Cache size limits

GitHub caches are **per-repo** with a **10 GB** total limit. Least-recently-used caches are evicted when the limit is reached. Caches also expire automatically after **7 days** of not being accessed.

## Cache key strategies

| Pattern | Key example | Use when |
|---|---|---|
| Content hash | `pip-ubuntu-${{ hashFiles('requirements*.txt') }}` | Standard — invalidates when deps change |
| Weekly | `pip-ubuntu-${{ env.WEEK }}` | Force weekly refresh |
| Daily | `pip-ubuntu-${{ env.DATE }}` | Force daily refresh |
| Branch-scoped | `pip-ubuntu-${{ github.ref_name }}-<hash>` | Feature branches need different deps |

## Common Mistakes

**Mistake:** Not including `runner.os` in the key — Linux and macOS wheels are different binaries and can't be shared.

**Mistake:** Using the same cache key forever (no hash) — the cache never invalidates and you run stale packages after updating `requirements.txt`.

**Mistake:** Caching `site-packages` directly — cache `~/.cache/pip` (the download cache) instead. Restoring `site-packages` directly across Python versions causes breakage.

## Congratulations!

You've completed all 10 examples. You now know the core building blocks of GitHub Actions:

1. Push triggers and path filters
2. Pull request event types
3. Scheduled cron jobs
4. Manual dispatch with inputs
5. Concurrency control
6. Environment variable scopes
7. Job outputs and data passing
8. Conditional logic
9. Matrix builds
10. Dependency caching

Head back to the [examples README](../README.md) to see them all together, or continue with the full course modules.
