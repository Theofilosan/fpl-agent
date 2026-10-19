# Development

Install with `pip install -r requirements.txt`. The old `requirments.txt`
spelling remains as a compatibility shim.

Run offline tests with `python -m unittest discover -v`. Tests mock HTTP and
never use real FPL tokens. CI runs on Python 3.10 and 3.12.

The API layer makes read-only requests. Public endpoints get no private token;
only `my-team` receives `X-API-Authorization`. Redirects are rejected to avoid
sending credentials elsewhere. HTTP 429 is not retried automatically. Errors
do not echo response bodies or credential-bearing network details.

Current squad access still requires `FPL_AUTH_TOKEN` in an untracked `.env`.
No transfer, captaincy or account writes are implemented.

## Player scoring

`player_analysis.py` ranks raw bootstrap players. The score blends 60% form and
40% points per game, scales by completed-team-match minutes share, damps samples
below 450 minutes, and multiplies by availability and `(6 - FDR) / 3` per fixture.
Horizon totals divide by the requested number of gameweeks: blanks count zero
and doubles count twice. Next-GW scores are kept separate for later lineup work.

These are heuristic units, not expected points. Weights are hand chosen, form
and PPG overlap, and the historical minutes share is not a rotation forecast.
No history produces zero evidence, not an invented prior. Injuries can lag API
news. The public shortlist excludes doubtful or unavailable players.

## Lineup and captain choices

`squad_strategy.py` validates a 15-player squad, position counts and club limits,
then searches legal formations to maximize next-gameweek heuristic score.
Captain and vice-captain are distinct starters; fully fit non-blank candidates
are preferred. The goalkeeper substitute is separate from the ordered outfield
bench. Forced risky starters and an empty captain pool produce warnings.
This is not an auto-sub simulation or a prediction. No account changes are made.

## Single-transfer alternatives

Run `python fpl.py --bank 1.5 --free-transfers 1` to confirm current bank and
remaining free transfers. Selling prices come from authenticated my-team picks,
never market price. Missing financials skip comparisons. Each option is an
independent same-position transfer within budget and the club limit, excluding
owned, doubtful and fixtureless targets. A gain above 0.5 heuristic units is a
shortlist threshold, not expected points. Zero free transfers means hold;
no points-hit, multi-transfer or chip recommendation is made. The CLI has no
write endpoints and cannot execute a transfer. Recheck news before acting.

## Public and offline CLI

The default `python fpl.py --entry YOUR_ENTRY_ID` now uses last published deadline
picks, clearly labelled as NOT the current squad. Transfers since that deadline
are invisible. `--current` explicitly requires authenticated current picks and
never falls back. `--market-only` skips all manager/squad access.

Use `--offline local-data` with bootstrap.json, fixtures.json, manager.json and
squad.json in FPL response formats; market-only needs just the first two.
Offline freshness is unverified. Public picks contain no selling prices, so
transfer comparisons remain skipped. The tool never infers financials from
public bank or team value. No login is required for public modes.

## Observed price changes

Run `python fpl.py --market-only --snapshot .cache/prices.snapshot.json`.
The first run saves a baseline; later runs show observed rises/drops since the
previous run, not predictions. No polling, schedule, notifications or external
price site is installed. Snapshots are local and ignored by Git. Corrupt JSON
is not overwritten. Use a separate path for each season; the snapshot has no
season identifier. Don't use two simultaneous processes on the same file.
