#!/usr/bin/env python3
"""
Master script to run the complete Pinto convert capacity analysis.
Executes all analysis steps in the correct order.
"""

import os
import subprocess
import sys

def run_script(script_path, description):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        # Change to script directory and run
        script_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)
        
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"💥 {description} crashed: {e}")
        return False
    
    return True

def main():
    """Run the complete analysis pipeline."""
    print("🔬 Starting Pinto Convert Capacity Analysis Pipeline")
    print("This will fetch data, run analysis, and generate all visualizations.")
    
    # Ensure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("visualizations/capacity_visualizations", exist_ok=True)
    os.makedirs("visualizations/ramp_rate_visualizations", exist_ok=True)
    
    # Define the analysis pipeline
    pipeline = [
        # Step 1: Data Collection
        ("scripts/01_data_collection/fetch_season_data.py", "Step 1: Fetch Season Data from Subgraphs"),
        ("scripts/01_data_collection/get_max_twadeltab.py", "Step 2: Track Maximum Negative TwaDeltaB"),
        ("scripts/01_data_collection/plot_max_twa_delta_b.py", "Step 3: Plot Maximum Negative Evolution"),
        
        # Step 2: Capacity Analysis
        ("scripts/02_capacity_analysis/add_capacity_analysis.py", "Step 4: Add Capacity Analysis (S Parameters)"),
        ("scripts/02_capacity_analysis/plot_capacity_analysis.py", "Step 5: Generate Capacity Visualizations"),
        ("scripts/02_capacity_analysis/interactive_capacity_dashboard.py", "Step 6: Create Interactive Capacity Dashboard"),
        
        # Step 3: Ramp Rate Analysis
        ("scripts/03_ramp_analysis/ramp_rate_analysis.py", "Step 7: Ramp Rate Analysis (Δd Parameters)"),
        ("scripts/03_ramp_analysis/visualize_ramp_rates.py", "Step 8: Generate Ramp Rate Visualizations"),
        ("scripts/03_ramp_analysis/interactive_ramp_dashboard.py", "Step 9: Create Interactive Ramp Dashboard"),
        ("scripts/03_ramp_analysis/advanced_ramp_visualizations.py", "Step 10: Advanced Ramp Visualizations"),
    ]
    
    # Track progress
    total_steps = len(pipeline)
    completed_steps = 0
    
    # Run each step
    for script_path, description in pipeline:
        if run_script(script_path, description):
            completed_steps += 1
            print(f"📊 Progress: {completed_steps}/{total_steps} steps completed")
        else:
            print(f"🛑 Pipeline stopped at: {description}")
            print(f"📊 Completed: {completed_steps}/{total_steps} steps")
            return False
    
    # Success summary
    print(f"\n{'='*60}")
    print("🎉 ANALYSIS PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"✅ All {total_steps} steps completed")
    print(f"📁 Data files created in: ./data/")
    print(f"📊 Visualizations created in: ./visualizations/")
    print(f"")
    print(f"📈 Generated Files:")
    print(f"   • 4 CSV files with complete analysis")
    print(f"   • 6 capacity visualization files")
    print(f"   • 11 ramp rate visualization files")
    print(f"")
    print(f"🔍 Next Steps:")
    print(f"   • Open HTML files in browser for interactive exploration")
    print(f"   • Review README.md for interpretation guide")
    print(f"   • Use visualizations to optimize S and Δd parameters")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)