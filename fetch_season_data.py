#!/usr/bin/env python3
"""
Standalone script to fetch season data from Pinto subgraphs and export to CSV.
Fetches data for all seasons since deployment (~5200 seasons).
"""

import requests
import csv
import time
from typing import Dict, List, Optional

# Subgraph endpoints
PINTO_SUBGRAPH = "https://graph.pinto.money/pinto"
PINTOSTALK_SUBGRAPH = "https://graph.pinto.money/pintostalk"

# Query templates
PINTO_QUERY = """
{
  seasons(first: %d, skip: %d, orderBy: season, orderDirection: asc) {
    season
    beanHourlySnapshot {
      twaDeltaB
      twaPrice
      l2sr
    }
  }
}
"""

PINTOSTALK_QUERY = """
{
  fieldHourlySnapshots(
    first: %d, 
    skip: %d, 
    orderBy: season, 
    orderDirection: asc,
    where: {field: "0xd1a0d188e861ed9d15773a2f3574a2e94134ba8f"}
  ) {
    season
    podRate
  }
}
"""

def query_subgraph(endpoint: str, query: str, retries: int = 3) -> Optional[Dict]:
    """Query a subgraph with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.post(
                endpoint,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if "errors" in data:
                print(f"GraphQL errors: {data['errors']}")
                return None
                
            return data.get("data", {})
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            
    return None

def fetch_all_pinto_data() -> Dict[int, Dict]:
    """Fetch all season data from Pinto subgraph with pagination."""
    print("Fetching data from Pinto subgraph...")
    all_seasons = {}
    skip = 0
    batch_size = 1000
    
    while True:
        query = PINTO_QUERY % (batch_size, skip)
        data = query_subgraph(PINTO_SUBGRAPH, query)
        
        if not data or "seasons" not in data:
            print(f"No more data or error at skip={skip}")
            break
            
        seasons = data["seasons"]
        if not seasons:
            print(f"No seasons returned at skip={skip}")
            break
            
        print(f"Fetched {len(seasons)} seasons from Pinto (skip={skip})")
        
        for season in seasons:
            season_num = int(season["season"])
            snapshot = season.get("beanHourlySnapshot")
            
            if snapshot:
                all_seasons[season_num] = {
                    "twaDeltaB": snapshot.get("twaDeltaB"),
                    "twaPrice": snapshot.get("twaPrice"),
                    "l2sr": snapshot.get("l2sr")
                }
        
        if len(seasons) < batch_size:
            break
            
        skip += batch_size
        time.sleep(0.1)  # Rate limiting
    
    print(f"Total seasons from Pinto: {len(all_seasons)}")
    return all_seasons

def fetch_all_pintostalk_data() -> Dict[int, Dict]:
    """Fetch all field data from Pintostalk subgraph with pagination."""
    print("Fetching data from Pintostalk subgraph...")
    all_field_data = {}
    skip = 0
    batch_size = 1000
    
    while True:
        query = PINTOSTALK_QUERY % (batch_size, skip)
        data = query_subgraph(PINTOSTALK_SUBGRAPH, query)
        
        if not data or "fieldHourlySnapshots" not in data:
            print(f"No more data or error at skip={skip}")
            break
            
        snapshots = data["fieldHourlySnapshots"]
        if not snapshots:
            print(f"No snapshots returned at skip={skip}")
            break
            
        print(f"Fetched {len(snapshots)} field snapshots from Pintostalk (skip={skip})")
        
        for snapshot in snapshots:
            season_num = int(snapshot["season"])
            pod_rate = snapshot.get("podRate")
            # Convert pod rate to percentage by multiplying by 100
            if pod_rate is not None:
                pod_rate = float(pod_rate) * 100
            
            all_field_data[season_num] = {
                "podRate": pod_rate
            }
        
        if len(snapshots) < batch_size:
            break
            
        skip += batch_size
        time.sleep(0.1)  # Rate limiting
    
    print(f"Total field snapshots from Pintostalk: {len(all_field_data)}")
    return all_field_data

def merge_and_export_data(pinto_data: Dict[int, Dict], pintostalk_data: Dict[int, Dict], output_file: str):
    """Merge data from both subgraphs and export to CSV."""
    print("Merging data and exporting to CSV...")
    
    # Get all unique seasons
    all_seasons = set(pinto_data.keys()) | set(pintostalk_data.keys())
    
    # Sort seasons
    sorted_seasons = sorted(all_seasons)
    
    # Filter out first three seasons (0, 1, 2) as they add noise
    filtered_seasons = [season for season in sorted_seasons if season > 3]
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Season', 'twaDeltaB', 'twaPrice', 'l2sr', 'podRate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for season in filtered_seasons:
            pinto_season = pinto_data.get(season, {})
            pintostalk_season = pintostalk_data.get(season, {})
            
            row = {
                'Season': season,
                'twaDeltaB': pinto_season.get('twaDeltaB', ''),
                'twaPrice': pinto_season.get('twaPrice', ''),
                'l2sr': pinto_season.get('l2sr', ''),
                'podRate': pintostalk_season.get('podRate', '')
            }
            
            writer.writerow(row)
    
    print(f"Data exported to {output_file}")
    print(f"Total seasons exported: {len(filtered_seasons)}")

def main():
    """Main function to orchestrate the data fetching and export."""
    print("Starting Pinto season data collection...")
    
    # Fetch data from both subgraphs
    pinto_data = fetch_all_pinto_data()
    pintostalk_data = fetch_all_pintostalk_data()
    
    # Export to CSV
    output_file = "pinto_season_data.csv"
    merge_and_export_data(pinto_data, pintostalk_data, output_file)
    
    print("Data collection complete!")

if __name__ == "__main__":
    main()