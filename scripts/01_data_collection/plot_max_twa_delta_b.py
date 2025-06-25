#!/usr/bin/env python3
"""
Plotting script to visualize maxNegativeTwaDeltaB values across all seasons.
"""

import csv
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_max_twa_delta_b(csv_file: str):
    """Plot maxNegativeTwaDeltaB for every season."""
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run analysis.py first.")
        return
    
    # Read the CSV data
    df = pd.read_csv(csv_file)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot maxNegativeTwaDeltaB values
    plt.plot(df['Season'], df['maxNegativeTwaDeltaB'], 
             linewidth=2, color='red', alpha=0.8, label='Max Negative TwaDeltaB')
    
    # Highlight points where new maximums occur
    new_max_data = df[df['isNewMaxTwaDeltaB'] == True]
    if not new_max_data.empty:
        plt.scatter(new_max_data['Season'], new_max_data['maxNegativeTwaDeltaB'], 
                   color='darkred', s=50, zorder=5, label='New Maximum Points')
        
        # Add text annotations showing the exact values
        for _, row in new_max_data.iterrows():
            plt.annotate(f'{row["maxNegativeTwaDeltaB"]:.0f}', 
                        xy=(row['Season'], row['maxNegativeTwaDeltaB']),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # Formatting
    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Max Negative TwaDeltaB (thousands)', fontsize=12)
    
    # Format y-axis to show values in thousands
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    plt.title('Maximum Negative TwaDeltaB Since Genesis', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Add some styling
    plt.tight_layout()
    
    # Save the plot
    output_file = '../../data/max_negative_twa_delta_b_plot.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()  # Close the figure to free memory
    
    print(f"Plot saved as: {output_file}")
    print(f"Total seasons plotted: {len(df)}")
    print(f"Final max negative value: {df['maxNegativeTwaDeltaB'].iloc[-1]}")
    
    # Print some statistics
    new_max_count = len(new_max_data)
    print(f"Number of times new maximum was reached: {new_max_count}")
    
    if new_max_count > 0:
        print("Seasons where new maximums occurred:")
        for _, row in new_max_data.iterrows():
            print(f"  Season {int(row['Season'])}: {row['maxNegativeTwaDeltaB']:.2f}")

def main():
    """Main function to create the plot."""
    csv_file = "../../data/pinto_season_data_with_max_negative.csv"
    plot_max_twa_delta_b(csv_file)

if __name__ == "__main__":
    main()