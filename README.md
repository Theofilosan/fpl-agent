# FPL Agent

A read-only Fantasy Premier League CLI for fixture rankings, player shortlists,
a legal starting XI, captain/vice-captain and bench suggestions, single-transfer
comparisons and observed price changes. It never changes your FPL account.

Scores are explainable heuristics, **not expected points**. Review suggestions
against current news and your actual squad before using them.

## Install

Requires Python 3.10+ and internet access for live data. No FPL login is needed
for public mode. The repository is private, so cloning needs GitHub access.

```sh
git clone https://github.com/Theofilosan/fpl-agent.git
cd fpl-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead. The old misspelled
`requirments.txt` remains a compatibility shim; use `requirements.txt`.

## Quick start: no token

```sh
python fpl.py --market-only
python fpl.py --entry YOUR_ENTRY_ID
python fpl.py --help
```

Pass your entry ID with `--entry`, or set `FPL_ENTRY_ID` (see below for how to find it). Default mode shows public **last published deadline
picks**, not the current squad. Transfers since that deadline are invisible.
The report warns about this. `--market-only` skips manager and squad access and
shows only player/fixture rankings. An entry without published picks gets market
rankings and a notice instead of an invented squad.

## Find your entry ID

Your entry ID (team ID) is a number that never changes and is not secret. Sign in at fantasy.premierleague.com, open the Points tab and read the address bar:

```text
https://fantasy.premierleague.com/entry/1234567/event/8
```

The number after `/entry/` is your entry ID (1234567 here). The number after `/event/` is the gameweek. In the mobile app the address bar is hidden, so use the site in a browser instead. Then either pass it each time or set it once:

```sh
python fpl.py --entry 1234567
export FPL_ENTRY_ID=1234567
```

## Get your token

Only `--current` needs a token, because the current squad comes from the logged-in `my-team` endpoint. The tool sends the token as the `X-API-Authorization` header, exactly as you store it. FPL has no public API for tokens, so this is manual and may change when the site changes:

1. Sign in at fantasy.premierleague.com in your browser.
2. Open the developer tools (F12) and go to the Network tab.
3. Reload the page or open the My Team page, and click a request to `fantasy.premierleague.com/api/` (for example `my-team`).
4. In the request headers, copy the value of `x-api-authorization`, including the word `Bearer`.
5. Put it in a `.env` file in the project root (this file is git-ignored):

```text
FPL_AUTH_TOKEN=Bearer eyJ...
```

Tokens expire, often within hours. If you get an authentication error, repeat the steps and replace the value. The token gives access to your account, so keep it out of issues, pull requests, screenshots and shell history, and never commit `.env`. If you shared it by accident, sign out of FPL everywhere to invalidate it. This steps list comes from how other community FPL tools describe it and has not been tested end to end with this project.

## Current squad: authenticated opt-in

Create an untracked `.env` file in the project root:

```text
FPL_AUTH_TOKEN=Bearer YOUR_TOKEN_HERE
```

Then:

```sh
python fpl.py --entry YOUR_ENTRY_ID --current
```

Supply a valid FPL token authorized for that entry. The CLI does not obtain,
refresh or store account passwords. Treat the token as a secret: never commit
or share it. Tokens are sent only to the my-team endpoint. Current mode stops
on authentication errors and **does not silently fall back** to old public picks.
Authenticated end-to-end access has not been live-tested in this build; API
contracts are covered by mocked tests.

## Single-transfer comparisons

Current squad picks must include selling prices. Confirm your current bank and
**remaining** free transfers explicitly:

```sh
python fpl.py --current --bank 1.5 --free-transfers 1
```

Bank is in £m, in 0.1 increments. Free transfers must be 0-5. Missing bank,
free transfers or selling prices skips comparisons. Public picks do not contain
selling prices, so public mode cannot produce budget-verified transfers.

Options are independent alternatives, **not a sequence**. They enforce same
position, affordability and at most three players per club, excluding owned,
doubtful and fixtureless targets. Selling price is not market price. Zero free
transfers means hold: this heuristic cannot justify a points hit. There is no
transfer execution command.

## Observed price changes

```sh
python fpl.py --market-only --snapshot .cache/prices.snapshot.json
```

First run saves a baseline. Repeat later to see observed rises/drops since that
run. This is **not a price prediction** and installs no polling or notifications.
Snapshots are local and ignored by Git. Use a separate path per season and do
not run concurrent processes against the same file. Corrupt JSON is not
silently overwritten.

## Offline runs and tests

```sh
python -m unittest discover -v
python fpl.py --offline local-data
python fpl.py --offline local-data --market-only
```

Put FPL-format `bootstrap.json`, `fixtures.json`, `manager.json` and `squad.json`
in the offline directory. Market-only needs just the first two. These are inputs
you supply, not sample files shipped in the repo. Offline data may be stale.
Tests use synthetic inputs and mocked HTTP, with no network or real credentials.
CI tests Python 3.10 and 3.12.

## Reading the report

- Fixture score preserves the original average `(6 - FDR) * 2` scale.
- Player scores blend 60% form and 40% points per game, multiplied by historical
  minutes share, a sub-450-minute sample penalty, availability and fixture ease.
- Minutes share uses completed team matches, not a full 38-game season. It is
  historical evidence, not a rotation forecast.
- Horizon score covers five gameweeks. Blanks count zero; doubles count twice.
  The separate next-GW score drives legal XI and captain choices.
- The bench goalkeeper is separate from the three ordered outfield substitutes.
  Captain and vice-captain are distinct starters. Forced risky starters warn.
- Transfer gain is in heuristic units, not FPL points. The 0.5 threshold is a
  shortlist filter, not proof that a move is worth making.

Form and points per game overlap; weights are hand chosen and uncalibrated.
FDR is coarse and injury flags can lag news. The squad-analysis table's
Limited/Rotation/Regular/Established labels describe completed-match minutes
share, not forecasts. Missing completed-match history remains a limited sample.

## Structure and remaining work

`fpl_api.py`: read-only HTTP. `data.py`: dataset normalization. `analysis.py`:
original fixture/squad analysis. `player_analysis.py`: player rankings.
`squad_strategy.py`: legal XI and armbands. `transfers.py`: one-transfer options.
`price_tracking.py`: local baselines. `display.py`: Rich output. `fpl.py`: CLI.

Working now: data access, fixture/player rankings, read-only lineup/captain
suggestions, financially constrained single-transfer comparisons, public/offline
modes and observed-price snapshots.

Still unimplemented from the original roadmap: calibrated/backtested expected
points, recent-match rotation models, xG/xA-driven recommendations, multi-transfer
optimization, chip/wildcard planning, external analyst inputs, natural-language
AI questions and predictive price alerts. No paid service or LLM is required.
