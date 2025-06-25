#!/usr/bin/env python3
"""
Comprehensive ramp rate visualization suite.
Creates multiple types of plots to analyze capacity ramping at different Δd values.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import os

def load_ramp_data(csv_file: str) -> pd.DataFrame:
    """Load the ramp rate analysis data."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run ramp_rate_analysis.py first.")
        return None
    
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} seasons of ramp rate data")
    return df

def create_price_delta_heatmaps(df: pd.DataFrame):
    """Create Price-Δd heatmaps showing seasons-to-max and seasons-to-min."""
    
    # Define Δd values and their corresponding column patterns
    delta_d_values = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0]
    
    # Create price bins for better visualization
    price_bins = np.linspace(df['twaPrice'].min(), df['twaPrice'].quantile(0.95), 20)  # Exclude extreme outliers
    price_centers = (price_bins[:-1] + price_bins[1:]) / 2
    
    # Initialize matrices for heatmap data
    seasons_to_max_matrix = np.zeros((len(delta_d_values), len(price_centers)))
    seasons_to_min_matrix = np.zeros((len(delta_d_values), len(price_centers)))
    
    # Fill matrices with averaged data for each price-delta_d combination
    for i, delta_d in enumerate(delta_d_values):
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        min_col = f"seasons_to_min_capacity_dd_{delta_d_pct}pct"
        
        for j, price_center in enumerate(price_centers):
            # Find data points in this price bin
            price_mask = (df['twaPrice'] >= price_bins[j]) & (df['twaPrice'] < price_bins[j+1])
            if price_mask.sum() > 0:
                seasons_to_max_matrix[i, j] = df[price_mask][max_col].median()
                seasons_to_min_matrix[i, j] = df[price_mask][min_col].median()
    
    # Create the heatmap plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Seasons to Max heatmap
    im1 = ax1.imshow(seasons_to_max_matrix, cmap='RdYlBu_r', aspect='auto', 
                     norm=plt.Normalize(vmin=0, vmax=500))  # Cap at 500 seasons for better color scale
    ax1.set_title('Seasons to Maximum Capacity', fontsize=16, fontweight='bold')
    ax1.set_xlabel('TwaPrice', fontsize=12)
    ax1.set_ylabel('Δd (%)', fontsize=12)
    
    # Set custom ticks
    ax1.set_xticks(range(0, len(price_centers), 3))
    ax1.set_xticklabels([f'{p:.2f}' for p in price_centers[::3]], rotation=45)
    ax1.set_yticks(range(len(delta_d_values)))
    ax1.set_yticklabels([f'{d:.2f}%' for d in delta_d_values])
    
    # Add colorbar
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('Seasons to Max Capacity', fontsize=12)
    
    # Seasons to Min heatmap
    im2 = ax2.imshow(seasons_to_min_matrix, cmap='RdYlGn_r', aspect='auto',
                     norm=plt.Normalize(vmin=0, vmax=10))  # Cap at 10 seasons for better color scale
    ax2.set_title('Seasons to Minimum Capacity', fontsize=16, fontweight='bold')
    ax2.set_xlabel('TwaPrice', fontsize=12)
    ax2.set_ylabel('Δd (%)', fontsize=12)
    
    # Set custom ticks
    ax2.set_xticks(range(0, len(price_centers), 3))
    ax2.set_xticklabels([f'{p:.2f}' for p in price_centers[::3]], rotation=45)
    ax2.set_yticks(range(len(delta_d_values)))
    ax2.set_yticklabels([f'{d:.2f}%' for d in delta_d_values])
    
    # Add colorbar
    cbar2 = plt.colorbar(im2, ax=ax2)
    cbar2.set_label('Seasons to Min Capacity', fontsize=12)
    
    plt.tight_layout()
    save_path = "../../visualizations/ramp_rate_visualizations/price_delta_heatmaps.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Price-Δd heatmaps saved as: {save_path}")

def create_ramp_tradeoff_analysis(df: pd.DataFrame):
    """Create scatter plot showing ramp-up vs ramp-down trade-offs."""
    
    # Select key delta_d values for analysis
    key_deltas = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Plot 1: Ramp rates at median price
    median_price = df['twaPrice'].median()
    median_data = df[abs(df['twaPrice'] - median_price) < 0.1].iloc[0]  # Get data close to median price
    
    increase_rates = []
    decrease_rates = []
    delta_labels = []
    
    for delta_d in key_deltas:
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        inc_col = f"effective_increase_rate_dd_{delta_d_pct}pct"
        dec_col = f"effective_decrease_rate_dd_{delta_d_pct}pct"
        
        increase_rates.append(median_data[inc_col] * 100)  # Convert to percentage
        decrease_rates.append(median_data[dec_col] * 100)  # Convert to percentage
        delta_labels.append(f'{delta_d}%')
    
    scatter1 = ax1.scatter(increase_rates, decrease_rates, c=key_deltas, cmap='viridis', 
                          s=150, alpha=0.8, edgecolors='black')
    
    # Add labels for each point
    for i, label in enumerate(delta_labels):
        ax1.annotate(label, (increase_rates[i], decrease_rates[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
    
    ax1.set_xlabel('Increase Rate (%/season)', fontsize=12)
    ax1.set_ylabel('Decrease Rate (%/season)', fontsize=12)
    ax1.set_title(f'Ramp Rate Trade-offs at Median Price ({median_price:.3f})', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')  # Log scale for better visualization
    
    # Add colorbar
    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label('Δd (%)', fontsize=12)
    
    # Plot 2: Seasons to max/min at median price
    seasons_to_max = []
    seasons_to_min = []
    
    for delta_d in key_deltas:
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        min_col = f"seasons_to_min_capacity_dd_{delta_d_pct}pct"
        
        seasons_to_max.append(median_data[max_col])
        seasons_to_min.append(median_data[min_col])
    
    scatter2 = ax2.scatter(seasons_to_max, seasons_to_min, c=key_deltas, cmap='viridis', 
                          s=150, alpha=0.8, edgecolors='black')
    
    # Add labels for each point
    for i, label in enumerate(delta_labels):
        ax2.annotate(label, (seasons_to_max[i], seasons_to_min[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
    
    ax2.set_xlabel('Seasons to Max Capacity', fontsize=12)
    ax2.set_ylabel('Seasons to Min Capacity', fontsize=12)
    ax2.set_title(f'Ramp Time Trade-offs at Median Price ({median_price:.3f})', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    
    # Add colorbar
    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label('Δd (%)', fontsize=12)
    
    plt.tight_layout()
    save_path = "../../visualizations/ramp_rate_visualizations/ramp_tradeoff_analysis.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Ramp trade-off analysis saved as: {save_path}")

def create_timeseries_analysis(df: pd.DataFrame):
    """Create time series analysis for key Δd values."""
    
    # Select key delta_d values for visualization
    key_deltas = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
    colors = plt.cm.Set2(np.linspace(0, 1, len(key_deltas)))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Plot 1: Seasons to max capacity over time
    for i, delta_d in enumerate(key_deltas):
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        # Apply reasonable cap for visualization
        capped_data = np.minimum(df[max_col], 1000)
        
        ax1.plot(df['Season'], capped_data, color=colors[i], linewidth=2, 
                alpha=0.8, label=f'Δd={delta_d}%')
    
    ax1.set_xlabel('Season', fontsize=12)
    ax1.set_ylabel('Seasons to Max Capacity (capped at 1000)', fontsize=12)
    ax1.set_title('Ramp-Up Time Evolution Across Seasons', fontsize=14, fontweight='bold')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Plot 2: TwaPrice overlay for context
    ax2_twin = ax2.twinx()
    
    # Plot a subset of delta_d values to avoid clutter
    subset_deltas = [1.0, 2.0, 5.0]
    subset_colors = [colors[key_deltas.index(d)] for d in subset_deltas]
    
    for i, delta_d in enumerate(subset_deltas):
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        capped_data = np.minimum(df[max_col], 500)  # Lower cap for better visibility
        ax2.plot(df['Season'], capped_data, color=subset_colors[i], linewidth=2, 
                alpha=0.8, label=f'Δd={delta_d}%')
    
    # Plot twaPrice on secondary axis
    ax2_twin.plot(df['Season'], df['twaPrice'], color='gray', alpha=0.6, linewidth=1, 
                 label='TwaPrice')
    
    ax2.set_xlabel('Season', fontsize=12)
    ax2.set_ylabel('Seasons to Max Capacity (capped at 500)', fontsize=12)
    ax2_twin.set_ylabel('TwaPrice', fontsize=12)
    ax2.set_title('Ramp-Up Time vs Price Context', fontsize=14, fontweight='bold')
    
    # Combine legends
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    plt.tight_layout()
    save_path = "../../visualizations/ramp_rate_visualizations/ramp_timeseries_analysis.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Time series analysis saved as: {save_path}")

def create_small_multiples_grid(df: pd.DataFrame):
    """Create small multiples grid comparing different Δd behaviors."""
    
    # Select 6 key delta_d values for the grid
    key_deltas = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, delta_d in enumerate(key_deltas):
        ax = axes[i]
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        # Cap data for better visualization
        capped_data = np.minimum(df[max_col], 1000)
        
        # Plot seasons to max
        line1 = ax.plot(df['Season'], capped_data, color='blue', linewidth=1.5, 
                       alpha=0.7, label='Seasons to Max')
        
        # Add twaPrice on secondary axis
        ax2 = ax.twinx()
        line2 = ax2.plot(df['Season'], df['twaPrice'], color='orange', alpha=0.5, 
                        linewidth=1, label='TwaPrice')
        
        # Formatting
        ax.set_title(f'Δd = {delta_d}%', fontsize=12, fontweight='bold')
        ax.set_ylabel('Seasons to Max', fontsize=10)
        ax2.set_ylabel('TwaPrice', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        # Only add x-label to bottom row
        if i >= 3:
            ax.set_xlabel('Season', fontsize=10)
        
        # Add legend only to first subplot
        if i == 0:
            lines = line1 + line2
            labels = ['Seasons to Max', 'TwaPrice']
            ax.legend(lines, labels, loc='upper right', fontsize=8)
    
    plt.suptitle('Ramp Behavior Comparison Across Different Δd Values', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    save_path = "../../visualizations/ramp_rate_visualizations/ramp_small_multiples.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Small multiples grid saved as: {save_path}")

def main():
    """Main function to create all ramp rate visualizations."""
    csv_file = "../../data/pinto_season_data_with_ramp_analysis.csv"
    
    print("Loading ramp rate analysis data...")
    df = load_ramp_data(csv_file)
    
    if df is None:
        return
    
    # Ensure output directory exists
    os.makedirs("../../visualizations/ramp_rate_visualizations", exist_ok=True)
    
    print("\n1. Creating Price-Δd heatmaps...")
    create_price_delta_heatmaps(df)
    
    print("\n2. Creating ramp trade-off analysis...")
    create_ramp_tradeoff_analysis(df)
    
    print("\n3. Creating time series analysis...")
    create_timeseries_analysis(df)
    
    print("\n4. Creating small multiples grid...")
    create_small_multiples_grid(df)
    
    print("\nCore ramp rate visualizations completed!")

if __name__ == "__main__":
    main()