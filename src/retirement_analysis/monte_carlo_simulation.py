#!/usr/bin/env python3
"""
Monte Carlo Simulation for Roth Conversion Strategy
Tests strategy performance under various market conditions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import random
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from dataclasses import dataclass
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


@dataclass
class SimulationResult:
    """Store results from a single simulation run."""
    simulation_id: int
    final_net_worth: float
    final_roth_balance: float
    total_conversions: float
    total_taxes: float
    roth_preserved: bool
    years_with_shortfall: int
    worst_year_return: float
    best_year_return: float
    sequence_of_returns_risk: float


class MonteCarloRothAnalyzer:
    """Monte Carlo simulation for Roth conversion strategy under market volatility."""
    
    def __init__(self, num_simulations: int = 1000):
        # Base parameters (same as original strategy)
        self.num_simulations = num_simulations
        self.start_year = 2026
        self.start_age = 62
        self.end_age = 85
        self.ss_start_age = 67
        self.rmd_age = 73
        
        # Starting account balances
        self.initial_ira = 1_250_000
        self.initial_roth = 250_000
        self.initial_brokerage = 1_200_000
        self.initial_savings = 300_000
        self.home_equity = 900_000
        
        # Economic assumptions
        self.base_expenses = 60_000
        self.travel_expenses = 20_000
        self.car_purchase = 20_000
        self.home_renovation = 80_000
        self.ss_annual_benefit = 36_000
        self.inflation_rate = 0.03
        
        # Market assumptions for Monte Carlo
        self.mean_return = 0.06        # 6% average return
        self.return_volatility = 0.18  # 18% standard deviation (realistic for 60/40 portfolio)
        self.correlation_factor = 0.7  # Correlation between consecutive years
        
        # Tax rates and brackets
        self.standard_deduction = 15_000
        self.tax_brackets = {
            'bracket_12_max': 48_475,
            'bracket_22_max': 103_350,
            'bracket_24_max': 197_300
        }
        self.tax_rate_ira = 0.22
        self.tax_rate_conversion = 0.22
        self.tax_rate_brokerage = 0.15
        self.tax_rate_roth = 0.00
        
        # Market scenarios for testing
        self.scenarios = {
            'base_case': {'mean': 0.06, 'volatility': 0.18},
            'low_return': {'mean': 0.04, 'volatility': 0.18},
            'high_volatility': {'mean': 0.06, 'volatility': 0.25},
            'stagflation': {'mean': 0.03, 'volatility': 0.22},
            'great_recession': {'mean': 0.02, 'volatility': 0.30}
        }
    
    def generate_market_returns(self, scenario: str = 'base_case') -> List[float]:
        """Generate correlated market returns for the retirement period."""
        params = self.scenarios[scenario]
        mean_return = params['mean']
        volatility = params['volatility']
        
        years = self.end_age - self.start_age + 1
        returns = []
        
        # Generate first year return
        returns.append(np.random.normal(mean_return, volatility))
        
        # Generate subsequent years with correlation
        for year in range(1, years):
            # Correlated return based on previous year
            correlated_component = self.correlation_factor * returns[year-1]
            random_component = (1 - self.correlation_factor) * np.random.normal(mean_return, volatility)
            new_return = correlated_component + random_component
            
            # Add some mean reversion
            mean_reversion = 0.1 * (mean_return - returns[year-1])
            new_return += mean_reversion
            
            returns.append(new_return)
        
        return returns
    
    def calculate_expenses(self, age: int, year: int) -> float:
        """Calculate expenses with inflation adjustment."""
        years_since_start = year - self.start_year
        inflation_factor = (1 + self.inflation_rate) ** years_since_start
        
        total_expenses = self.base_expenses * inflation_factor
        
        if 62 <= age <= 70:
            total_expenses += self.travel_expenses * inflation_factor
        if age == 63:
            total_expenses += self.car_purchase * inflation_factor
        elif age == 64:
            total_expenses += self.home_renovation * inflation_factor
        
        return total_expenses
    
    def get_social_security(self, age: int) -> float:
        """Get Social Security benefit."""
        return self.ss_annual_benefit if age >= self.ss_start_age else 0
    
    def calculate_conversion_capacity(self, current_income: float) -> float:
        """Calculate conversion capacity for 22% bracket."""
        taxable_capacity = self.tax_brackets['bracket_22_max'] - self.standard_deduction
        return max(0, taxable_capacity - current_income)
    
    def get_conversion_target(self, age: int) -> float:
        """Get age-appropriate conversion target."""
        if 62 <= age <= 66:
            return 80_000
        elif age == 67:
            return 60_000
        elif 68 <= age <= 72:
            return 50_000
        elif age >= 73:
            return 30_000
        else:
            return 0
    
    def run_single_simulation(self, sim_id: int, scenario: str = 'base_case') -> SimulationResult:
        """Run a single simulation with given market returns."""
        # Generate market returns for this simulation
        market_returns = self.generate_market_returns(scenario)
        
        # Initialize balances
        ira_balance = self.initial_ira
        roth_balance = self.initial_roth
        brokerage_balance = self.initial_brokerage
        savings_balance = self.initial_savings
        
        # Tracking variables
        total_conversions = 0
        total_taxes = 0
        years_with_shortfall = 0
        roth_withdrawals = 0
        
        for year_idx in range(len(market_returns)):
            age = self.start_age + year_idx
            year = self.start_year + year_idx
            market_return = market_returns[year_idx]
            
            # Apply market returns (could be negative!)
            ira_balance *= (1 + market_return)
            roth_balance *= (1 + market_return)
            brokerage_balance *= (1 + market_return)
            savings_balance *= (1 + market_return)
            
            # Ensure no negative balances
            ira_balance = max(0, ira_balance)
            roth_balance = max(0, roth_balance)
            brokerage_balance = max(0, brokerage_balance)
            savings_balance = max(0, savings_balance)
            
            # Calculate expenses and income
            total_expenses = self.calculate_expenses(age, year)
            ss_income = self.get_social_security(age)
            net_expenses = max(0, total_expenses - ss_income)
            
            # ROTH CONVERSION LOGIC
            conversion_amount = 0
            if 62 <= age <= 73 and ira_balance > 0:
                # Estimate taxable income
                estimated_withdrawals = max(0, net_expenses - savings_balance)
                estimated_brokerage = min(estimated_withdrawals / 0.85, brokerage_balance)
                estimated_ira = max(0, (estimated_withdrawals - estimated_brokerage * 0.85) / 0.78)
                current_taxable_income = estimated_ira + estimated_brokerage * 0.5
                
                # Calculate conversion capacity
                conversion_capacity = self.calculate_conversion_capacity(current_taxable_income)
                target_conversion = min(
                    self.get_conversion_target(age),
                    conversion_capacity,
                    ira_balance
                )
                
                # Check affordability
                if target_conversion > 0:
                    conversion_tax = target_conversion * self.tax_rate_conversion
                    available_for_tax = savings_balance + brokerage_balance * 0.4
                    
                    if available_for_tax >= conversion_tax and target_conversion >= 10_000:
                        conversion_amount = target_conversion
                        ira_balance -= conversion_amount
                        roth_balance += conversion_amount
                        total_conversions += conversion_amount
                        
                        # Pay conversion tax
                        if savings_balance >= conversion_tax:
                            savings_balance -= conversion_tax
                        else:
                            remaining_tax = conversion_tax - savings_balance
                            savings_balance = 0
                            brokerage_balance -= remaining_tax
                        
                        total_taxes += conversion_tax
            
            # EXPENSE COVERAGE LOGIC
            remaining_need = net_expenses
            
            # Use savings
            if remaining_need > 0 and savings_balance > 0:
                used = min(remaining_need, savings_balance)
                savings_balance -= used
                remaining_need -= used
            
            # Use brokerage
            if remaining_need > 0 and brokerage_balance > 0:
                gross_needed = remaining_need / (1 - self.tax_rate_brokerage)
                used = min(gross_needed, brokerage_balance)
                net_received = used * (1 - self.tax_rate_brokerage)
                brokerage_balance -= used
                remaining_need -= net_received
                total_taxes += used * self.tax_rate_brokerage
            
            # Use IRA
            if remaining_need > 0 and ira_balance > 0:
                gross_needed = remaining_need / (1 - self.tax_rate_ira)
                used = min(gross_needed, ira_balance)
                net_received = used * (1 - self.tax_rate_ira)
                ira_balance -= used
                remaining_need -= net_received
                total_taxes += used * self.tax_rate_ira
            
            # Use Roth (track this as failure)
            if remaining_need > 0:
                if roth_balance >= remaining_need:
                    roth_balance -= remaining_need
                    roth_withdrawals += remaining_need
                    remaining_need = 0
                else:
                    roth_withdrawals += roth_balance
                    remaining_need -= roth_balance
                    roth_balance = 0
                    years_with_shortfall += 1
        
        # Calculate final metrics
        final_home_equity = self.home_equity * ((1 + self.inflation_rate) ** (self.end_age - self.start_age))
        final_net_worth = ira_balance + roth_balance + savings_balance + brokerage_balance + final_home_equity
        
        # Calculate sequence of returns risk (early years impact)
        early_years_avg = np.mean(market_returns[:5])  # First 5 years
        sequence_risk = abs(early_years_avg - self.mean_return)
        
        return SimulationResult(
            simulation_id=sim_id,
            final_net_worth=final_net_worth,
            final_roth_balance=roth_balance,
            total_conversions=total_conversions,
            total_taxes=total_taxes,
            roth_preserved=(roth_withdrawals == 0),
            years_with_shortfall=years_with_shortfall,
            worst_year_return=min(market_returns),
            best_year_return=max(market_returns),
            sequence_of_returns_risk=sequence_risk
        )
    
    def run_monte_carlo_analysis(self, scenario: str = 'base_case') -> List[SimulationResult]:
        """Run Monte Carlo analysis with parallel processing."""
        print(f"🎲 Running {self.num_simulations:,} Monte Carlo simulations for '{scenario}' scenario...")
        print(f"Market assumptions: {self.scenarios[scenario]['mean']:.1%} return, {self.scenarios[scenario]['volatility']:.1%} volatility")
        
        # Use multiprocessing for faster execution
        num_cores = min(multiprocessing.cpu_count(), 8)  # Use max 8 cores
        
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            futures = [
                executor.submit(self.run_single_simulation, i, scenario) 
                for i in range(self.num_simulations)
            ]
            
            results = []
            for i, future in enumerate(futures):
                if (i + 1) % 100 == 0:
                    print(f"Completed {i + 1:,} simulations...")
                results.append(future.result())
        
        print(f"✅ Completed all {self.num_simulations:,} simulations!")
        return results
    
    def analyze_results(self, results: List[SimulationResult], scenario_name: str) -> Dict:
        """Analyze Monte Carlo results and generate statistics."""
        # Convert to arrays for analysis
        net_worths = [r.final_net_worth for r in results]
        roth_balances = [r.final_roth_balance for r in results]
        conversions = [r.total_conversions for r in results]
        taxes = [r.total_taxes for r in results]
        roth_preserved_count = sum(1 for r in results if r.roth_preserved)
        shortfall_years = [r.years_with_shortfall for r in results]
        
        # Calculate percentiles
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        net_worth_percentiles = np.percentile(net_worths, percentiles)
        roth_percentiles = np.percentile(roth_balances, percentiles)
        
        analysis = {
            'scenario': scenario_name,
            'total_simulations': len(results),
            'roth_preservation_rate': roth_preserved_count / len(results),
            'avg_final_net_worth': np.mean(net_worths),
            'median_final_net_worth': np.median(net_worths),
            'std_final_net_worth': np.std(net_worths),
            'avg_final_roth': np.mean(roth_balances),
            'median_final_roth': np.median(roth_balances),
            'avg_conversions': np.mean(conversions),
            'avg_taxes': np.mean(taxes),
            'prob_roth_above_1m': sum(1 for r in roth_balances if r >= 1_000_000) / len(results),
            'prob_roth_above_2m': sum(1 for r in roth_balances if r >= 2_000_000) / len(results),
            'prob_net_worth_above_5m': sum(1 for nw in net_worths if nw >= 5_000_000) / len(results),
            'avg_shortfall_years': np.mean(shortfall_years),
            'worst_case_net_worth': min(net_worths),
            'best_case_net_worth': max(net_worths),
            'net_worth_percentiles': dict(zip(percentiles, net_worth_percentiles)),
            'roth_percentiles': dict(zip(percentiles, roth_percentiles))
        }
        
        return analysis
    
    def create_comprehensive_visualization(self, all_results: Dict[str, List[SimulationResult]]):
        """Create comprehensive visualization of all scenarios."""
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle('Monte Carlo Analysis: Roth Conversion Strategy Under Market Volatility', fontsize=16)
        
        scenarios = list(all_results.keys())
        colors = ['blue', 'green', 'orange', 'red', 'purple']
        
        # Plot 1: Net Worth Distributions
        ax1 = plt.subplot(3, 3, 1)
        for i, (scenario, results) in enumerate(all_results.items()):
            net_worths = [r.final_net_worth / 1e6 for r in results]  # Convert to millions
            ax1.hist(net_worths, bins=50, alpha=0.6, label=scenario, color=colors[i % len(colors)])
        ax1.set_title('Final Net Worth Distribution')
        ax1.set_xlabel('Net Worth ($M)')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Roth Balance Distributions
        ax2 = plt.subplot(3, 3, 2)
        for i, (scenario, results) in enumerate(all_results.items()):
            roth_balances = [r.final_roth_balance / 1e6 for r in results]
            ax2.hist(roth_balances, bins=50, alpha=0.6, label=scenario, color=colors[i % len(colors)])
        ax2.set_title('Final Roth Balance Distribution')
        ax2.set_xlabel('Roth Balance ($M)')
        ax2.set_ylabel('Frequency')
        ax2.axvline(x=1.0, color='red', linestyle='--', label='$1M Target')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Roth Preservation Rates
        ax3 = plt.subplot(3, 3, 3)
        preservation_rates = []
        for scenario, results in all_results.items():
            rate = sum(1 for r in results if r.roth_preserved) / len(results)
            preservation_rates.append(rate)
        ax3.bar(scenarios, preservation_rates, color=colors[:len(scenarios)])
        ax3.set_title('Roth Preservation Success Rate')
        ax3.set_ylabel('Success Rate')
        ax3.set_ylim(0, 1)
        for i, rate in enumerate(preservation_rates):
            ax3.text(i, rate + 0.01, f'{rate:.1%}', ha='center')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Box plot of Net Worth by Scenario
        ax4 = plt.subplot(3, 3, 4)
        net_worth_data = []
        for scenario, results in all_results.items():
            net_worth_data.append([r.final_net_worth / 1e6 for r in results])
        ax4.boxplot(net_worth_data, labels=scenarios)
        ax4.set_title('Net Worth Distribution by Scenario')
        ax4.set_ylabel('Net Worth ($M)')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Shortfall Analysis
        ax5 = plt.subplot(3, 3, 5)
        avg_shortfalls = []
        for scenario, results in all_results.items():
            avg_shortfall = np.mean([r.years_with_shortfall for r in results])
            avg_shortfalls.append(avg_shortfall)
        ax5.bar(scenarios, avg_shortfalls, color=colors[:len(scenarios)])
        ax5.set_title('Average Years with Asset Shortfall')
        ax5.set_ylabel('Years')
        ax5.grid(True, alpha=0.3)
        
        # Plot 6: Probability of Achieving Targets
        ax6 = plt.subplot(3, 3, 6)
        targets = ['Roth > $1M', 'Roth > $2M', 'Net Worth > $5M']
        target_probs = {scenario: [] for scenario in scenarios}
        
        for scenario, results in all_results.items():
            target_probs[scenario].append(sum(1 for r in results if r.final_roth_balance >= 1_000_000) / len(results))
            target_probs[scenario].append(sum(1 for r in results if r.final_roth_balance >= 2_000_000) / len(results))
            target_probs[scenario].append(sum(1 for r in results if r.final_net_worth >= 5_000_000) / len(results))
        
        x = np.arange(len(targets))
        width = 0.15
        for i, scenario in enumerate(scenarios):
            ax6.bar(x + i*width, target_probs[scenario], width, label=scenario, color=colors[i % len(colors)])
        
        ax6.set_title('Probability of Achieving Targets')
        ax6.set_ylabel('Probability')
        ax6.set_xticks(x + width * 2)
        ax6.set_xticklabels(targets)
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # Plot 7: Sequence of Returns Risk
        ax7 = plt.subplot(3, 3, 7)
        for i, (scenario, results) in enumerate(all_results.items()):
            sequence_risks = [r.sequence_of_returns_risk for r in results]
            final_roths = [r.final_roth_balance / 1e6 for r in results]
            ax7.scatter(sequence_risks, final_roths, alpha=0.5, label=scenario, color=colors[i % len(colors)])
        ax7.set_title('Sequence of Returns Risk vs Final Roth')
        ax7.set_xlabel('Early Years Return Deviation')
        ax7.set_ylabel('Final Roth Balance ($M)')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # Plot 8: Conversion Success Analysis
        ax8 = plt.subplot(3, 3, 8)
        for i, (scenario, results) in enumerate(all_results.items()):
            conversions = [r.total_conversions / 1e6 for r in results]
            ax8.hist(conversions, bins=30, alpha=0.6, label=scenario, color=colors[i % len(colors)])
        ax8.set_title('Total Conversions Distribution')
        ax8.set_xlabel('Total Conversions ($M)')
        ax8.set_ylabel('Frequency')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # Plot 9: Summary Statistics Table
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('tight')
        ax9.axis('off')
        
        # Create summary table
        summary_data = []
        for scenario, results in all_results.items():
            net_worths = [r.final_net_worth for r in results]
            roth_balances = [r.final_roth_balance for r in results]
            preserved = sum(1 for r in results if r.roth_preserved)
            
            summary_data.append([
                scenario,
                f"${np.mean(net_worths)/1e6:.1f}M",
                f"${np.mean(roth_balances)/1e6:.1f}M",
                f"{preserved/len(results):.1%}"
            ])
        
        table = ax9.table(cellText=summary_data,
                         colLabels=['Scenario', 'Avg Net Worth', 'Avg Roth', 'Preservation %'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        ax9.set_title('Summary Statistics')
        
        plt.tight_layout()
        
        # Save plot
        Path("output").mkdir(exist_ok=True)
        plt.savefig("output/monte_carlo_comprehensive_analysis.png", dpi=300, bbox_inches='tight')
        print(f"\nComprehensive visualization saved to: output/monte_carlo_comprehensive_analysis.png")
        
        plt.show()
    
    def print_detailed_analysis(self, analysis: Dict):
        """Print detailed analysis results."""
        print(f"\n📊 DETAILED ANALYSIS: {analysis['scenario'].upper()} SCENARIO")
        print("=" * 70)
        print(f"Total Simulations: {analysis['total_simulations']:,}")
        print(f"Roth Preservation Success Rate: {analysis['roth_preservation_rate']:.1%}")
        print(f"\n💰 NET WORTH ANALYSIS:")
        print(f"Average Final Net Worth: ${analysis['avg_final_net_worth']:,.0f}")
        print(f"Median Final Net Worth: ${analysis['median_final_net_worth']:,.0f}")
        print(f"Standard Deviation: ${analysis['std_final_net_worth']:,.0f}")
        print(f"Worst Case: ${analysis['worst_case_net_worth']:,.0f}")
        print(f"Best Case: ${analysis['best_case_net_worth']:,.0f}")
        
        print(f"\n🎯 ROTH ANALYSIS:")
        print(f"Average Final Roth: ${analysis['avg_final_roth']:,.0f}")
        print(f"Median Final Roth: ${analysis['median_final_roth']:,.0f}")
        print(f"Probability Roth > $1M: {analysis['prob_roth_above_1m']:.1%}")
        print(f"Probability Roth > $2M: {analysis['prob_roth_above_2m']:.1%}")
        
        print(f"\n📈 PERCENTILE ANALYSIS (Net Worth):")
        for pct, value in analysis['net_worth_percentiles'].items():
            print(f"{pct}th percentile: ${value:,.0f}")
        
        print(f"\n⚠️ RISK ANALYSIS:")
        print(f"Average Years with Shortfall: {analysis['avg_shortfall_years']:.1f}")
        print(f"Probability Net Worth > $5M: {analysis['prob_net_worth_above_5m']:.1%}")
    
    def save_detailed_results(self, all_results: Dict[str, List[SimulationResult]], analyses: Dict[str, Dict]):
        """Save detailed results to CSV files."""
        Path("output").mkdir(exist_ok=True)
        
        # Save summary analysis
        summary_data = []
        for scenario, analysis in analyses.items():
            summary_data.append({
                'Scenario': scenario,
                'Simulations': analysis['total_simulations'],
                'Roth_Preservation_Rate': analysis['roth_preservation_rate'],
                'Avg_Final_Net_Worth': analysis['avg_final_net_worth'],
                'Median_Final_Net_Worth': analysis['median_final_net_worth'],
                'Std_Final_Net_Worth': analysis['std_final_net_worth'],
                'Avg_Final_Roth': analysis['avg_final_roth'],
                'Median_Final_Roth': analysis['median_final_roth'],
                'Prob_Roth_Above_1M': analysis['prob_roth_above_1m'],
                'Prob_Roth_Above_2M': analysis['prob_roth_above_2m'],
                'Prob_Net_Worth_Above_5M': analysis['prob_net_worth_above_5m'],
                'Avg_Shortfall_Years': analysis['avg_shortfall_years'],
                'Worst_Case_Net_Worth': analysis['worst_case_net_worth'],
                'Best_Case_Net_Worth': analysis['best_case_net_worth']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv("output/monte_carlo_summary.csv", index=False)
        print(f"Summary analysis saved to: output/monte_carlo_summary.csv")
        
        # Save detailed results for each scenario
        for scenario, results in all_results.items():
            detailed_data = []
            for result in results:
                detailed_data.append({
                    'Simulation_ID': result.simulation_id,
                    'Final_Net_Worth': result.final_net_worth,
                    'Final_Roth_Balance': result.final_roth_balance,
                    'Total_Conversions': result.total_conversions,
                    'Total_Taxes': result.total_taxes,
                    'Roth_Preserved': result.roth_preserved,
                    'Years_With_Shortfall': result.years_with_shortfall,
                    'Worst_Year_Return': result.worst_year_return,
                    'Best_Year_Return': result.best_year_return,
                    'Sequence_Risk': result.sequence_of_returns_risk
                })
            
            detailed_df = pd.DataFrame(detailed_data)
            filename = f"output/monte_carlo_detailed_{scenario}.csv"
            detailed_df.to_csv(filename, index=False)
            print(f"Detailed {scenario} results saved to: {filename}")


def main():
    """Run comprehensive Monte Carlo analysis."""
    # Initialize analyzer
    analyzer = MonteCarloRothAnalyzer(num_simulations=1000)  # Use 1000 for speed, increase for more precision
    
    # Run simulations for different scenarios
    all_results = {}
    all_analyses = {}
    
    scenarios_to_test = ['base_case', 'low_return', 'high_volatility', 'stagflation']
    
    for scenario in scenarios_to_test:
        print(f"\n{'='*60}")
        results = analyzer.run_monte_carlo_analysis(scenario)
        analysis = analyzer.analyze_results(results, scenario)
        
        all_results[scenario] = results
        all_analyses[scenario] = analysis
        
        analyzer.print_detailed_analysis(analysis)
    
    # Create comprehensive visualization
    analyzer.create_comprehensive_visualization(all_results)
    
    # Save all results
    analyzer.save_detailed_results(all_results, all_analyses)
    
    print(f"\n🎉 Monte Carlo Analysis Complete!")
    print(f"Results saved to output/ directory")
    
    return analyzer, all_results, all_analyses


if __name__ == "__main__":
    analyzer, results, analyses = main()