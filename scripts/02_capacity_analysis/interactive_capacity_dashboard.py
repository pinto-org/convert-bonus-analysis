#!/usr/bin/env python3
"""
Interactive Plotly dashboard for capacity analysis exploration.
Creates an interactive web-based dashboard with multiple linked views.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import os

def load_data(csv_file: str) -> pd.DataFrame:
    """Load the capacity analysis data."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run add_capacity_analysis.py first.")
        return None
    
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} seasons of data")
    return df

def create_interactive_dashboard(df: pd.DataFrame, output_file: str = "../../visualizations/capacity_visualizations/capacity_dashboard.html"):
    """Create comprehensive interactive dashboard."""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Capacity Time Series', 'Capacity Heatmap', 
                       'Capacity Distribution', 'Key Moments Analysis'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Multi-line time series (top left)
    s_values = list(range(100, 1100, 100))
    colors = px.colors.qualitative.Set3
    
    for i, s_value in enumerate(s_values):
        column_name = f'Capacity_at_Smin_{s_value}'
        fig.add_trace(
            go.Scatter(
                x=df['Season'], 
                y=df[column_name],
                mode='lines',
                name=f'S={s_value}',
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate=f'<b>S={s_value}</b><br>' +
                             'Season: %{x}<br>' +
                             'Capacity: %{y:.3f}<br>' +
                             '<extra></extra>'
            ),
            row=1, col=1
        )
    
    # 2. Heatmap data preparation (top right)
    # Sample every 25th season for better visualization
    sampled_df = df.iloc[::25].copy()
    capacity_columns = [f'Capacity_at_Smin_{s}' for s in s_values]
    
    # Create heatmap
    fig.add_trace(
        go.Heatmap(
            z=sampled_df[capacity_columns].values.T,
            x=sampled_df['Season'].values,
            y=[f'S={s}' for s in s_values],
            colorscale='Viridis',
            showscale=True,
            hovertemplate='Season: %{x}<br>' +
                         'S Value: %{y}<br>' +
                         'Capacity: %{z:.3f}<br>' +
                         '<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Box plot data (bottom left)
    # Create box plot for each S value
    for i, s_value in enumerate(s_values):
        column_name = f'Capacity_at_Smin_{s_value}'
        fig.add_trace(
            go.Box(
                y=df[column_name],
                name=f'S={s_value}',
                boxpoints='outliers',
                marker_color=colors[i % len(colors)]
            ),
            row=2, col=1
        )
    
    # 4. Key moments analysis (bottom right)
    key_moments = df[df['isNewMaxTwaDeltaB'] == True]
    
    # Add background line for context
    fig.add_trace(
        go.Scatter(
            x=df['Season'],
            y=df['maxNegativeTwaDeltaB'],
            mode='lines',
            name='Max Negative TwaDeltaB',
            line=dict(color='lightgray', width=1),
            opacity=0.5,
            hovertemplate='Season: %{x}<br>' +
                         'Max Negative TwaDeltaB: %{y:.3f}<br>' +
                         '<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Add key moments as scatter points
    if not key_moments.empty:
        fig.add_trace(
            go.Scatter(
                x=key_moments['Season'],
                y=key_moments['maxNegativeTwaDeltaB'],
                mode='markers+text',
                name='Key Moments',
                marker=dict(color='red', size=10),
                text=[f'S{int(season)}' for season in key_moments['Season']],
                textposition='top center',
                hovertemplate='<b>Key Moment</b><br>' +
                             'Season: %{x}<br>' +
                             'Max Negative TwaDeltaB: %{y:.3f}<br>' +
                             '<extra></extra>'
            ),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Interactive Capacity Analysis Dashboard",
            x=0.5,
            font=dict(size=20)
        ),
        height=800,
        showlegend=True,
        hovermode='closest'
    )
    
    # Update subplot titles and axes
    fig.update_xaxes(title_text="Season", row=1, col=1)
    fig.update_yaxes(title_text="Capacity", row=1, col=1)
    fig.update_xaxes(title_text="Season", row=1, col=2)
    fig.update_yaxes(title_text="S Value", row=1, col=2)
    fig.update_xaxes(title_text="S Value", row=2, col=1)
    fig.update_yaxes(title_text="Capacity", row=2, col=1)
    fig.update_xaxes(title_text="Season", row=2, col=2)
    fig.update_yaxes(title_text="Max Negative TwaDeltaB", row=2, col=2)
    
    # Save as HTML file
    pyo.plot(fig, filename=output_file, auto_open=False)
    print(f"Interactive dashboard saved as: {output_file}")
    
    return fig

def create_simple_interactive_timeseries(df: pd.DataFrame, output_file: str = "../../visualizations/capacity_visualizations/interactive_timeseries.html"):
    """Create a focused interactive time series plot with toggleable lines."""
    
    fig = go.Figure()
    
    s_values = list(range(100, 1100, 100))
    colors = px.colors.qualitative.Set3
    
    for i, s_value in enumerate(s_values):
        column_name = f'Capacity_at_Smin_{s_value}'
        fig.add_trace(
            go.Scatter(
                x=df['Season'],
                y=df[column_name],
                mode='lines',
                name=f'S={s_value}',
                line=dict(color=colors[i % len(colors)], width=2),
                visible=True,
                hovertemplate=f'<b>S={s_value}</b><br>' +
                             'Season: %{x}<br>' +
                             'Capacity: %{y:.3f}<br>' +
                             '<extra></extra>'
            )
        )
    
    # Add dropdown menu for S value selection
    buttons = []
    
    # Show all lines
    buttons.append(dict(
        label="All S Values",
        method="update",
        args=[{"visible": [True] * len(s_values)}]
    ))
    
    # Individual S values
    for i, s_value in enumerate(s_values):
        visibility = [False] * len(s_values)
        visibility[i] = True
        buttons.append(dict(
            label=f"S={s_value}",
            method="update",
            args=[{"visible": visibility}]
        ))
    
    # Compare high vs low S values
    high_low_visibility = [False] * len(s_values)
    high_low_visibility[0] = True  # S=100
    high_low_visibility[-1] = True  # S=1000
    buttons.append(dict(
        label="Compare S=100 vs S=1000",
        method="update",
        args=[{"visible": high_low_visibility}]
    ))
    
    fig.update_layout(
        title="Interactive Capacity Time Series - Toggle S Values",
        xaxis_title="Season",
        yaxis_title="Capacity",
        hovermode='x unified',
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
    print(f"Interactive time series saved as: {output_file}")
    
    return fig

def main():
    """Main function to create interactive visualizations."""
    csv_file = "../../data/pinto_season_data_with_capacity_analysis.csv"
    
    print("Loading capacity analysis data...")
    df = load_data(csv_file)
    
    if df is None:
        return
    
    print("\n1. Creating comprehensive interactive dashboard...")
    create_interactive_dashboard(df)
    
    print("\n2. Creating focused interactive time series...")
    create_simple_interactive_timeseries(df)
    
    print("\nInteractive visualizations completed!")
    print("Open the HTML files in your browser to explore the data interactively.")

if __name__ == "__main__":
    main()