#!/usr/bin/env python3
"""
Synthetic price extension module for ramp rate analysis.
Generates synthetic price data points to extend analysis to lower price ranges.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional

def generate_synthetic_price_grid(
    min_price: float = 0.25,
    max_price: Optional[float] = None,
    step_size: float = 0.01,
    historical_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Generate synthetic price grid for ramp rate analysis.
    
    Args:
        min_price: Minimum price to include (default: 0.25)
        max_price: Maximum price for synthetic data (default: min of historical data)
        step_size: Price increment step (default: 0.01)
        historical_df: Historical data to determine max_price if not provided
    
    Returns:
        DataFrame with synthetic price points and metadata
    """
    
    if max_price is None:
        if historical_df is not None:
            max_price = historical_df['twaPrice'].min()
        else:
            max_price = 0.52  # Conservative default just below typical minimum
    
    # Generate price points
    price_points = np.arange(min_price, max_price, step_size)
    
    # Round to avoid floating point precision issues
    price_points = np.round(price_points, 3)
    
    # Create synthetic dataframe
    synthetic_df = pd.DataFrame({
        'Season': range(-len(price_points), 0),  # Negative seasons for synthetic data
        'twaPrice': price_points,
        'data_source': 'synthetic',
        'twaDeltaB': 0.0,  # Not relevant for synthetic data
        'l2sr': 0.0,       # Not relevant for synthetic data  
        'podRate': 0.0,    # Not relevant for synthetic data
    })
    
    print(f"Generated {len(synthetic_df)} synthetic price points")
    print(f"Price range: {min_price:.3f} to {max_price:.3f} (step: {step_size})")
    
    return synthetic_df

def calculate_synthetic_ramp_rates(
    synthetic_df: pd.DataFrame,
    delta_d_values: Optional[List[float]] = None
) -> pd.DataFrame:
    """
    Calculate ramp rate metrics for synthetic price data.
    
    Args:
        synthetic_df: DataFrame with synthetic price data
        delta_d_values: List of delta_d values to analyze (default: 0.1% to 3.0%)
    
    Returns:
        DataFrame with ramp rate calculations added
    """
    
    if delta_d_values is None:
        # Default: 0.1% to 3.0% in 0.1% steps
        delta_d_values = [i/1000 for i in range(1, 31)]
    
    result_df = synthetic_df.copy()
    
    print(f"Calculating ramp rates for {len(delta_d_values)} delta_d values")
    
    for delta_d in delta_d_values:
        delta_d_pct = f"{delta_d*100:.2f}".replace('.', '_')
        
        # Calculate effective increase rate (when capacity is reached)
        increase_rate_col = f"effective_increase_rate_dd_{delta_d_pct}pct"
        result_df[increase_rate_col] = delta_d * result_df['twaPrice']
        
        # Calculate effective decrease rate (when capacity not reached)
        decrease_rate_col = f"effective_decrease_rate_dd_{delta_d_pct}pct"
        result_df[decrease_rate_col] = 0.01 / (delta_d * result_df['twaPrice'])
        
        # Calculate seasons to maximum capacity (from D_t = 0.01 to D_t = 1)
        seasons_to_max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        result_df[seasons_to_max_col] = 0.99 / result_df[increase_rate_col]
        
        # Calculate seasons to minimum capacity (from D_t = 1 to D_t = 0.01)
        seasons_to_min_col = f"seasons_to_min_capacity_dd_{delta_d_pct}pct"
        result_df[seasons_to_min_col] = 0.99 / result_df[decrease_rate_col]
        
        # Round to 3 decimal places
        result_df[increase_rate_col] = result_df[increase_rate_col].round(3)
        result_df[decrease_rate_col] = result_df[decrease_rate_col].round(3)
        result_df[seasons_to_max_col] = result_df[seasons_to_max_col].round(3)
        result_df[seasons_to_min_col] = result_df[seasons_to_min_col].round(3)
    
    return result_df

def create_extended_dataset(
    historical_df: pd.DataFrame,
    include_synthetic: bool = True,
    min_synthetic_price: float = 0.25,
    price_step: float = 0.01
) -> Tuple[pd.DataFrame, dict]:
    """
    Create extended dataset combining historical and synthetic data.
    
    Args:
        historical_df: Historical data with ramp rate analysis
        include_synthetic: Whether to include synthetic data (default: True)
        min_synthetic_price: Minimum price for synthetic data (default: 0.25)
        price_step: Step size for synthetic prices (default: 0.01)
    
    Returns:
        Tuple of (extended_dataframe, metadata_dict)
    """
    
    # Add data source marker to historical data
    historical_df = historical_df.copy()
    if 'data_source' not in historical_df.columns:
        historical_df['data_source'] = 'historical'
    
    metadata = {
        'historical_count': len(historical_df),
        'historical_price_range': (historical_df['twaPrice'].min(), historical_df['twaPrice'].max()),
        'synthetic_count': 0,
        'synthetic_price_range': None,
        'total_count': len(historical_df)
    }
    
    if not include_synthetic:
        return historical_df, metadata
    
    # Generate synthetic data
    synthetic_df = generate_synthetic_price_grid(
        min_price=min_synthetic_price,
        max_price=historical_df['twaPrice'].min(),
        step_size=price_step,
        historical_df=historical_df
    )
    
    # Calculate ramp rates for synthetic data
    synthetic_with_ramp = calculate_synthetic_ramp_rates(synthetic_df)
    
    # Align columns between historical and synthetic data
    historical_cols = set(historical_df.columns)
    synthetic_cols = set(synthetic_with_ramp.columns)
    
    # Add missing columns to synthetic data (fill with appropriate defaults)
    missing_in_synthetic = historical_cols - synthetic_cols
    for col in missing_in_synthetic:
        if 'dd_' in col:  # Ramp rate columns should already be calculated
            continue
        elif col in ['maxNegativeTwaDeltaB', 'isNewMaxTwaDeltaB']:
            synthetic_with_ramp[col] = False
        elif col.startswith('Capacity_at_Smin_'):
            synthetic_with_ramp[col] = 0.0
        else:
            synthetic_with_ramp[col] = 0.0
    
    # Add missing columns to historical data (shouldn't happen, but defensive)
    missing_in_historical = synthetic_cols - historical_cols
    for col in missing_in_historical:
        if col == 'data_source':
            continue  # Already added
        historical_df[col] = 0.0
    
    # Ensure column order consistency
    all_columns = sorted(list(set(historical_df.columns) | set(synthetic_with_ramp.columns)))
    historical_df = historical_df.reindex(columns=all_columns, fill_value=0.0)
    synthetic_with_ramp = synthetic_with_ramp.reindex(columns=all_columns, fill_value=0.0)
    
    # Combine datasets
    extended_df = pd.concat([synthetic_with_ramp, historical_df], 
                           ignore_index=True, 
                           sort=False)
    
    # Sort by price for logical ordering
    extended_df = extended_df.sort_values('twaPrice').reset_index(drop=True)
    
    # Update metadata
    metadata.update({
        'synthetic_count': len(synthetic_with_ramp),
        'synthetic_price_range': (synthetic_with_ramp['twaPrice'].min(), 
                                 synthetic_with_ramp['twaPrice'].max()),
        'total_count': len(extended_df),
        'price_gap_filled': True,
        'extension_range': (min_synthetic_price, historical_df['twaPrice'].min())
    })
    
    print(f"\nDataset Extension Summary:")
    print(f"  Historical data: {metadata['historical_count']} seasons")
    print(f"  Synthetic data: {metadata['synthetic_count']} price points") 
    print(f"  Total data: {metadata['total_count']} rows")
    print(f"  Extended price range: {min_synthetic_price:.3f} to {historical_df['twaPrice'].max():.3f}")
    
    return extended_df, metadata

def analyze_price_coverage(extended_df: pd.DataFrame, metadata: dict) -> None:
    """Analyze and report on price coverage in the extended dataset."""
    
    print(f"\n=== Price Coverage Analysis ===")
    
    historical_data = extended_df[extended_df['data_source'] == 'historical']
    synthetic_data = extended_df[extended_df['data_source'] == 'synthetic']
    
    print(f"\nHistorical Data:")
    if len(historical_data) > 0:
        print(f"  Count: {len(historical_data)} seasons")
        print(f"  Price range: {historical_data['twaPrice'].min():.3f} to {historical_data['twaPrice'].max():.3f}")
        print(f"  Price mean: {historical_data['twaPrice'].mean():.3f}")
        print(f"  Price median: {historical_data['twaPrice'].median():.3f}")
    
    print(f"\nSynthetic Data:")
    if len(synthetic_data) > 0:
        print(f"  Count: {len(synthetic_data)} price points")
        print(f"  Price range: {synthetic_data['twaPrice'].min():.3f} to {synthetic_data['twaPrice'].max():.3f}")
        print(f"  Price step: {np.diff(sorted(synthetic_data['twaPrice'].unique())).mean():.3f}")
    
    print(f"\nCombined Coverage:")
    print(f"  Total range: {extended_df['twaPrice'].min():.3f} to {extended_df['twaPrice'].max():.3f}")
    print(f"  Gap filled: {metadata.get('extension_range', 'None')}")

def main():
    """Example usage of synthetic price extension."""
    
    # Load historical data
    input_file = "../../data/pinto_season_data_with_ramp_analysis.csv"
    
    if not pd.io.common.file_exists(input_file):
        print(f"Error: {input_file} not found.")
        print("Please run ramp_rate_analysis.py first to generate the base data.")
        return
    
    print("Loading historical ramp rate data...")
    historical_df = pd.read_csv(input_file)
    print(f"Loaded {len(historical_df)} seasons of historical data")
    
    # Create extended dataset
    print(f"\nCreating extended dataset with synthetic price data...")
    extended_df, metadata = create_extended_dataset(
        historical_df,
        include_synthetic=True,
        min_synthetic_price=0.25,
        price_step=0.01
    )
    
    # Analyze coverage
    analyze_price_coverage(extended_df, metadata)
    
    # Save extended dataset
    output_file = "../../data/pinto_season_data_with_extended_ramp_analysis.csv"
    extended_df.to_csv(output_file, index=False)
    print(f"\nExtended dataset saved to: {output_file}")
    
    print(f"\nSynthetic price extension completed!")

if __name__ == "__main__":
    main()