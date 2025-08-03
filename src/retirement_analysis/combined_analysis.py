#!/usr/bin/env python3
"""
Combined Analysis: Run both deterministic and Monte Carlo analyses
"""

from .roth_conversion_strategy import RothConversionAnalyzer, main as roth_main
from .monte_carlo_simulation import MonteCarloRothAnalyzer, main as mc_main

def run_combined_analysis():
    """Run both analyses and compare results."""
    print("🎯 COMPREHENSIVE RETIREMENT ANALYSIS")
    print("=" * 60)
    print("Running both deterministic and Monte Carlo analyses...")
    
    # Run deterministic analysis
    print("\n1️⃣ DETERMINISTIC ANALYSIS (Base Case)")
    print("-" * 40)
    base_analyzer, base_results = roth_main()
    
    # Run Monte Carlo analysis
    print("\n2️⃣ MONTE CARLO ANALYSIS (1000 Simulations)")
    print("-" * 40)
    mc_analyzer, mc_results, mc_analyses = mc_main()
    
    # Compare results
    print("\n📊 COMPARISON SUMMARY")
    print("=" * 50)
    base_final_roth = base_results['Roth_End'].iloc[-1]
    mc_avg_roth = mc_analyses['base_case']['avg_final_roth']
    mc_preservation_rate = mc_analyses['base_case']['roth_preservation_rate']
    
    print(f"Deterministic Final Roth: ${base_final_roth:,.0f}")
    print(f"Monte Carlo Avg Roth: ${mc_avg_roth:,.0f}")
    print(f"Monte Carlo Preservation Rate: {mc_preservation_rate:.1%}")
    print(f"Difference: ${mc_avg_roth - base_final_roth:,.0f}")
    
    return base_analyzer, base_results, mc_analyzer, mc_results, mc_analyses

if __name__ == "__main__":
    run_combined_analysis()