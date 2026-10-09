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
