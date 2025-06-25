#!/usr/bin/env python3
"""
Analysis script to process Pinto season data and track maximum negative twaDeltaB values.
Adds columns for maxNegativeTwaDeltaB and isNewMax to the CSV file.
"""

import csv
import os
from typing import List, Dict, Any

def process_season_data(input_file: str, output_file: str):
    """Process the season data to track maximum negative twaDeltaB values."""
    
    # Read the original CSV data
    rows = []
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    
    # Track maximum negative twaDeltaB since genesis
    max_negative_twa_delta_b = 0.0  # Start at 0 (no negative value yet)
    
    # Process each row and add new columns
    for row in rows:
        twa_delta_b = float(row['twaDeltaB']) if row['twaDeltaB'] else 0.0
        is_new_max = False
        
        # Apply the logic from requirements:
        # 1. If twaDeltaB > 0, keep maxNegativeTwaDeltaB unchanged
        # 2. If twaDeltaB < 0, check if it exceeds current max negative value
        if twa_delta_b < 0:
            # Check if this negative value is more negative than our current max
            if twa_delta_b < max_negative_twa_delta_b:
                max_negative_twa_delta_b = twa_delta_b
                is_new_max = True
        
        # Add new columns to the row
        row['maxNegativeTwaDeltaB'] = max_negative_twa_delta_b
        row['isNewMaxTwaDeltaB'] = is_new_max
    
    # Write the updated data to a new CSV file
    if rows:
        fieldnames = list(rows[0].keys())
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"Processed {len(rows)} seasons")
    print(f"Maximum negative twaDeltaB found: {max_negative_twa_delta_b}")
    print(f"Updated data saved to: {output_file}")

def main():
    """Main function to process the Pinto season data."""
    input_file = "pinto_season_data.csv"
    output_file = "pinto_season_data_with_max_negative.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run fetch_season_data.py first.")
        return
    
    process_season_data(input_file, output_file)

if __name__ == "__main__":
    main()