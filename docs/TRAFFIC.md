# 📈 Repository traffic history

[![Scope](https://img.shields.io/badge/Scope-Repository_analytics-00338D?style=flat-square)](#-stored-data)
[![Activation](https://img.shields.io/badge/Activation-Pending-BF8700?style=flat-square)](#-activation-and-evidence)

GitHub keeps repository traffic for 14 days. The **Traffic history** workflow
([.github/workflows/traffic-history.yml](../.github/workflows/traffic-history.yml))
collects it once a day and merges it into CSV files on the data-only
`traffic-history` branch, so the history outlives that window. It is
repository analytics, not CI: it builds and tests nothing.

## ⏱️ Schedule

The workflow is scheduled daily at **06:17 UTC** and can be started from
**Actions → Traffic history → Run workflow** on `main`. GitHub may start
scheduled runs late; each collection records the time it was actually taken.
A manual run on any other branch is skipped.

## 🔑 Credential setup and renewal

The traffic API needs a token with **Administration: read** on the
repository. The workflow token cannot be given that permission, so a
fine-grained personal access token is used.

1. **Settings → Environments → New environment** `analytics`. Under
   *Deployment branches and tags*, select *Selected branches and tags* and
   allow `main` only. Do this before adding the secret: a run that names a
   missing environment creates it without that restriction.
2. **Settings → Developer settings → Fine-grained tokens → Generate new
   token**: resource owner `danielep71`, *Only select repositories*:
   `K-LCR`, repository permission **Administration: Read-only**, nothing
   else. Set an expiry of at most 90 days.
3. In the `analytics` environment, add the secret **TRAFFIC_TOKEN** with that
   token. Never put the token in a file, issue, comment or chat.
4. Run the workflow manually on `main` and check that it passes and that
   `traffic-history` gains a commit.

**Renewal:** before the token expires, and at least every 90 days, generate a
new token with the same settings, replace the secret, and repeat step 4.
Revoke the token at once if it may have been exposed, or if the workflow is
changed by anyone but the maintainer. Collections missed while the token is
invalid are lost once they fall outside the 14-day window.

Only the fetch step receives `TRAFFIC_TOKEN`, and it runs `curl` only. The
merge script runs without it, and the push uses the workflow token with
`contents: write`.

## 🗄️ Stored data

The `traffic-history` branch holds `README.md` and these files under `data/`.
On the first successful collection, the workflow creates an orphan commit
containing only this README and the four CSV files. It has no history in
common with main, must
never be merged into a source branch, and must never be force-pushed.

| File | Key | Contents |
| --- | --- | --- |
| `daily.csv` | `date` | Views and unique views, clones and unique clones per UTC day. `views_collected_at` and `clones_collected_at` give the collection that last changed each pair; `views_observed_at` and `clones_observed_at` record the latest observation. |
| `snapshots.csv` | `snapshot_date` | One row per collection day: the first and last day the API reported, the 14-day totals, and `collected_at`, the collection that last changed that day's snapshot, referrers or paths. `observed_at` records the latest observation of that unit. |
| `referrers.csv` | `snapshot_date`, `rank` | The top 10 referrers over the 14 days before each collection. |
| `paths.csv` | `snapshot_date`, `rank` | The top 10 repository paths over the same window. |

Referrers and paths are retained per collection day, because the API gives
them only as 14-day totals, never per day.

### Merge rules

`tools/traffic_history.py` merges each collection idempotently:

- **Overlapping windows:** for every date the collection reports, its values
  replace the stored ones. The newest collection wins, so a day that was
  incomplete when first collected is corrected later. Views and clones are
  merged separately, each with its own collection time, which stays unchanged
  when its values do not change. Separate observed-at watermarks advance on
  every newer observation, even if counts are identical.
- **Older history:** dates the collection does not report keep their values.
  Nothing is deleted.
- **No double counting:** values are replaced, never added. Unique counts are
  never summed across days or windows; a 14-day unique count is only in
  `snapshots.csv`.
- **Same-day runs:** a collection day's snapshot, referrers and paths are one
  unit. A second collection on the same UTC day replaces the unit only if any
  of the three changed. An unchanged later collection advances the observation
  watermarks only. Replaying identical data with the same collection timestamp
  changes nothing.
- **Order:** "newest" means the latest collection time. Merging an older
  collection after a newer one, when a saved collection is replayed or a run
  is rebuilt on a newer branch tip, never replaces what the newer one stored;
  it can only fill a date or metric that nothing newer reported. Freshness uses
  the latest-observed watermark, separately from the last-change time; this
  remains correct when counts or rankings are corrected or return to an
  earlier value.

### Zero or unavailable

The API reports each day of its window, days without activity included, as
`0`. So:

- **`0`**: the day was collected and had no activity;
- **no row**: no collection covered the day, either because it is before
  tracking began or because collections stopped for more than 14 days;
- **a blank metric**: one of the two series was not reported for that day.

The step summary of each run lists the dates between the first and the last
stored day that have no row.

### Visibility

K-LCR is public, so a traffic-history branch in this repository is public too.
The planned retained data is aggregate counts, top referrer names and repository
paths/titles, with no visitor identifiers. Retention is indefinite on the
data branch; raw API responses stay in the runner's temporary directory and
are not uploaded as artifacts. No traffic badge or Pages report is published.
Counts include the maintainer's visits and CI clones. This is repository
traffic, not website analytics. Do not add personal or client data.

## 🚦 Activation and evidence

Implementation is staged under #17. No successful live collection is claimed.
The `analytics` environment was created on 2026-10-29 and permits only `main`;
it has no secrets or variables. The first successful collection bootstraps the
protected data-only branch. Before activation: provision its dedicated credential
and obtain
owner authorization to integrate the workflow into main. A manual run from
a release branch is deliberately skipped.

After activation, record the main commit and workflow run URLs in #17:

1. Run the first collection and inspect all four CSV files and the step summary.
2. Rerun on the same day: identical payloads with a newer collection time
   advance observation watermarks only; changed payloads replace the day's
   values without duplicates. An exact replay including its timestamp must
   produce no commit (covered by offline tests).
3. Confirm previous dates remain intact and failed fetches leave the data
   branch unchanged. Offline regression tests cover replay, overlap and
   malformed or missing responses; those tests are not live-run evidence.
4. Keep #17 open until the first run and rerun are verified. Missing credentials
   or main integration are explicit external blockers, not completed controls.

## 🛡️ Branch protection

The workflow pushes to `traffic-history` directly, so its rules differ from
those of `main` and `release/**` ([GOVERNANCE.md](GOVERNANCE.md#-release-integration-and-synchronization)):

| Rule | `traffic-history` |
| --- | --- |
| Deletion | Blocked. |
| Force pushes | Blocked. |
| Pull request required | No: the workflow commits directly. |
| Required status checks | None. |
| Bypass | None. |

## 🩺 Failure diagnosis and recovery

Each run fails before anything is written if a response is missing or
invalid, and leaves the history unchanged. Read the failing step:

| Step and message | Cause | Action |
| --- | --- | --- |
| *Fetch*: `TRAFFIC_TOKEN is not set` | Secret missing, or the run is not in the `analytics` environment. | Follow the credential setup. |
| *Fetch*: HTTP 401 | Token expired or revoked. | Renew the token. |
| *Fetch*: HTTP 403 or 404 | Token lacks *Administration: read* on this repository. | Regenerate it with the settings above. |
| *Fetch*: HTTP 429 or 5xx after retries | Rate limit or GitHub outage. | Run it again later; the next run collects the same 14 days. |
| *Merge*: `ERROR: ...; the history was not changed` | The API returned an unexpected shape, or a history file no longer has the expected layout. | Inspect the response or the named file; a file edited by hand must keep its header and columns. |
| *Commit and push*: `Could not push the history` | `traffic-history` kept moving, or a rule rejected the push. | Check the branch's rules and recent commits, then run again. |
| *Check out or initialize traffic-history* fails | Remote query or checkout failed. | Inspect the error; a failed query never triggers empty initialization. If history was deleted, restore the last known commit before running again. |

A failed run can always be repeated: the merge is idempotent, and each
collection covers the last 14 days.

If the branch must be repaired, change it with a new commit made with
`python tools/traffic_history.py merge` or by hand, keeping every header.
`python tools/traffic_history.py init --data data` recreates missing files
with their headers and never overwrites an existing one.
