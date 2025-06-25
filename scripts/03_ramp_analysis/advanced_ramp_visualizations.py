#!/usr/bin/env python3
"""
Advanced ramp rate visualizations including 3D surfaces, contour plots, and price regime analysis.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
from plotly.subplots import make_subplots
import os

def load_ramp_data(csv_file: str) -> pd.DataFrame:
    """Load the ramp rate analysis data."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run ramp_rate_analysis.py first.")
        return None
    
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} seasons of ramp rate data")
    return df

def create_3d_surface_plots(df: pd.DataFrame):
    """Create 3D surface plots showing Price × Δd × Seasons-to-Max relationship."""
    
    # Define delta_d values and price range (0.1% to 3.0%)
    key_deltas = [i/10 for i in range(5, 31, 3)]  # 0.5, 0.8, 1.1, 1.4, 1.7, 2.0, 2.3, 2.6, 2.9
    price_range = np.linspace(df['twaPrice'].quantile(0.05), df['twaPrice'].quantile(0.95), 20)
    
    # Create meshgrid
    delta_mesh, price_mesh = np.meshgrid(key_deltas, price_range)
    seasons_mesh = np.zeros_like(delta_mesh)
    
    # Calculate seasons-to-max for each combination
    for i, price in enumerate(price_range):
        for j, delta_d in enumerate(key_deltas):
            # Formula: seasons = 0.99 / (delta_d/100 * price)
            seasons = 0.99 / (delta_d/100 * price)
            seasons_mesh[i, j] = min(seasons, 1000)  # Cap at 1000 for visualization
    
    # Create 3D surface plot with matplotlib
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(price_mesh, delta_mesh, seasons_mesh, 
                          cmap='RdYlBu_r', alpha=0.8, edgecolor='none')
    
    # Add contour lines on bottom
    ax.contour(price_mesh, delta_mesh, seasons_mesh, levels=10, 
               zdir='z', offset=0, colors='gray', alpha=0.5)
    
    ax.set_xlabel('TwaPrice', fontsize=12)
    ax.set_ylabel('Δd (%)', fontsize=12)
    ax.set_zlabel('Seasons to Max Capacity', fontsize=12)
    ax.set_title('3D Surface: Price × Δd × Ramp Time Relationship', fontsize=14, fontweight='bold')
    
    # Add colorbar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=20, label='Seasons to Max')
    
    # Set viewing angle
    ax.view_init(elev=30, azim=45)
    
    save_path = "../../visualizations/ramp_rate_visualizations/3d_surface_plot.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"3D surface plot saved as: {save_path}")

def create_interactive_3d_surface(df: pd.DataFrame):
    """Create interactive 3D surface plot with Plotly."""
    
    # Define ranges (0.1% to 3.0% in 0.1% steps for smoother surface)
    key_deltas = np.arange(0.1, 3.1, 0.1)
    price_range = np.linspace(df['twaPrice'].quantile(0.05), df['twaPrice'].quantile(0.95), 30)
    
    # Create meshgrid
    delta_mesh, price_mesh = np.meshgrid(key_deltas, price_range)
    seasons_mesh = np.zeros_like(delta_mesh)
    
    # Calculate seasons-to-max for each combination
    for i, price in enumerate(price_range):
        for j, delta_d in enumerate(key_deltas):
            seasons = 0.99 / (delta_d/100 * price)
            seasons_mesh[i, j] = min(seasons, 800)  # Cap for better visualization
    
    # Create 3D surface
    fig = go.Figure(data=[go.Surface(
        x=price_mesh,
        y=delta_mesh,
        z=seasons_mesh,
        colorscale='RdYlBu_r',
        hovertemplate='Price: %{x:.3f}<br>Δd: %{y:.2f}%<br>Seasons to Max: %{z:.1f}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Interactive 3D Surface: Price × Δd × Ramp Time',
        scene=dict(
            xaxis_title='TwaPrice',
            yaxis_title='Δd (%)',
            zaxis_title='Seasons to Max Capacity',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        height=700
    )
    
    save_path = "../../visualizations/ramp_rate_visualizations/interactive_3d_surface.html"
    pyo.plot(fig, filename=save_path, auto_open=False)
    print(f"Interactive 3D surface saved as: {save_path}")

def create_contour_plots(df: pd.DataFrame):
    """Create contour plots showing ramp time levels."""
    
    # Define ranges (0.1% to 3.0% in 0.1% steps)
    key_deltas = np.arange(0.1, 3.1, 0.1)
    price_range = np.linspace(df['twaPrice'].quantile(0.05), df['twaPrice'].quantile(0.95), 50)
    
    # Create meshgrid
    delta_mesh, price_mesh = np.meshgrid(key_deltas, price_range)
    seasons_mesh = np.zeros_like(delta_mesh)
    
    # Calculate seasons-to-max
    for i, price in enumerate(price_range):
        for j, delta_d in enumerate(key_deltas):
            seasons = 0.99 / (delta_d/100 * price)
            seasons_mesh[i, j] = min(seasons, 1000)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Contour plot 1: Filled contours
    contour_levels = [25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
    cs1 = ax1.contourf(price_mesh, delta_mesh, seasons_mesh, levels=contour_levels, 
                      cmap='RdYlBu_r', alpha=0.8)
    
    # Add contour lines with labels
    cs1_lines = ax1.contour(price_mesh, delta_mesh, seasons_mesh, levels=contour_levels, 
                           colors='black', linewidths=1, alpha=0.6)
    ax1.clabel(cs1_lines, inline=True, fontsize=8, fmt='%d')
    
    ax1.set_xlabel('TwaPrice', fontsize=12)
    ax1.set_ylabel('Δd (%)', fontsize=12)
    ax1.set_title('Contour Plot: Seasons to Max Capacity', fontsize=14, fontweight='bold')
    
    # Add colorbar
    cbar1 = plt.colorbar(cs1, ax=ax1)
    cbar1.set_label('Seasons to Max Capacity', fontsize=12)
    
    # Contour plot 2: Target zones
    # Define target zones
    target_zones = [
        (0, 50, 'Very Fast', 'red'),
        (50, 100, 'Fast', 'orange'), 
        (100, 200, 'Moderate', 'yellow'),
        (200, 500, 'Slow', 'lightblue'),
        (500, 1000, 'Very Slow', 'blue')
    ]
    
    # Create legend patches manually
    legend_patches = []
    
    for min_val, max_val, label, color in target_zones:
        mask = (seasons_mesh >= min_val) & (seasons_mesh < max_val)
        ax2.contourf(price_mesh, delta_mesh, mask, levels=[0.5, 1.5], 
                    colors=[color], alpha=0.6)
        # Create legend patch
        from matplotlib.patches import Patch
        legend_patches.append(Patch(color=color, alpha=0.6, label=label))
    
    # Add contour lines for key levels
    key_levels = [50, 100, 200, 500]
    cs2 = ax2.contour(price_mesh, delta_mesh, seasons_mesh, levels=key_levels, 
                     colors='black', linewidths=2)
    ax2.clabel(cs2, inline=True, fontsize=10, fmt='%d seasons')
    
    ax2.set_xlabel('TwaPrice', fontsize=12)
    ax2.set_ylabel('Δd (%)', fontsize=12)
    ax2.set_title('Ramp Speed Zones', fontsize=14, fontweight='bold')
    ax2.legend(handles=legend_patches, loc='upper right')
    
    plt.tight_layout()
    save_path = "../../visualizations/ramp_rate_visualizations/contour_plots.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Contour plots saved as: {save_path}")

def create_price_regime_analysis(df: pd.DataFrame):
    """Create comprehensive price regime comparison analysis."""
    
    # Define price regimes based on quantiles
    price_quantiles = [0, 0.25, 0.5, 0.75, 1.0]
    regime_names = ['Low Price\n(0-25th %ile)', 'Medium-Low\n(25-50th %ile)', 
                   'Medium-High\n(50-75th %ile)', 'High Price\n(75-100th %ile)']
    
    # Calculate price regime boundaries
    regime_boundaries = [df['twaPrice'].quantile(q) for q in price_quantiles]
    
    # Assign regime to each season
    df_analysis = df.copy()
    df_analysis['price_regime'] = pd.cut(df_analysis['twaPrice'], 
                                       bins=regime_boundaries, 
                                       labels=regime_names, 
                                       include_lowest=True)
    
    # Create comprehensive analysis
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # 1. Box plots of ramp times by regime (Top Left)
    key_deltas = [0.5, 1.0, 2.0, 3.0]
    regime_colors = ['lightcoral', 'lightsalmon', 'lightblue', 'lightgreen']
    
    box_data = []
    box_labels = []
    box_colors = []
    
    for delta_d in key_deltas:
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        for i, regime in enumerate(regime_names):
            regime_data = df_analysis[df_analysis['price_regime'] == regime]
            if len(regime_data) > 0:
                ramp_times = np.minimum(regime_data[max_col], 1000)
                box_data.extend(ramp_times)
                box_labels.extend([f'Δd={delta_d}%\n{regime}'] * len(ramp_times))
                box_colors.extend([regime_colors[i]] * len(ramp_times))
    
    # Create box plot data
    box_df = pd.DataFrame({'Ramp_Time': box_data, 'Label': box_labels, 'Color': box_colors})
    
    sns.boxplot(data=box_df, x='Label', y='Ramp_Time', ax=axes[0,0])
    axes[0,0].set_xticklabels(axes[0,0].get_xticklabels(), rotation=45, ha='right')
    axes[0,0].set_ylabel('Seasons to Max Capacity', fontsize=12)
    axes[0,0].set_title('Ramp Time Distribution by Price Regime', fontsize=14, fontweight='bold')
    axes[0,0].set_yscale('log')
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. Median ramp times by regime (Top Right)
    regime_medians = {}
    for delta_d in key_deltas:
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        regime_medians[f'Δd={delta_d}%'] = []
        for regime in regime_names:
            regime_data = df_analysis[df_analysis['price_regime'] == regime]
            if len(regime_data) > 0:
                median_ramp = regime_data[max_col].median()
                regime_medians[f'Δd={delta_d}%'].append(min(median_ramp, 1000))
            else:
                regime_medians[f'Δd={delta_d}%'].append(np.nan)
    
    x_pos = np.arange(len(regime_names))
    width = 0.2
    
    for i, (delta_label, medians) in enumerate(regime_medians.items()):
        axes[0,1].bar(x_pos + i*width, medians, width, label=delta_label, alpha=0.8)
    
    axes[0,1].set_xlabel('Price Regime', fontsize=12)
    axes[0,1].set_ylabel('Median Seasons to Max', fontsize=12)
    axes[0,1].set_title('Median Ramp Times by Price Regime', fontsize=14, fontweight='bold')
    axes[0,1].set_xticks(x_pos + width*1.5)
    axes[0,1].set_xticklabels(regime_names, rotation=45, ha='right')
    axes[0,1].legend()
    axes[0,1].set_yscale('log')
    axes[0,1].grid(True, alpha=0.3)
    
    # 3. Price distribution over time (Bottom Left)
    # Sample data for performance
    sample_df = df_analysis.iloc[::25]
    
    for i, regime in enumerate(regime_names):
        regime_data = sample_df[sample_df['price_regime'] == regime]
        if len(regime_data) > 0:
            axes[1,0].scatter(regime_data['Season'], regime_data['twaPrice'], 
                            c=regime_colors[i], alpha=0.6, s=10, label=regime)
    
    axes[1,0].set_xlabel('Season', fontsize=12)
    axes[1,0].set_ylabel('TwaPrice', fontsize=12)
    axes[1,0].set_title('Price Regime Distribution Over Time', fontsize=14, fontweight='bold')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # 4. Optimal Δd by regime (Bottom Right)
    target_seasons = [50, 100, 200]
    target_colors = ['red', 'orange', 'blue']
    
    for j, target in enumerate(target_seasons):
        optimal_deltas = []
        for regime in regime_names:
            regime_data = df_analysis[df_analysis['price_regime'] == regime]
            if len(regime_data) > 0:
                median_price = regime_data['twaPrice'].median()
                optimal_delta = (0.99 / (target * median_price)) * 100
                optimal_deltas.append(optimal_delta)
            else:
                optimal_deltas.append(np.nan)
        
        x_pos_targets = np.arange(len(regime_names))
        axes[1,1].bar(x_pos_targets + j*0.25, optimal_deltas, 0.25, 
                     label=f'{target} seasons', color=target_colors[j], alpha=0.8)
    
    axes[1,1].set_xlabel('Price Regime', fontsize=12)
    axes[1,1].set_ylabel('Optimal Δd (%)', fontsize=12)
    axes[1,1].set_title('Optimal Δd by Price Regime and Target', fontsize=14, fontweight='bold')
    axes[1,1].set_xticks(x_pos_targets + 0.25)
    axes[1,1].set_xticklabels(regime_names, rotation=45, ha='right')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_path = "../../visualizations/ramp_rate_visualizations/price_regime_analysis.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close figure to free memory
    
    print(f"Price regime analysis saved as: {save_path}")
    
    # Print summary statistics
    print(f"\n=== Price Regime Summary ===")
    for i, regime in enumerate(regime_names):
        regime_data = df_analysis[df_analysis['price_regime'] == regime]
        if len(regime_data) > 0:
            print(f"{regime}:")
            print(f"  Price range: {regime_data['twaPrice'].min():.3f} - {regime_data['twaPrice'].max():.3f}")
            print(f"  Median price: {regime_data['twaPrice'].median():.3f}")
            print(f"  Seasons: {len(regime_data)}")
            
            # Show optimal Δd for 100-season target
            median_price = regime_data['twaPrice'].median()
            optimal_delta = (0.99 / (100 * median_price)) * 100
            print(f"  Optimal Δd for 100-season ramp: {optimal_delta:.2f}%")
            print()

def main():
    """Main function to create advanced ramp rate visualizations."""
    csv_file = "../../data/pinto_season_data_with_ramp_analysis.csv"
    
    print("Loading ramp rate analysis data...")
    df = load_ramp_data(csv_file)
    
    if df is None:
        return
    
    # Ensure output directory exists
    os.makedirs("ramp_rate_visualizations", exist_ok=True)
    
    print("\n1. Creating 3D surface plots...")
    create_3d_surface_plots(df)
    
    print("\n2. Creating interactive 3D surface...")
    create_interactive_3d_surface(df)
    
    print("\n3. Creating contour plots...")
    create_contour_plots(df)
    
    print("\n4. Creating price regime analysis...")
    create_price_regime_analysis(df)
    
    print("\nAdvanced ramp rate visualizations completed!")

if __name__ == "__main__":
    main()