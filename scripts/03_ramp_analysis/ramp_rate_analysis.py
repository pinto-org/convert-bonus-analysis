#!/usr/bin/env python3
"""
Ramp rate analysis for convert capacity based on twaPrice and delta_d values.
Calculates effective D_t and seasons to max/min capacity for different delta_d percentages.
"""

import pandas as pd
import numpy as np
import csv
import os

def calculate_ramp_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ramp rate analysis for different delta_d values.
    
    Formula for D_t:
    - If Bonus Convert Capacity Reached: min(1, D_{t-1} + Δd × P_{t-1})
    - If Bonus Convert Capacity Almost reached: D_{t-1}
    - Else: max(0.01, D_{t-1} - 0.01 / (Δd × P_{t-1}))
    
    For this analysis, we'll focus on the increase/decrease rates.
    """
    
    # Define delta_d values: 0.1% to 5% with 0.25% steps after 0.1%
    delta_d_values = [0.001]  # 0.1%
    delta_d_values.extend([i/100 for i in np.arange(0.25, 5.25, 0.25)])  # 0.25% to 5%
    
    print(f"Analyzing {len(delta_d_values)} delta_d values: {[f'{d*100:.2f}%' for d in delta_d_values]}")
    
    # Create a copy of the dataframe to add new columns
    result_df = df.copy()
    
    for delta_d in delta_d_values:
        delta_d_pct = f"{delta_d*100:.2f}".replace('.', '_')
        
        # Calculate effective increase rate (when capacity is reached)
        # Increase rate: delta_d × twaPrice
        increase_rate_col = f"effective_increase_rate_dd_{delta_d_pct}pct"
        result_df[increase_rate_col] = delta_d * result_df['twaPrice']
        
        # Calculate effective decrease rate (when capacity not reached)
        # Decrease rate: 0.01 / (delta_d × twaPrice)
        decrease_rate_col = f"effective_decrease_rate_dd_{delta_d_pct}pct"
        result_df[decrease_rate_col] = 0.01 / (delta_d * result_df['twaPrice'])
        
        # Calculate seasons to maximum capacity (from D_t = 0.01 to D_t = 1)
        # Seasons = (1 - 0.01) / increase_rate = 0.99 / increase_rate
        seasons_to_max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        result_df[seasons_to_max_col] = 0.99 / result_df[increase_rate_col]
        
        # Calculate seasons to minimum capacity (from D_t = 1 to D_t = 0.01)
        # This is more complex as it's not linear, but we can approximate
        # Seasons ≈ (1 - 0.01) / decrease_rate = 0.99 / decrease_rate
        seasons_to_min_col = f"seasons_to_min_capacity_dd_{delta_d_pct}pct"
        result_df[seasons_to_min_col] = 0.99 / result_df[decrease_rate_col]
        
        # Round to 3 decimal places
        result_df[increase_rate_col] = result_df[increase_rate_col].round(3)
        result_df[decrease_rate_col] = result_df[decrease_rate_col].round(3)
        result_df[seasons_to_max_col] = result_df[seasons_to_max_col].round(3)
        result_df[seasons_to_min_col] = result_df[seasons_to_min_col].round(3)
    
    return result_df

def analyze_historical_ramp_patterns(df: pd.DataFrame):
    """Analyze historical patterns to suggest reasonable ramp rates."""
    
    print("\n=== Historical Ramp Rate Analysis ===")
    
    # Analyze twaPrice statistics
    price_stats = df['twaPrice'].describe()
    print(f"\nTwaPrice Statistics:")
    print(f"  Min: {price_stats['min']:.3f}")
    print(f"  25th percentile: {price_stats['25%']:.3f}")
    print(f"  Median: {price_stats['50%']:.3f}")
    print(f"  75th percentile: {price_stats['75%']:.3f}")
    print(f"  Max: {price_stats['max']:.3f}")
    print(f"  Mean: {price_stats['mean']:.3f}")
    
    # Find key price levels for analysis
    key_prices = [
        price_stats['min'],
        price_stats['25%'],
        price_stats['50%'],
        price_stats['75%'],
        price_stats['max']
    ]
    
    print(f"\n=== Ramp Rate Analysis at Key Price Levels ===")
    
    delta_d_values = [0.001, 0.0025, 0.005, 0.0075, 0.01, 0.02, 0.03, 0.04, 0.05]
    
    for i, price in enumerate(key_prices):
        price_label = ['Min', '25th %ile', 'Median', '75th %ile', 'Max'][i]
        print(f"\n--- At {price_label} Price ({price:.3f}) ---")
        
        for delta_d in delta_d_values:
            increase_rate = delta_d * price
            decrease_rate = 0.01 / (delta_d * price)
            seasons_to_max = 0.99 / increase_rate
            seasons_to_min = 0.99 / decrease_rate
            
            print(f"Δd={delta_d*100:4.2f}%: +{increase_rate*100:6.3f}%/season, -{decrease_rate*100:6.3f}%/season, "
                  f"Max in {seasons_to_max:6.1f} seasons, Min in {seasons_to_min:6.1f} seasons")
    
    # Suggest reasonable ranges
    print(f"\n=== Recommendations ===")
    median_price = price_stats['50%']
    
    print(f"Based on median twaPrice of {median_price:.3f}:")
    print(f"")
    print(f"For FAST ramping (50-100 seasons to max):")
    target_seasons = [50, 75, 100]
    for target in target_seasons:
        required_delta_d = 0.99 / (target * median_price)
        print(f"  {target} seasons → Δd ≈ {required_delta_d*100:.2f}%")
    
    print(f"")
    print(f"For MODERATE ramping (100-200 seasons to max):")
    target_seasons = [100, 150, 200]
    for target in target_seasons:
        required_delta_d = 0.99 / (target * median_price)
        print(f"  {target} seasons → Δd ≈ {required_delta_d*100:.2f}%")
    
    print(f"")
    print(f"For SLOW ramping (200-500 seasons to max):")
    target_seasons = [200, 300, 500]
    for target in target_seasons:
        required_delta_d = 0.99 / (target * median_price)
        print(f"  {target} seasons → Δd ≈ {required_delta_d*100:.2f}%")

def save_ramp_analysis(df: pd.DataFrame, output_file: str):
    """Save the ramp rate analysis to CSV."""
    
    df.to_csv(output_file, index=False)
    print(f"\nRamp rate analysis saved to: {output_file}")
    print(f"Total columns: {len(df.columns)}")
    
    # Show sample of new columns
    ramp_columns = [col for col in df.columns if 'dd_' in col]
    print(f"Added {len(ramp_columns)} ramp rate analysis columns")
    
    if ramp_columns:
        print(f"\nSample ramp rate data for Season {df['Season'].iloc[-1]}:")
        sample_row = df.iloc[-1]
        print(f"twaPrice: {sample_row['twaPrice']}")
        
        # Show a few example calculations
        for col in ramp_columns[:8]:  # First 8 columns as example
            print(f"  {col}: {sample_row[col]}")

def main():
    """Main function for ramp rate analysis."""
    input_file = "../../data/pinto_season_data_with_capacity_analysis.csv"
    output_file = "../../data/pinto_season_data_with_ramp_analysis.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run add_capacity_analysis.py first.")
        return
    
    print("Loading capacity analysis data...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} seasons of data")
    
    print("\nCalculating ramp rates for different delta_d values...")
    result_df = calculate_ramp_rates(df)
    
    print("\nAnalyzing historical patterns...")
    analyze_historical_ramp_patterns(df)
    
    print(f"\nSaving results...")
    save_ramp_analysis(result_df, output_file)
    
    print(f"\nRamp rate analysis completed!")

if __name__ == "__main__":
    main()