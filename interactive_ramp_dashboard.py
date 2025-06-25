#!/usr/bin/env python3
"""
Interactive dashboard for ramp rate analysis with sliders and selectors.
Creates comprehensive Plotly dashboard for exploring ramp rate scenarios.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import os

def load_ramp_data(csv_file: str) -> pd.DataFrame:
    """Load the ramp rate analysis data."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run ramp_rate_analysis.py first.")
        return None
    
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} seasons of ramp rate data")
    return df

def create_interactive_ramp_dashboard(df: pd.DataFrame, output_file: str = "ramp_rate_visualizations/ramp_interactive_dashboard.html"):
    """Create comprehensive interactive dashboard for ramp rate analysis."""
    
    # Create subplot structure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Price-Δd Heatmap (Seasons to Max)', 'Ramp Trade-offs', 
                       'Time Series Analysis', 'Target-Based Analysis'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": True}, {"secondary_y": False}]]
    )
    
    # Define key delta_d values for analysis
    key_deltas = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    colors = px.colors.qualitative.Set3
    
    # 1. Price-Δd Heatmap (Top Left)
    # Create aggregated data for heatmap
    price_bins = np.linspace(df['twaPrice'].quantile(0.05), df['twaPrice'].quantile(0.95), 15)
    price_centers = (price_bins[:-1] + price_bins[1:]) / 2
    
    # Initialize heatmap matrix
    heatmap_matrix = np.zeros((len(key_deltas), len(price_centers)))
    
    for i, delta_d in enumerate(key_deltas):
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        for j, price_center in enumerate(price_centers):
            price_mask = (df['twaPrice'] >= price_bins[j]) & (df['twaPrice'] < price_bins[j+1])
            if price_mask.sum() > 0:
                heatmap_matrix[i, j] = df[price_mask][max_col].median()
    
    # Cap values for better visualization
    heatmap_matrix = np.minimum(heatmap_matrix, 500)
    
    fig.add_trace(
        go.Heatmap(
            z=heatmap_matrix,
            x=[f'{p:.2f}' for p in price_centers],
            y=[f'{d}%' for d in key_deltas],
            colorscale='RdYlBu_r',
            name='Seasons to Max',
            hovertemplate='Price: %{x}<br>Δd: %{y}<br>Seasons to Max: %{z:.1f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Ramp Trade-offs (Top Right)
    median_price = df['twaPrice'].median()
    median_data = df[abs(df['twaPrice'] - median_price) < 0.1].iloc[0]
    
    increase_rates = []
    decrease_rates = []
    
    for delta_d in key_deltas:
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        inc_col = f"effective_increase_rate_dd_{delta_d_pct}pct"
        dec_col = f"effective_decrease_rate_dd_{delta_d_pct}pct"
        
        increase_rates.append(median_data[inc_col] * 100)
        decrease_rates.append(median_data[dec_col] * 100)
    
    fig.add_trace(
        go.Scatter(
            x=increase_rates,
            y=decrease_rates,
            mode='markers+text',
            text=[f'{d}%' for d in key_deltas],
            textposition='top center',
            marker=dict(size=12, color=key_deltas, colorscale='Viridis', showscale=False),
            name='Trade-offs',
            hovertemplate='Δd: %{text}<br>Increase Rate: %{x:.3f}%/season<br>Decrease Rate: %{y:.3f}%/season<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Time Series Analysis (Bottom Left)
    # Plot a few key delta_d values
    subset_deltas = [1.0, 2.0, 4.0]
    
    for i, delta_d in enumerate(subset_deltas):
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        # Sample data for performance (every 10th point)
        sampled_df = df.iloc[::10]
        capped_data = np.minimum(sampled_df[max_col], 1000)
        
        fig.add_trace(
            go.Scatter(
                x=sampled_df['Season'],
                y=capped_data,
                mode='lines',
                name=f'Δd={delta_d}%',
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate=f'Δd={delta_d}%<br>Season: %{{x}}<br>Seasons to Max: %{{y:.1f}}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Add twaPrice on secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=sampled_df['Season'],
            y=sampled_df['twaPrice'],
            mode='lines',
            name='TwaPrice',
            line=dict(color='gray', width=1, dash='dash'),
            opacity=0.6,
            yaxis='y4',
            hovertemplate='Season: %{x}<br>TwaPrice: %{y:.3f}<extra></extra>'
        ),
        row=2, col=1, secondary_y=True
    )
    
    # 4. Target-Based Analysis (Bottom Right)
    # Show required Δd for different target ramp times
    target_seasons = [50, 100, 150, 200, 300, 500]
    median_price = df['twaPrice'].median()
    
    required_deltas = []
    for target in target_seasons:
        # Required Δd = 0.99 / (target × median_price)
        required_delta = (0.99 / (target * median_price)) * 100  # Convert to percentage
        required_deltas.append(required_delta)
    
    fig.add_trace(
        go.Bar(
            x=[f'{t} seasons' for t in target_seasons],
            y=required_deltas,
            name='Required Δd',
            marker_color='lightblue',
            hovertemplate='Target: %{x}<br>Required Δd: %{y:.2f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Interactive Ramp Rate Analysis Dashboard",
            x=0.5,
            font=dict(size=20)
        ),
        height=800,
        showlegend=True,
        hovermode='closest'
    )
    
    # Update subplot titles and axes
    fig.update_xaxes(title_text="TwaPrice", row=1, col=1)
    fig.update_yaxes(title_text="Δd (%)", row=1, col=1)
    
    fig.update_xaxes(title_text="Increase Rate (%/season)", row=1, col=2)
    fig.update_yaxes(title_text="Decrease Rate (%/season)", type="log", row=1, col=2)
    
    fig.update_xaxes(title_text="Season", row=2, col=1)
    fig.update_yaxes(title_text="Seasons to Max (capped at 1000)", type="log", row=2, col=1)
    fig.update_yaxes(title_text="TwaPrice", secondary_y=True, row=2, col=1)
    
    fig.update_xaxes(title_text="Target Ramp Time", row=2, col=2)
    fig.update_yaxes(title_text="Required Δd (%)", row=2, col=2)
    
    # Save as HTML file
    pyo.plot(fig, filename=output_file, auto_open=False)
    print(f"Interactive ramp dashboard saved as: {output_file}")
    
    return fig

def create_delta_explorer(df: pd.DataFrame, output_file: str = "ramp_rate_visualizations/delta_explorer.html"):
    """Create focused interactive tool to explore different Δd values."""
    
    # Define all available delta_d values
    all_deltas = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0]
    
    # Create initial plot with first delta value
    initial_delta = 1.0
    delta_d_pct = f"{initial_delta:.2f}".replace('.', '_')
    max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
    
    # Sample data for performance
    sampled_df = df.iloc[::5]
    
    fig = go.Figure()
    
    # Add initial trace
    fig.add_trace(
        go.Scatter(
            x=sampled_df['Season'],
            y=np.minimum(sampled_df[max_col], 1000),
            mode='lines',
            name=f'Δd={initial_delta}%',
            line=dict(width=3),
            visible=True
        )
    )
    
    # Create buttons for each delta value
    buttons = []
    
    for delta_d in all_deltas:
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        # Create new trace data
        y_data = np.minimum(sampled_df[max_col], 1000)
        
        buttons.append(dict(
            label=f"Δd = {delta_d}%",
            method="restyle",
            args=[{"y": [y_data], "name": [f"Δd = {delta_d}%"]}]
        ))
    
    # Add dropdown menu
    fig.update_layout(
        title="Δd Explorer - Select Different Delta Values",
        xaxis_title="Season",
        yaxis_title="Seasons to Max Capacity (capped at 1000)",
        yaxis_type="log",
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=0.02,
                xanchor="left",
                y=1.02,
                yanchor="top"
            )
        ],
        height=600
    )
    
    # Save as HTML file
    pyo.plot(fig, filename=output_file, auto_open=False)
    print(f"Delta explorer saved as: {output_file}")
    
    return fig

def create_target_based_analysis(df: pd.DataFrame):
    """Create detailed target-based analysis showing required Δd for different scenarios."""
    
    # Define target scenarios
    scenarios = {
        'Fast Ramp (50-100 seasons)': [50, 75, 100],
        'Moderate Ramp (100-200 seasons)': [100, 150, 200],
        'Slow Ramp (200-500 seasons)': [200, 300, 500]
    }
    
    # Create analysis for different price percentiles
    price_percentiles = [10, 25, 50, 75, 90]
    price_values = [df['twaPrice'].quantile(p/100) for p in price_percentiles]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Required Δd by Price Level', 'Ramp Time Distribution', 
                       'Price Impact Analysis', 'Scenario Comparison'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Required Δd by Price Level (Top Left)
    target_seasons = [50, 100, 200, 500]
    colors_targets = ['red', 'orange', 'blue', 'green']
    
    for i, target in enumerate(target_seasons):
        required_deltas = []
        for price in price_values:
            required_delta = (0.99 / (target * price)) * 100
            required_deltas.append(required_delta)
        
        fig.add_trace(
            go.Scatter(
                x=[f'{p}th' for p in price_percentiles],
                y=required_deltas,
                mode='lines+markers',
                name=f'{target} seasons',
                line=dict(color=colors_targets[i], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
    
    # 2. Ramp Time Distribution (Top Right)
    # Show distribution of ramp times for key Δd values at median price
    median_price = df['twaPrice'].median()
    key_deltas = [0.5, 1.0, 2.0, 5.0]
    
    for delta_d in key_deltas:
        delta_d_pct = f"{delta_d:.2f}".replace('.', '_')
        max_col = f"seasons_to_max_capacity_dd_{delta_d_pct}pct"
        
        # Calculate ramp times for this delta at current prices
        sample_data = df.iloc[::50]  # Sample for performance
        ramp_times = np.minimum(sample_data[max_col], 1000)
        
        fig.add_trace(
            go.Box(
                y=ramp_times,
                name=f'Δd={delta_d}%',
                boxpoints='outliers'
            ),
            row=1, col=2
        )
    
    # 3. Price Impact Analysis (Bottom Left)
    # Show how price changes affect ramp times for fixed Δd
    fixed_delta = 2.0  # Example fixed delta
    price_range = np.linspace(df['twaPrice'].quantile(0.1), df['twaPrice'].quantile(0.9), 20)
    
    ramp_times_by_price = []
    for price in price_range:
        # Calculate seasons to max for this price and fixed delta
        seasons = 0.99 / (fixed_delta/100 * price)
        ramp_times_by_price.append(min(seasons, 1000))  # Cap at 1000
    
    fig.add_trace(
        go.Scatter(
            x=price_range,
            y=ramp_times_by_price,
            mode='lines',
            name=f'Δd={fixed_delta}%',
            line=dict(width=3, color='purple')
        ),
        row=2, col=1
    )
    
    # 4. Scenario Comparison (Bottom Right)
    # Compare different scenarios at median price
    scenario_names = []
    scenario_deltas = []
    scenario_colors = []
    
    color_map = {'Fast Ramp (50-100 seasons)': 'red', 
                 'Moderate Ramp (100-200 seasons)': 'orange', 
                 'Slow Ramp (200-500 seasons)': 'blue'}
    
    for scenario_name, targets in scenarios.items():
        for target in targets:
            required_delta = (0.99 / (target * median_price)) * 100
            scenario_names.append(f'{target}s')
            scenario_deltas.append(required_delta)
            scenario_colors.append(color_map[scenario_name])
    
    fig.add_trace(
        go.Bar(
            x=scenario_names,
            y=scenario_deltas,
            marker_color=scenario_colors,
            name='Required Δd'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title="Target-Based Ramp Analysis - Reverse Engineering Optimal Δd",
        height=800,
        showlegend=True
    )
    
    # Update axes
    fig.update_xaxes(title_text="Price Percentile", row=1, col=1)
    fig.update_yaxes(title_text="Required Δd (%)", row=1, col=1)
    
    fig.update_xaxes(title_text="Δd Value", row=1, col=2)
    fig.update_yaxes(title_text="Ramp Time Distribution", type="log", row=1, col=2)
    
    fig.update_xaxes(title_text="TwaPrice", row=2, col=1)
    fig.update_yaxes(title_text="Seasons to Max", type="log", row=2, col=1)
    
    fig.update_xaxes(title_text="Target Scenarios", row=2, col=2)
    fig.update_yaxes(title_text="Required Δd (%)", row=2, col=2)
    
    save_path = "ramp_rate_visualizations/target_based_analysis.html"
    pyo.plot(fig, filename=save_path, auto_open=False)
    print(f"Target-based analysis saved as: {save_path}")
    
    return fig

def main():
    """Main function to create interactive ramp rate visualizations."""
    csv_file = "pinto_season_data_with_ramp_analysis.csv"
    
    print("Loading ramp rate analysis data...")
    df = load_ramp_data(csv_file)
    
    if df is None:
        return
    
    # Ensure output directory exists
    os.makedirs("ramp_rate_visualizations", exist_ok=True)
    
    print("\n1. Creating comprehensive interactive dashboard...")
    create_interactive_ramp_dashboard(df)
    
    print("\n2. Creating Δd explorer tool...")
    create_delta_explorer(df)
    
    print("\n3. Creating target-based analysis...")
    create_target_based_analysis(df)
    
    print("\nInteractive ramp rate visualizations completed!")
    print("Open the HTML files in your browser to explore the data interactively.")

if __name__ == "__main__":
    main()