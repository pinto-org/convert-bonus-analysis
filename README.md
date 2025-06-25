# Pinto DeFi Protocol: Convert Capacity Analysis

This repository contains a comprehensive analysis of the Pinto DeFi protocol's convert capacity system, focusing on capacity scaling and ramp rate optimization for protocol stability.

## 📊 Overview

This analysis examines how the Pinto protocol should manage its convert capacity system, which allows users to convert between different protocol tokens. The system needs to:

1. **Scale capacity appropriately** based on demand (S parameter analysis)
2. **Ramp capacity up/down at optimal rates** based on market conditions (Δd parameter analysis)

We analyze **5,213+ seasons** of historical data to understand price dynamics and optimal parameter selection.

## 🎯 What We're Analyzing

### **Convert Capacity System**
- **Capacity**: Maximum amount that can be converted per season
- **S Parameter**: Scaling factor that determines capacity = |maxNegativeTwaDeltaB| / S
- **Δd Parameter**: Rate at which capacity ramps up/down based on market conditions
- **TwaPrice**: Time-weighted average price that influences ramping speed

### **Key Metrics**
- **twaDeltaB**: Delta between current and target price (negative = below peg)
- **maxNegativeTwaDeltaB**: Most negative twaDeltaB value seen since genesis
- **Ramp Times**: How many seasons to reach maximum/minimum capacity
- **Price Regimes**: Different market conditions affecting optimal parameters

## 🚀 Analysis Flow

### **Step 1: Data Collection**
```bash
python3 fetch_season_data.py
```
Fetches season data from two Pinto subgraphs and merges into `pinto_season_data.csv`

### **Step 2: Maximum Negative TwaDeltaB Tracking**  
```bash
python3 get_max_negative_twadeltab.py
```
Tracks the maximum negative twaDeltaB values since genesis, identifies when new maximums occur

### **Step 3: Capacity Analysis**
```bash
python3 add_capacity_analysis.py
```
Calculates capacity for different S values (100-1000) showing how scaling affects capacity

### **Step 4: Ramp Rate Analysis**
```bash
python3 ramp_rate_analysis.py
```
Analyzes ramping behavior for different Δd values (0.1%-5%) and provides optimization recommendations

### **Step 5-7: Visualization Generation**
```bash
# Capacity visualizations
python3 plot_capacity_analysis.py
python3 interactive_capacity_dashboard.py

# Ramp rate visualizations  
python3 visualize_ramp_rates.py
python3 interactive_ramp_dashboard.py
python3 advanced_ramp_visualizations.py
```

## 📁 Visualization Folders

### **`capacity_visualizations/` - S Parameter Analysis**

Understanding how different S values affect capacity scaling:

#### **Static Visualizations (PNG)**
- **`capacity_timeseries.png`**: Shows how capacity evolves over time for S=100 to S=1000
  - *Insight*: Lower S = higher capacity but more volatile; Higher S = lower but more stable capacity
  
- **`capacity_heatmap.png`**: Season vs S-value heatmap with capacity as color intensity
  - *Insight*: Identifies optimal S ranges for different time periods
  
- **`capacity_boxplots.png`**: Statistical distributions showing capacity variance by S value
  - *Insight*: Compare stability vs responsiveness trade-offs across S values
  
- **`key_moments_analysis.png`**: Focuses on 10 critical seasons when maxNegativeTwaDeltaB reached new lows
  - *Insight*: Shows how capacity would scale during major protocol stress events

#### **Interactive Tools (HTML)**
- **`capacity_dashboard.html`**: 4-panel interactive dashboard for exploring capacity relationships
- **`interactive_timeseries.html`**: Toggle different S values on/off to compare behaviors

### **`ramp_rate_visualizations/` - Δd Parameter Analysis**

Understanding optimal ramping rates for capacity adjustments:

#### **Core Analysis (PNG)**
- **`price_delta_heatmaps.png`**: **MOST IMPORTANT** - Shows seasons-to-max and seasons-to-min capacity across price and Δd combinations
  - *Insight*: Directly answers "What Δd should I choose for different price scenarios?"
  - *Usage*: Find your expected price range, choose Δd that gives reasonable ramp times
  
- **`ramp_tradeoff_analysis.png`**: Scatter plots showing ramp-up vs ramp-down rate trade-offs
  - *Insight*: Higher Δd = faster ramp-up but also faster ramp-down; shows the fundamental trade-off
  
- **`ramp_timeseries_analysis.png`**: How ramp times evolve over 5,213 seasons for key Δd values
  - *Insight*: Shows how price volatility affects ramping behavior over time
  
- **`ramp_small_multiples.png`**: Grid comparing 6 key Δd values (0.5% to 5%) side-by-side
  - *Insight*: Easy visual comparison of different Δd behaviors

#### **Advanced Analysis (PNG)**
- **`3d_surface_plot.png`**: 3D surface showing Price × Δd × Ramp Time relationship
  - *Insight*: Complete mathematical relationship landscape
  
- **`contour_plots.png`**: Contour plots with ramp speed zones (Very Fast, Fast, Moderate, Slow, Very Slow)
  - *Insight*: Identifies "speed zones" for different Price-Δd combinations
  
- **`price_regime_analysis.png`**: 4-panel analysis comparing behavior across different price regimes
  - *Insight*: Shows how optimal Δd varies during different market conditions

#### **Interactive Tools (HTML)**
- **`ramp_interactive_dashboard.html`**: Comprehensive 4-panel dashboard with heatmaps, trade-offs, and time series
- **`interactive_3d_surface.html`**: Rotatable 3D surface for exploring Price-Δd-RampTime relationships
- **`target_based_analysis.html`**: Reverse engineering tool - input target ramp time, get required Δd
- **`delta_explorer.html`**: Dropdown selector to explore individual Δd values

## 🎯 Key Recommendations

### **S Parameter (Capacity Scaling)**
Based on capacity analysis:
- **S = 200-400**: Balanced approach for most scenarios
- **S = 100**: High responsiveness, use during high volatility periods
- **S = 500-1000**: Conservative approach for stable periods

### **Δd Parameter (Ramp Rates)**
Based on ramp rate analysis across price regimes:

#### **By Price Level**
- **Low Price (0.518-0.774)**: Δd ≈ 1.38% for 100-season ramp
- **Medium Price (0.775-0.997)**: Δd ≈ 1.01-1.20% for 100-season ramp  
- **High Price (0.998+)**: Δd ≈ 0.99% for 100-season ramp

#### **By Desired Ramp Speed**
- **Fast Ramping (50-100 seasons)**: Δd = 1.15-2.30%
- **Moderate Ramping (100-200 seasons)**: Δd = 0.58-1.15%
- **Slow Ramping (200-500 seasons)**: Δd = 0.23-0.58%

## 📈 Files Generated

### **CSV Data Files**
1. `pinto_season_data.csv` - Raw season data (5 columns)
2. `pinto_season_data_with_max_negative.csv` - Adds max negative tracking (7 columns)
3. `pinto_season_data_with_capacity_analysis.csv` - Adds capacity analysis (17 columns)
4. `pinto_season_data_with_ramp_analysis.csv` - Complete analysis (101 columns)

### **Visualization Files**
- **6 files** in `capacity_visualizations/` (4 PNG + 2 HTML)
- **11 files** in `ramp_rate_visualizations/` (7 PNG + 4 HTML)

## 🔧 Technical Details

### **Capacity Formula**
```
Capacity = |maxNegativeTwaDeltaB| / S
```

### **Ramp Rate Formula**
```
D_t = {
  min(1, D_{t-1} + Δd × P_{t-1}),     if Bonus Convert Capacity Reached
  D_{t-1},                            if Bonus Convert Capacity Almost Reached  
  max(0.01, D_{t-1} - 0.01/(Δd × P_{t-1})), else
}
```

### **Key Relationships**
- **Increase Rate**: Δd × twaPrice (%/season)
- **Decrease Rate**: 0.01 / (Δd × twaPrice) (%/season)
- **Seasons to Max**: 0.99 / (Δd × twaPrice)
- **Seasons to Min**: 0.99 / (0.01 / (Δd × twaPrice))

This analysis provides a data-driven foundation for optimizing Pinto's convert capacity system to maintain protocol stability while ensuring adequate responsiveness to market conditions.