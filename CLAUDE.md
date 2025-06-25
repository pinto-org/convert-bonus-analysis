# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a Python data analysis project focused on fetching and analyzing DeFi protocol data from Pinto subgraphs.

### Core Components

- **fetch_season_data.py**: Standalone script that fetches season data from Pinto subgraphs:
  - Pinto subgraph: Fetches season snapshots with twaDeltaB, twaPrice, and l2sr metrics
  - Pintostalk subgraph: Fetches field hourly snapshots with podRate data and silo hourly snapshots with crop_ratio (beanToMaxLpGpPerBdvRatio)
  - Merges data from all sources and exports to CSV, filtering out the first 3 seasons (0-3) as noise
  - Implements pagination and retry logic for robust data fetching

- **get_max_twadeltab.py**: Tracks maximum negative twaDeltaB values since genesis and identifies when new maximums occur

- **pinto_season_data.csv**: Generated output containing merged season data with columns:
  - Season, twaDeltaB, twaPrice, l2sr, podRate, crop_ratio

### Subgraph Endpoints

- Pinto: `https://graph.pinto.money/pinto`
- Pintostalk: `https://graph.pinto.money/pintostalk`

## Commands

To fetch fresh data:
```bash
python3 fetch_season_data.py
```

To run analysis (when implemented):
```bash
python3 analysis.py
```

## Data Flow

1. Script queries both subgraphs with pagination (1000 records per batch)
2. Applies exponential backoff retry logic for failed requests
3. Merges data by season number
4. Filters out seasons 0-3 to reduce noise
5. Exports to CSV with all relevant metrics

The fetched data covers approximately 5200+ seasons since deployment.