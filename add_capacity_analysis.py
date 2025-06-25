#!/usr/bin/env python3
"""
Script to add capacity analysis columns to the CSV file.
Calculates capacity as maxNegativeTwaDeltaB/S for S values from 100 to 1000 (step 100).
"""

import csv
import os

def add_capacity_columns(input_file: str, output_file: str):
    """Add capacity columns for different S values to the CSV file."""
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run analysis.py first.")
        return
    
    # Read the original CSV data
    rows = []
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    
    # Process each row and add capacity columns
    for row in rows:
        max_negative_twa_delta_b = float(row['maxNegativeTwaDeltaB']) if row['maxNegativeTwaDeltaB'] else 0.0
        
        # Truncate maxNegativeTwaDeltaB to 3 decimal places
        row['maxNegativeTwaDeltaB'] = round(max_negative_twa_delta_b, 3)
        
        # Also truncate other numeric columns to 3 decimal places
        for col in ['twaDeltaB', 'twaPrice', 'l2sr', 'podRate']:
            if col in row and row[col]:
                try:
                    row[col] = round(float(row[col]), 3)
                except (ValueError, TypeError):
                    pass
        
        # Add capacity columns for S values from 100 to 1000 (step 100)
        for s_value in range(100, 1100, 100):  # 100, 200, ..., 1000
            column_name = f'Capacity_at_Smin_{s_value}'
            
            # Calculate capacity = abs(maxNegativeTwaDeltaB) / S (capacity should be positive)
            if s_value != 0:
                capacity = abs(max_negative_twa_delta_b) / s_value
            else:
                capacity = 0.0
            
            # Truncate to 3 decimal places
            row[column_name] = round(capacity, 3)
    
    # Write the updated data to output file
    if rows:
        fieldnames = list(rows[0].keys())
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"Added capacity columns for S values: 100, 200, 300, ..., 1000")
    print(f"Processed {len(rows)} seasons")
    print(f"Updated data saved to: {output_file}")
    
    # Show sample of capacity calculations for the final season
    if rows:
        final_row = rows[-1]
        print(f"\nSample capacity calculations for Season {final_row['Season']}:")
        print(f"maxNegativeTwaDeltaB: {final_row['maxNegativeTwaDeltaB']}")
        for s_value in [100, 500, 1000]:
            capacity_col = f'Capacity_at_Smin_{s_value}'
            print(f"  {capacity_col}: {final_row[capacity_col]}")

def main():
    """Main function to add capacity analysis to the CSV file."""
    input_file = "pinto_season_data_with_max_negative.csv"
    output_file = "pinto_season_data_with_capacity_analysis.csv"
    
    add_capacity_columns(input_file, output_file)

if __name__ == "__main__":
    main()