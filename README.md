# FPL Agent

A Python-based Fantasy Premier League analytics and decision-support tool.

The goal of this project is to build an intelligent FPL agent that can analyse a manager's squad, evaluate upcoming fixtures and player performance, and eventually provide data-driven recommendations for transfers, captaincy, and overall squad strategy.

The project is being developed incrementally, starting with a reliable FPL data layer and gradually adding more advanced analytics and AI capabilities.

---

## Current Status

The project currently provides:

- FPL API integration
- FPL player data
- Premier League team data
- Fixture data
- Gameweek information
- Manager information
- Current squad information
- Structured fixture dataset
- Upcoming fixture analysis
- Fixture Score calculation
- Fixture ranking for all 20 teams
- Color-coded terminal output using Rich

---

## Project Architecture

The current architecture separates API communication, data processing, analytics, and presentation.

```text
                    FPL API
                       │
                       ▼
                 fpl_api.py
                       │
                       ▼
                    data.py
                       │
                       ▼
                 analysis.py
                       │
                       ▼
                  display.py
                       │
                       ▼
                   Terminal
```

The main entry point is `fpl.py`, which orchestrates the different components.

---

## Project Structure

```text
fpl-agent/
│
├── fpl.py
├── fpl_api.py
├── data.py
├── analysis.py
├── display.py
│
├── README.md
├── requirements.txt
├── .env
└── .gitignore
```

### `fpl.py`

Main application entry point.

Responsible for orchestrating:

- Loading FPL data
- Building datasets
- Running analysis
- Displaying results

### `fpl_api.py`

Handles communication with the Fantasy Premier League API.

Currently provides functions for:

- Bootstrap data
- Fixtures
- Manager information
- Current squad

### `data.py`

Transforms raw API responses into structured datasets.

Currently handles:

- Team lookup maps
- Player lookup maps
- Fixture dataset creation
- Team fixture retrieval

### `analysis.py`

Contains the analytical logic.

Currently includes:

- Fixture Score calculation
- Fixture ranking for all teams

This module will eventually contain the majority of the FPL decision-making logic.

### `display.py`

Handles terminal presentation using Rich.

Currently provides:

- Fixture tables
- Fixture difficulty colors
- Fixture Score rankings
- Player information
- Manager information
- Squad information

---

# Installation

## Requirements

- Python 3.10+
- Internet connection
- A Fantasy Premier League account

---

## Clone the Repository

```bash
git clone <repository-url>
cd fpl-agent
```

---

## Create a Virtual Environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

The default mode uses public last-deadline picks and does not require a login.
These are not the current squad: transfers since the deadline are invisible.
Use `python fpl.py --market-only` for fixture/player rankings only.

Authenticated current squad access is opt-in with `python fpl.py --current`.
The project uses environment variables for that access.

Create a `.env` file in the project root:

```text
FPL_AUTH_TOKEN=Bearer YOUR_TOKEN_HERE
```

Do **not** commit the `.env` file to Git.

The repository should contain `.env` in `.gitignore`.

---

# Usage

Run the application with:

```bash
python fpl.py
# Require authenticated current squad instead:
python fpl.py --current
```

The application will:

1. Load the FPL bootstrap data
2. Load all fixtures
3. Build structured datasets
4. Determine the current/next Gameweek
5. Analyse upcoming fixtures
6. Calculate Fixture Scores
7. Rank all 20 Premier League teams
8. Load manager information
9. Load public last-deadline picks (or current squad with --current)
10. Display the results in the terminal

---

# Fixture Analysis

One of the first analytical components of the project is the **Fixture Score**.

The Fantasy Premier League API provides a fixture difficulty rating from `1` to `5`.

The project converts this into a positive score:

| FPL Difficulty | Internal Score |
|---------------:|---------------:|
| 1 | 5 |
| 2 | 4 |
| 3 | 3 |
| 4 | 2 |
| 5 | 1 |

The average score of the selected upcoming fixtures is then converted to a `0-10` scale.

### Example

If a team has the following next five fixtures:

```text
GW1 → Difficulty 2
GW2 → Difficulty 4
GW3 → Difficulty 4
GW4 → Difficulty 3
GW5 → Difficulty 3
```

The converted scores are:

```text
4, 2, 2, 3, 3
```

Average:

```text
2.8 / 5
```

Final Fixture Score:

```text
5.6 / 10
```

The Fixture Score is currently based only on the FPL-provided fixture difficulty and is intended as a first analytical layer rather than a final predictive model.

---

# Terminal Output

The project uses Rich to make the terminal output easier to read.

Fixture difficulty is color-coded:

- 🟢 Green → Easy
- 🟡 Yellow → Medium
- 🔴 Red → Difficult

Fixture Scores are also color-coded based on their overall value.

Example:

```text
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Rank ┃ Team                 ┃ Score    ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│    1 │ Arsenal              │ 8.2/10   │
│    2 │ Chelsea              │ 7.8/10   │
│    3 │ Liverpool            │ 7.6/10   │
│  ... │ ...                  │ ...      │
└──────┴──────────────────────┴──────────┘
```

---

# Roadmap

The project is being developed in several stages.

## Phase 1 — FPL Data Layer

- [x] Connect to FPL API
- [x] Retrieve player data
- [x] Retrieve team data
- [x] Retrieve fixture data
- [x] Retrieve Gameweek information
- [x] Retrieve manager information
- [x] Retrieve current squad
- [x] Build structured fixture dataset

## Phase 2 — Fixture Analysis

- [x] Calculate Fixture Score
- [x] Analyse upcoming fixtures
- [x] Rank all 20 teams
- [x] Color-code fixture difficulty
- [x] Color-code Fixture Scores

## Phase 3 — Player Analysis

- [ ] Player performance scoring
- [ ] Recent form analysis
- [ ] Minutes/rotation probability
- [ ] Expected goals (xG)
- [ ] Expected assists (xA)
- [ ] Defensive statistics
- [ ] Player value analysis
- [ ] Ownership analysis

## Phase 4 — Transfer Engine

- [ ] Analyse current squad
- [ ] Identify weak positions
- [ ] Find potential replacements
- [ ] Compare players
- [ ] Calculate Transfer Score
- [ ] Recommend transfers
- [ ] Consider available budget
- [ ] Consider free transfers
- [ ] Consider transfer hits

## Phase 5 — Squad Strategy

- [ ] Captain recommendations
- [ ] Vice-captain recommendations
- [ ] Starting XI recommendations
- [ ] Bench recommendations
- [ ] Bench Boost strategy
- [ ] Triple Captain strategy
- [ ] Wildcard strategy
- [ ] Free Hit strategy
- [ ] Fixture swing detection

## Phase 6 — External FPL Intelligence

The agent will eventually incorporate information and recommendations from external FPL analysts and content creators.

Potential sources include:

- FPL Harry
- FPL Raptor
- Let's Talk FPL
- Other relevant FPL analysts and communities

The goal will not be to blindly follow external recommendations, but to compare them with the project's own data and analysis.

Example:

```text
FPL Agent Analysis
        │
        ├── Statistical Analysis
        ├── Fixture Analysis
        ├── Player Data
        └── External FPL Opinions
                    │
                    ▼
             Combined Analysis
                    │
                    ▼
             Recommendation
```

## Phase 7 — AI FPL Agent

The final goal is to turn the analytics engine into an AI-powered decision-support agent.

The agent should eventually be able to answer questions such as:

> Who should I transfer in this Gameweek?

> Should I sell Haaland?

> Who should I captain?

> Should I save my transfer?

> Which players should I target over the next 5 Gameweeks?

> Is it worth taking a -4 hit?

> Should I use a Wildcard now or wait?

Recommendations should be supported by the underlying data and explain **why** a recommendation was made.

---

# Long-Term Architecture

The intended architecture will eventually look more like:

```text
                       ┌─────────────────┐
                       │    FPL API      │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Layer    │
                       └────────┬────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
           Fixtures         Players          Squad
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Analysis Engine │
                       └────────┬────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        Fixture Score      Player Score     Transfer Score
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  AI Agent Layer │
                       └────────┬────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
          Transfers          Captain          Strategy
```

External FPL content and analysis will eventually feed into the AI layer as an additional source of information.

---

# Design Principles

The project is being developed around a few principles:

### Data-driven decisions

Recommendations should be based on measurable data rather than intuition alone.

### Explainable recommendations

The agent should explain why a player or transfer is being recommended.

### Modular architecture

API communication, data processing, analytics, and presentation should remain separated.

### Incremental development

New functionality should be added and tested before moving to the next layer.

### Independent analysis

External FPL recommendations should be treated as an additional source of information rather than automatically accepted as correct.

---

# Disclaimer

This project is an experimental analytics and decision-support tool for Fantasy Premier League.

Fantasy football outcomes are inherently uncertain. Any recommendations generated by the project are analytical suggestions and are not guaranteed to improve performance or rank.

---

# License

License information will be added as the project matures.
