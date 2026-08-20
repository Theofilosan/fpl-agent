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