# Example 03 — Scheduled (Cron) Trigger

## What This Teaches

The `schedule` event runs your workflow on a time-based schedule — no push or PR required. This is useful for nightly builds, daily reports, weekly cleanup, and health checks.

## Concepts Covered

| Concept | Key |
|---|---|
| Schedule a workflow | `on: schedule: - cron: "..."` |
| Cron expression syntax | `"0 2 * * *"` |
| Pair with manual trigger | `on: workflow_dispatch:` |
| Check which day it is | `date +%u` in a run step |
| Multiple cron schedules | list multiple `- cron:` entries |

## How to Try It

1. Copy `.github/workflows/scheduled-cron.yml` into your repo.
2. Commit and push to your **default branch** (usually `main`).
3. Scheduled workflows only activate on the default branch — feature branches are ignored.
4. To test immediately without waiting for 02:00 UTC: go to **Actions tab → select the workflow → Run workflow**.

## Cron Expression Cheatsheet

```
┌──────── minute   (0-59)
│ ┌────── hour     (0-23 UTC)
│ │ ┌──── day      (1-31)
│ │ │ ┌── month    (1-12)
│ │ │ │ ┌ weekday  (0=Sun, 6=Sat)
│ │ │ │ │
* * * * *
```

| Expression | Meaning |
|---|---|
| `0 6 * * *` | Every day at 06:00 UTC |
| `0 0 * * 1` | Every Monday at midnight UTC |
| `0 9-17 * * 1-5` | Every hour 9am–5pm, weekdays |
| `*/15 * * * *` | Every 15 minutes (GitHub minimum) |
| `0 2 1 * *` | First day of every month at 02:00 |

Use [crontab.guru](https://crontab.guru) to test your expressions interactively.

## Key Concepts Explained

### Always pair with `workflow_dispatch`

You can't run scheduled workflows on demand unless you add `workflow_dispatch`. Add it so you can test the workflow without waiting for the clock:

```yaml
on:
  schedule:
    - cron: "0 2 * * *"
  workflow_dispatch:      # adds "Run workflow" button in the UI
```

### Multiple schedules

```yaml
on:
  schedule:
    - cron: "0 2 * * *"    # nightly at 02:00
    - cron: "0 8 * * 1"    # weekly on Monday at 08:00
```

Both fire independently. Use `github.event.schedule` to tell them apart if needed.

### GitHub may delay runs

Scheduled workflows can be delayed by up to 15 minutes during high-traffic periods. Don't rely on them for time-sensitive work.

## Common Mistakes

**Mistake:** Pushing the workflow to a feature branch and expecting the schedule to work. Schedules only activate on the **default branch**.

**Mistake:** Using a cron interval shorter than `*/15` — GitHub enforces a 15-minute minimum.

**Mistake:** Forgetting that all cron times are **UTC**. A schedule of `"0 9 * * *"` is 09:00 UTC, which might be 2am or 5pm in your local timezone.

## What's Next

See [Example 04](../04-manual-dispatch/) to learn how to create a rich manual trigger with input parameters.
