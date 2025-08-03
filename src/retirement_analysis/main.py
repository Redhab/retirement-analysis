#!/usr/bin/env python3
"""
Clean Roth Conversion Strategy Analysis
Single retiree starting at age 62 in 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


class RothConversionAnalyzer:
    """Analyzes Roth conversion strategy for single retiree."""
    
    def __init__(self):
        # Retirement timeline
        self.start_year = 2026
        self.start_age = 62
        self.end_age = 85
        self.ss_start_age = 67
        self.rmd_age = 73
        
        # Starting account balances (2026)
        self.initial_ira = 1_250_000
        self.initial_roth = 250_000
        self.initial_brokerage = 1_200_000
        self.initial_savings = 300_000
        self.home_equity = 900_000  # Not used for expenses
        
        # Annual expenses (2026 dollars)
        self.base_expenses = 60_000
        self.travel_expenses = 20_000  # Ages 62-70
        self.car_purchase = 20_000     # Age 63 (2027)
        self.home_renovation = 80_000  # Age 64 (2028)
        
        # Social Security
        self.ss_annual_benefit = 36_000
        
        # Economic assumptions
        self.inflation_rate = 0.04
        self.market_return = 0.03
        
        # Tax brackets (2025 single filer, assuming similar for 2026+)
        self.standard_deduction = 15_000  # Estimated for 2025+
        self.tax_brackets = {
            'bracket_12_max': 48_475,
            'bracket_22_max': 103_350,
            'bracket_24_max': 197_300
        }
        
        # Tax rates
        self.tax_rate_ira = 0.22        # Assume 22% for IRA withdrawals
        self.tax_rate_conversion = 0.22  # Target 22% bracket for conversions
        self.tax_rate_brokerage = 0.15   # Long-term capital gains
        self.tax_rate_roth = 0.00        # Tax-free
    
    def calculate_expenses(self, age, year):
        """Calculate total expenses for a given age/year with inflation."""
        years_since_start = year - self.start_year
        inflation_factor = (1 + self.inflation_rate) ** years_since_start
        
        # Base expenses with inflation
        total_expenses = self.base_expenses * inflation_factor
        
        # Travel expenses (ages 62-70)
        if 62 <= age <= 70:
            total_expenses += self.travel_expenses * inflation_factor
        
        # One-time expenses
        if age == 63:  # Car purchase in 2027
            total_expenses += self.car_purchase * inflation_factor
        elif age == 64:  # Home renovation in 2028
            total_expenses += self.home_renovation * inflation_factor
        
        return total_expenses
    
    def get_social_security(self, age):
        """Get Social Security benefit for given age."""
        if age >= self.ss_start_age:
            return self.ss_annual_benefit
        return 0
    
    def calculate_conversion_capacity(self, current_income):
        """Calculate how much can be converted to stay in 22% bracket."""
        # Available space in 22% bracket
        taxable_capacity = self.tax_brackets['bracket_22_max'] - self.standard_deduction
        available_space = max(0, taxable_capacity - current_income)
        return available_space
    
    def run_conversion_strategy(self):
        """Execute the Roth conversion strategy."""
        
        # Initialize account balances
        ira_balance = self.initial_ira
        roth_balance = self.initial_roth
        brokerage_balance = self.initial_brokerage
        savings_balance = self.initial_savings
        
        # Results tracking
        results = []
        
        print("🎯 ROTH CONVERSION STRATEGY ANALYSIS")
        print("=" * 60)
        print(f"Retirement: 2026-{self.start_year + (self.end_age - self.start_age)} (ages {self.start_age}-{self.end_age})")
        print(f"Social Security: ${self.ss_annual_benefit:,}/year starting at age {self.ss_start_age}")
        print(f"Target: Maximize Roth balance while preserving it for inheritance")
        print("=" * 60)
        
        for year_offset in range(self.end_age - self.start_age + 1):
            year = self.start_year + year_offset
            age = self.start_age + year_offset
            
            print(f"\n--- Year {year} (Age {age}) ---")
            
            # Apply market growth at start of year
            ira_balance *= (1 + self.market_return)
            roth_balance *= (1 + self.market_return)
            brokerage_balance *= (1 + self.market_return)
            savings_balance *= (1 + self.market_return)
            
            print(f"After growth: IRA=${ira_balance:,.0f}, Roth=${roth_balance:,.0f}")
            print(f"              Savings=${savings_balance:,.0f}, Brokerage=${brokerage_balance:,.0f}")
            
            # Calculate expenses and income
            total_expenses = self.calculate_expenses(age, year)
            ss_income = self.get_social_security(age)
            net_expenses = max(0, total_expenses - ss_income)
            
            print(f"Expenses: ${total_expenses:,.0f}, SS: ${ss_income:,.0f}, Net need: ${net_expenses:,.0f}")
            
            # Initialize yearly tracking
            year_data = {
                'Year': year,
                'Age': age,
                'IRA_Start': ira_balance,
                'Roth_Start': roth_balance,
                'Expenses': total_expenses,
                'Social_Security': ss_income,
                'Net_Expenses': net_expenses,
                'Conversion_Amount': 0,
                'Conversion_Tax': 0,
                'IRA_Withdrawal': 0,
                'Brokerage_Withdrawal': 0,
                'Savings_Withdrawal': 0,
                'Roth_Withdrawal': 0,  # Should always be 0!
                'Total_Taxes': 0
            }
            
            # ROTH CONVERSION LOGIC (ages 62-73)
            conversion_amount = 0
            conversion_tax = 0
            
            if 62 <= age <= 73 and ira_balance > 0:
                print(f"\n🔄 Evaluating Roth conversion at age {age}")
                
                # Estimate current taxable income (before conversion)
                estimated_ira_withdrawal = 0
                estimated_brokerage_withdrawal = 0
                
                # Estimate what we'll need to withdraw for expenses
                remaining_expense_need = net_expenses
                
                # Will use savings first (tax-free), then brokerage, then IRA
                if savings_balance < remaining_expense_need:
                    shortage = remaining_expense_need - savings_balance
                    brokerage_gross_needed = shortage / (1 - self.tax_rate_brokerage)
                    
                    if brokerage_balance < brokerage_gross_needed:
                        estimated_brokerage_withdrawal = brokerage_balance
                        remaining_after_brokerage = shortage - (brokerage_balance * (1 - self.tax_rate_brokerage))
                        estimated_ira_withdrawal = remaining_after_brokerage / (1 - self.tax_rate_ira)
                    else:
                        estimated_brokerage_withdrawal = brokerage_gross_needed
                
                # Current taxable income from expected withdrawals
                current_taxable_income = estimated_ira_withdrawal + (estimated_brokerage_withdrawal * 0.5)
                
                # Calculate conversion capacity
                conversion_capacity = self.calculate_conversion_capacity(current_taxable_income)
                
                # Determine conversion target based on age
                if 62 <= age <= 66:  # Pre-SS aggressive phase
                    target_conversion = min(conversion_capacity, 80_000)
                elif age == 67:  # SS starts, moderate
                    target_conversion = min(conversion_capacity, 60_000)
                elif 68 <= age <= 72:  # Post-SS moderate phase
                    target_conversion = min(conversion_capacity, 50_000)
                else:  # Age 73+ (RMD phase)
                    target_conversion = min(conversion_capacity, 30_000)
                
                # Limit by available IRA balance
                target_conversion = min(target_conversion, ira_balance)
                
                # Check if we can afford the conversion tax
                if target_conversion > 0:
                    conversion_tax_needed = target_conversion * self.tax_rate_conversion
                    available_for_tax = savings_balance + brokerage_balance * 0.5  # Conservative
                    
                    print(f"Target conversion: ${target_conversion:,.0f}")
                    print(f"Tax needed: ${conversion_tax_needed:,.0f}")
                    print(f"Available for tax: ${available_for_tax:,.0f}")
                    
                    if available_for_tax >= conversion_tax_needed and target_conversion >= 10_000:
                        conversion_amount = target_conversion
                        conversion_tax = conversion_tax_needed
                        
                        # Execute conversion
                        ira_balance -= conversion_amount
                        roth_balance += conversion_amount
                        
                        print(f"✅ CONVERTED: ${conversion_amount:,.0f} (tax: ${conversion_tax:,.0f})")
                        
                        # Pay conversion tax from liquid assets
                        if savings_balance >= conversion_tax:
                            savings_balance -= conversion_tax
                        else:
                            remaining_tax = conversion_tax - savings_balance
                            savings_balance = 0
                            brokerage_balance -= remaining_tax
                    else:
                        print("❌ Conversion skipped - insufficient funds for tax")
                else:
                    print("No conversion capacity or IRA funds available")
            
            year_data['Conversion_Amount'] = conversion_amount
            year_data['Conversion_Tax'] = conversion_tax
            
            # WITHDRAWAL LOGIC FOR LIVING EXPENSES - NEVER TOUCH ROTH!
            print(f"\n💰 Covering expenses: ${net_expenses:,.0f}")
            
            remaining_need = net_expenses
            total_withdrawal_taxes = 0
            
            # 1. Use Savings first (tax-free)
            if remaining_need > 0 and savings_balance > 0:
                savings_used = min(remaining_need, savings_balance)
                savings_balance -= savings_used
                remaining_need -= savings_used
                year_data['Savings_Withdrawal'] = savings_used
                print(f"Used savings: ${savings_used:,.0f}, remaining need: ${remaining_need:,.0f}")
            
            # 2. Use Brokerage (taxable)
            if remaining_need > 0 and brokerage_balance > 0:
                gross_needed = remaining_need / (1 - self.tax_rate_brokerage)
                brokerage_used = min(gross_needed, brokerage_balance)
                net_received = brokerage_used * (1 - self.tax_rate_brokerage)
                withdrawal_tax = brokerage_used * self.tax_rate_brokerage
                
                brokerage_balance -= brokerage_used
                remaining_need -= net_received
                total_withdrawal_taxes += withdrawal_tax
                year_data['Brokerage_Withdrawal'] = brokerage_used
                print(f"Used brokerage: ${brokerage_used:,.0f} (net: ${net_received:,.0f}), remaining need: ${remaining_need:,.0f}")
            
            # 3. Use IRA (taxable)
            if remaining_need > 0 and ira_balance > 0:
                gross_needed = remaining_need / (1 - self.tax_rate_ira)
                ira_used = min(gross_needed, ira_balance)
                net_received = ira_used * (1 - self.tax_rate_ira)
                withdrawal_tax = ira_used * self.tax_rate_ira
                
                ira_balance -= ira_used
                remaining_need -= net_received
                total_withdrawal_taxes += withdrawal_tax
                year_data['IRA_Withdrawal'] = ira_used
                print(f"Used IRA: ${ira_used:,.0f} (net: ${net_received:,.0f}), remaining need: ${remaining_need:,.0f}")
            
            # 4. NEVER USE ROTH (preserve for inheritance)
            if remaining_need > 0:
                print(f"🚨 SHORTFALL: ${remaining_need:,.0f} - REFUSING to use Roth!")
                # year_data['Roth_Withdrawal'] remains 0
            
            year_data['Total_Taxes'] = conversion_tax + total_withdrawal_taxes
            year_data['IRA_End'] = ira_balance
            year_data['Roth_End'] = roth_balance
            year_data['Savings_End'] = savings_balance
            year_data['Brokerage_End'] = brokerage_balance
            
            print(f"End balances: IRA=${ira_balance:,.0f}, Roth=${roth_balance:,.0f}")
            print(f"              Savings=${savings_balance:,.0f}, Brokerage=${brokerage_balance:,.0f}")
            
            results.append(year_data)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Summary statistics
        total_conversions = df['Conversion_Amount'].sum()
        total_taxes = df['Total_Taxes'].sum()
        final_ira = df['IRA_End'].iloc[-1]
        final_roth = df['Roth_End'].iloc[-1]
        final_savings = df['Savings_End'].iloc[-1]
        final_brokerage = df['Brokerage_End'].iloc[-1]
        final_liquid_assets = final_ira + final_roth + final_savings + final_brokerage
        
        # Calculate final home equity with appreciation
        years_of_appreciation = self.end_age - self.start_age
        final_home_equity = self.home_equity * ((1 + self.inflation_rate) ** years_of_appreciation)
        final_net_worth = final_liquid_assets + final_home_equity
        
        total_roth_withdrawals = df['Roth_Withdrawal'].sum()
        initial_liquid_assets = self.initial_ira + self.initial_roth + self.initial_brokerage + self.initial_savings
        
        print(f"\n🎯 STRATEGY RESULTS")
        print("=" * 50)
        print(f"Total Roth conversions: ${total_conversions:,.0f}")
        print(f"Total taxes paid: ${total_taxes:,.0f}")
        print(f"Total Roth withdrawals: ${total_roth_withdrawals:,.0f}")
        print(f"Roth preserved for inheritance: {'YES' if total_roth_withdrawals == 0 else 'NO'}")
        print("\n📊 FINAL ACCOUNT BALANCES AT AGE 85:")
        print(f"IRA Balance: ${final_ira:,.0f}")
        print(f"Roth Balance: ${final_roth:,.0f}")
        print(f"Savings Balance: ${final_savings:,.0f}")
        print(f"Brokerage Balance: ${final_brokerage:,.0f}")
        print(f"Home Equity (with appreciation): ${final_home_equity:,.0f}")
        print(f"-" * 30)
        print(f"Total Liquid Assets: ${final_liquid_assets:,.0f}")
        print(f"NET WORTH AT 85: ${final_net_worth:,.0f}")
        print(f"\n💰 WEALTH ANALYSIS:")
        print(f"Initial liquid assets: ${initial_liquid_assets:,.0f}")
        print(f"Asset growth despite distributions: ${final_liquid_assets - initial_liquid_assets:,.0f}")
        print(f"Tax-free inheritance (Roth): ${final_roth:,.0f}")
        
        return df
    
    def create_visualizations(self, df):
        """Create visualizations for the strategy results."""
        # Create a larger figure with 6 subplots
        fig = plt.figure(figsize=(18, 14))
        fig.suptitle('Comprehensive Roth Conversion Strategy Analysis', fontsize=16)
        
        # Calculate home equity appreciation over time
        home_equity_over_time = []
        for i, age in enumerate(df['Age']):
            years_elapsed = age - self.start_age
            home_value = self.home_equity * ((1 + self.inflation_rate) ** years_elapsed)
            home_equity_over_time.append(home_value)
        
        df_with_home = df.copy()
        df_with_home['Home_Equity'] = home_equity_over_time
        df_with_home['Net_Worth'] = df['IRA_End'] + df['Roth_End'] + df['Savings_End'] + df['Brokerage_End'] + df_with_home['Home_Equity']
        
        # Plot 1: All Account Balances Over Time (2x3 grid, position 1)
        ax1 = plt.subplot(2, 3, 1)
        ax1.plot(df['Age'], df['IRA_End'], label='IRA', linewidth=2, marker='o')
        ax1.plot(df['Age'], df['Roth_End'], label='Roth', linewidth=2, marker='s')
        ax1.plot(df['Age'], df['Savings_End'], label='Savings', linewidth=2, marker='^')
        ax1.plot(df['Age'], df['Brokerage_End'], label='Brokerage', linewidth=2, marker='d')
        ax1.set_title('All Account Balances Over Time')
        ax1.set_xlabel('Age')
        ax1.set_ylabel('Balance ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        # Plot 2: Net Worth Components (position 2)
        ax2 = plt.subplot(2, 3, 2)
        liquid_assets = df['IRA_End'] + df['Roth_End'] + df['Savings_End'] + df['Brokerage_End']
        ax2.plot(df['Age'], liquid_assets, label='Total Liquid Assets', linewidth=3, color='navy')
        ax2.plot(df['Age'], df_with_home['Home_Equity'], label='Home Equity', linewidth=2, color='brown')
        ax2.plot(df['Age'], df_with_home['Net_Worth'], label='Total Net Worth', linewidth=3, color='green', linestyle='--')
        ax2.set_title('Net Worth Components')
        ax2.set_xlabel('Age')
        ax2.set_ylabel('Value ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        # Plot 3: Annual Roth Conversions (position 3)
        ax3 = plt.subplot(2, 3, 3)
        conversion_data = df[df['Conversion_Amount'] > 0]
        if len(conversion_data) > 0:
            ax3.bar(conversion_data['Age'], conversion_data['Conversion_Amount'], alpha=0.7, color='green')
            ax3.set_title('Annual Roth Conversions')
            ax3.set_xlabel('Age')
            ax3.set_ylabel('Conversion Amount ($)')
            ax3.grid(True, alpha=0.3)
            ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
        else:
            ax3.text(0.5, 0.5, 'No Conversions', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Annual Roth Conversions')
        
        # Plot 4: Annual Cash Flow (position 4)
        ax4 = plt.subplot(2, 3, 4)
        ax4.bar(df['Age'], df['Expenses'], alpha=0.7, label='Total Expenses', color='red')
        ax4.bar(df['Age'], df['Social_Security'], alpha=0.7, label='Social Security', color='blue')
        ax4.set_title('Annual Expenses vs Social Security')
        ax4.set_xlabel('Age')
        ax4.set_ylabel('Amount ($)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
        
        # Plot 5: Withdrawal Sources Stacked Bar (position 5)
        ax5 = plt.subplot(2, 3, 5)
        bottom = np.zeros(len(df))
        
        # Stack withdrawals
        withdrawal_sources = [
            ('Savings', df['Savings_Withdrawal'], 'lightblue'),
            ('Brokerage', df['Brokerage_Withdrawal'], 'lightgreen'), 
            ('IRA', df['IRA_Withdrawal'], 'orange'),
            ('Roth', df['Roth_Withdrawal'], 'red')  # Should be zero
        ]
        
        for name, amounts, color in withdrawal_sources:
            ax5.bar(df['Age'], amounts, bottom=bottom, label=name, alpha=0.8, color=color)
            bottom += amounts
        
        ax5.set_title('Annual Withdrawal Sources')
        ax5.set_xlabel('Age')
        ax5.set_ylabel('Withdrawal Amount ($)')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
        
        # Plot 6: Cumulative Analysis (position 6)
        ax6 = plt.subplot(2, 3, 6)
        cumulative_conversions = df['Conversion_Amount'].cumsum()
        cumulative_taxes = df['Total_Taxes'].cumsum()
        ax6.plot(df['Age'], cumulative_conversions, label='Cumulative Conversions', linewidth=3, color='green')
        ax6.plot(df['Age'], cumulative_taxes, label='Cumulative Taxes', linewidth=3, color='red')
        ax6.set_title('Cumulative Conversions and Taxes')
        ax6.set_xlabel('Age')
        ax6.set_ylabel('Amount ($)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        ax6.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
        
        plt.tight_layout()
        
        # Save plot
        Path("output").mkdir(exist_ok=True)
        plt.savefig("output/roth_conversion_analysis.png", dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to: output/roth_conversion_analysis.png")
        
        plt.show()
        
        # Create a summary table for final balances - inline to avoid method issues
        print(f"\n📈 NET WORTH PROGRESSION SUMMARY")
        print("=" * 70)
        
        # Show key milestone ages
        milestone_ages = [62, 67, 72, 77, 82, 85]
        
        # Simple manual table creation
        print(f"{'Age':<4} {'Year':<6} {'IRA':<12} {'Roth':<12} {'Savings':<12} {'Brokerage':<12} {'Home_Equity':<15} {'Net_Worth':<15}")
        print("-" * 90)
        
        for age in milestone_ages:
            if age <= self.end_age:
                # Find the row for this age using simple iteration
                for index in range(len(df_with_home)):
                    row = df_with_home.iloc[index]
                    if row['Age'] == age:
                        ira_val = f"${row['IRA_End']:,.0f}"
                        roth_val = f"${row['Roth_End']:,.0f}"
                        savings_val = f"${row['Savings_End']:,.0f}"
                        brokerage_val = f"${row['Brokerage_End']:,.0f}"
                        home_val = f"${row['Home_Equity']:,.0f}"
                        net_worth_val = f"${row['Net_Worth']:,.0f}"
                        year_val = int(row['Year'])
                        
                        print(f"{age:<4} {year_val:<6} {ira_val:<12} {roth_val:<12} {savings_val:<12} {brokerage_val:<12} {home_val:<15} {net_worth_val:<15}")
                        break
        
        # Calculate final net worth breakdown using simple indexing
        final_row = df_with_home.iloc[-1]
        print(f"\n💎 LEGACY ANALYSIS AT AGE 85:")
        print(f"Tax-Deferred Assets (IRA): ${final_row['IRA_End']:,.0f}")
        print(f"Tax-Free Assets (Roth): ${final_row['Roth_End']:,.0f}")
        print(f"Taxable Assets (Savings + Brokerage): ${final_row['Savings_End'] + final_row['Brokerage_End']:,.0f}")
        print(f"Real Estate (Home): ${final_row['Home_Equity']:,.0f}")
        print(f"TOTAL NET WORTH: ${final_row['Net_Worth']:,.0f}")
        
        if final_row['Net_Worth'] > 0:
            tax_free_percentage = (final_row['Roth_End'] / final_row['Net_Worth']) * 100
            print(f"\nTax-free inheritance percentage: {tax_free_percentage:.1f}%")
        else:
            print(f"\nTax-free inheritance percentage: 0.0%")
    
    def _create_final_balance_summary(self, df_with_home):
        """Create a summary table showing the progression of net worth."""
        print(f"\n📈 NET WORTH PROGRESSION SUMMARY")
        print("=" * 70)
        
        # Show key milestone ages
        milestone_ages = [62, 67, 72, 77, 82, 85]
        milestone_data = []
        
        for age in milestone_ages:
            if age <= self.end_age:
                matching_rows = df_with_home[df_with_home['Age'] == age]
                if len(matching_rows) > 0:
                    row = matching_rows.iloc[0]
                    milestone_data.append({
                        'Age': age,
                        'Year': int(row['Year']),
                        'IRA': f"${row['IRA_End']:,.0f}",
                        'Roth': f"${row['Roth_End']:,.0f}",
                        'Savings': f"${row['Savings_End']:,.0f}",
                        'Brokerage': f"${row['Brokerage_End']:,.0f}",
                        'Home_Equity': f"${row['Home_Equity']:,.0f}",
                        'Net_Worth': f"${row['Net_Worth']:,.0f}"
                    })
        
        if milestone_data:
            milestone_df = pd.DataFrame(milestone_data)
            # Simple print instead of pandas to_string to avoid recursion issues
            print(f"{'Age':<4} {'Year':<6} {'IRA':<12} {'Roth':<12} {'Savings':<12} {'Brokerage':<12} {'Home_Equity':<15} {'Net_Worth':<15}")
            print("-" * 90)
            for _, row in milestone_df.iterrows():
                print(f"{row['Age']:<4} {row['Year']:<6} {row['IRA']:<12} {row['Roth']:<12} {row['Savings']:<12} {row['Brokerage']:<12} {row['Home_Equity']:<15} {row['Net_Worth']:<15}")
        
        # Calculate final net worth breakdown
        final_row = df_with_home.iloc[-1]
        print(f"\n💎 LEGACY ANALYSIS AT AGE 85:")
        print(f"Tax-Deferred Assets (IRA): ${final_row['IRA_End']:,.0f}")
        print(f"Tax-Free Assets (Roth): ${final_row['Roth_End']:,.0f}")
        print(f"Taxable Assets (Savings + Brokerage): ${final_row['Savings_End'] + final_row['Brokerage_End']:,.0f}")
        print(f"Real Estate (Home): ${final_row['Home_Equity']:,.0f}")
        print(f"TOTAL NET WORTH: ${final_row['Net_Worth']:,.0f}")
        
        tax_free_percentage = (final_row['Roth_End'] / final_row['Net_Worth']) * 100
        print(f"\nTax-free inheritance percentage: {tax_free_percentage:.1f}%")
        
        # Create a summary table for final balances
        self._create_final_balance_summary(df_with_home)
    
    def save_results(self, df):
        """Save detailed results to CSV."""
        Path("output").mkdir(exist_ok=True)
        
        # Add home equity and net worth to the dataframe for export
        home_equity_over_time = []
        for i, age in enumerate(df['Age']):
            years_elapsed = age - self.start_age
            home_value = self.home_equity * ((1 + self.inflation_rate) ** years_elapsed)
            home_equity_over_time.append(home_value)
        
        df_export = df.copy()
        df_export['Home_Equity'] = home_equity_over_time
        df_export['Net_Worth'] = (df['IRA_End'] + df['Roth_End'] + 
                                 df['Savings_End'] + df['Brokerage_End'] + 
                                 df_export['Home_Equity'])
        
        filename = "output/roth_conversion_detailed_results.csv"
        df_export.to_csv(filename, index=False)
        print(f"Detailed results saved to: {filename}")
        
        # Also create a summary CSV with just key metrics
        summary_data = {
            'Metric': [
                'Total Roth Conversions',
                'Total Taxes Paid', 
                'Final IRA Balance',
                'Final Roth Balance',
                'Final Savings Balance',
                'Final Brokerage Balance',
                'Final Home Equity',
                'Final Net Worth',
                'Tax-Free Inheritance (Roth)',
                'Roth Withdrawals (should be 0)'
            ],
            'Value': [
                df['Conversion_Amount'].sum(),
                df['Total_Taxes'].sum(),
                df['IRA_End'].iloc[-1],
                df['Roth_End'].iloc[-1], 
                df['Savings_End'].iloc[-1],
                df['Brokerage_End'].iloc[-1],
                home_equity_over_time[-1],
                df_export['Net_Worth'].iloc[-1],
                df['Roth_End'].iloc[-1],
                df['Roth_Withdrawal'].sum()
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_filename = "output/strategy_summary.csv"
        summary_df.to_csv(summary_filename, index=False)
        print(f"Strategy summary saved to: {summary_filename}")


def main():
    """Run the Roth conversion analysis."""
    analyzer = RothConversionAnalyzer()
    
    # Run the strategy
    results_df = analyzer.run_conversion_strategy()
    
    # Create visualizations
    analyzer.create_visualizations(results_df)
    
    # Save results
    analyzer.save_results(results_df)
    
    return analyzer, results_df


if __name__ == "__main__":
    analyzer, results = main()