#!/usr/bin/env python3
"""
Comprehensive capacity analysis visualization script.
Creates multiple types of plots to analyze capacity at different S values.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.colors import LinearSegmentedColormap

def load_data(csv_file: str) -> pd.DataFrame:
    """Load the capacity analysis data."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run add_capacity_analysis.py first.")
        return None
    
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} seasons of data")
    return df

def plot_multiline_timeseries(df: pd.DataFrame, save_path: str = "../../visualizations/capacity_visualizations/capacity_timeseries.png"):
    """Create multi-line time series plot for all S values."""
    plt.figure(figsize=(16, 10))
    
    # Define colors for different S values
    colors = plt.cm.viridis(np.linspace(0, 1, 10))
    
    # Plot each S value
    for i, s_value in enumerate(range(100, 1100, 100)):
        column_name = f'Capacity_at_Smin_{s_value}'
        plt.plot(df['Season'], df[column_name], 
                color=colors[i], linewidth=2, alpha=0.8, 
                label=f'S={s_value}')
    
    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Capacity', fontsize=12)
    plt.title('Capacity Evolution Across All S Values', fontsize=16, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Multi-line time series saved as: {save_path}")

def plot_capacity_heatmap(df: pd.DataFrame, save_path: str = "../../visualizations/capacity_visualizations/capacity_heatmap.png"):
    """Create heatmap of Season vs S-value with capacity as color."""
    # Create capacity matrix for heatmap
    s_values = list(range(100, 1100, 100))
    capacity_columns = [f'Capacity_at_Smin_{s}' for s in s_values]
    
    # Sample data to make heatmap manageable (every 50th season)
    sampled_df = df.iloc[::50].copy()
    
    # Prepare data for heatmap
    heatmap_data = sampled_df[capacity_columns].T
    heatmap_data.index = s_values
    heatmap_data.columns = sampled_df['Season'].values
    
    plt.figure(figsize=(20, 8))
    
    # Create custom colormap
    colors = ['#000080', '#0000FF', '#00FFFF', '#FFFF00', '#FF8000', '#FF0000']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('capacity', colors, N=n_bins)
    
    sns.heatmap(heatmap_data, cmap=cmap, cbar_kws={'label': 'Capacity'})
    
    plt.xlabel('Season (sampled every 50)', fontsize=12)
    plt.ylabel('S Value', fontsize=12)
    plt.title('Capacity Heatmap: S Values vs Seasons', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Heatmap saved as: {save_path}")

def plot_capacity_boxplots(df: pd.DataFrame, save_path: str = "../../visualizations/capacity_visualizations/capacity_boxplots.png"):
    """Create box plots showing capacity distributions for each S value."""
    s_values = list(range(100, 1100, 100))
    capacity_data = []
    s_labels = []
    
    for s_value in s_values:
        column_name = f'Capacity_at_Smin_{s_value}'
        capacity_data.extend(df[column_name].values)
        s_labels.extend([f'S={s_value}'] * len(df))
    
    # Create DataFrame for seaborn
    plot_df = pd.DataFrame({
        'S_Value': s_labels,
        'Capacity': capacity_data
    })
    
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=plot_df, x='S_Value', y='Capacity')
    plt.xticks(rotation=45)
    plt.xlabel('S Value', fontsize=12)
    plt.ylabel('Capacity', fontsize=12)
    plt.title('Capacity Distribution by S Value', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Box plots saved as: {save_path}")

def plot_key_moments_analysis(df: pd.DataFrame, save_path: str = "../../visualizations/capacity_visualizations/key_moments_analysis.png"):
    """Focus on seasons where maxNegativeTwaDeltaB changed (isNewMaxTwaDeltaB = True)."""
    key_moments = df[df['isNewMaxTwaDeltaB'] == True].copy()
    
    if key_moments.empty:
        print("No key moments found in the data")
        return
    
    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Top plot: Capacity evolution at key moments
    s_values = list(range(100, 1100, 100))
    colors = plt.cm.tab10(np.linspace(0, 1, len(key_moments)))
    
    for i, (_, row) in enumerate(key_moments.iterrows()):
        capacities = [row[f'Capacity_at_Smin_{s}'] for s in s_values]
        ax1.plot(s_values, capacities, 'o-', color=colors[i], 
                linewidth=2, markersize=6, label=f"Season {int(row['Season'])}")
    
    ax1.set_xlabel('S Value', fontsize=12)
    ax1.set_ylabel('Capacity', fontsize=12)
    ax1.set_title('Capacity Profiles at Key Moments (New Max Negative TwaDeltaB)', fontsize=14, fontweight='bold')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Bottom plot: Timeline of key moments
    ax2.plot(df['Season'], df['maxNegativeTwaDeltaB'], color='gray', alpha=0.5, linewidth=1)
    ax2.scatter(key_moments['Season'], key_moments['maxNegativeTwaDeltaB'], 
               color='red', s=100, zorder=5)
    
    # Annotate key moments
    for _, row in key_moments.iterrows():
        ax2.annotate(f"S{int(row['Season'])}", 
                    xy=(row['Season'], row['maxNegativeTwaDeltaB']),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    ax2.set_xlabel('Season', fontsize=12)
    ax2.set_ylabel('Max Negative TwaDeltaB', fontsize=12)
    ax2.set_title('Timeline of Key Moments', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Key moments analysis saved as: {save_path}")
    print(f"Found {len(key_moments)} key moments")

def main():
    """Main function to create all capacity visualizations."""
    csv_file = "../../data/pinto_season_data_with_capacity_analysis.csv"
    
    print("Loading capacity analysis data...")
    df = load_data(csv_file)
    
    if df is None:
        return
    
    print("\n1. Creating multi-line time series plot...")
    plot_multiline_timeseries(df)
    
    print("\n2. Creating capacity heatmap...")
    plot_capacity_heatmap(df)
    
    print("\n3. Creating capacity box plots...")
    plot_capacity_boxplots(df)
    
    print("\n4. Creating key moments analysis...")
    plot_key_moments_analysis(df)
    
    print("\nAll visualizations completed!")

if __name__ == "__main__":
    main()