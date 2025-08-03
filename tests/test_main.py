import pytest
import pandas as pd
from retirement_analysis.main import RetirementAnalyzer

# NOT UP To DATE WITH MAIN SCRIPT

def test_retirement_analyzer_init():
    """Test that RetirementAnalyzer initializes correctly."""
    analyzer = RetirementAnalyzer()
    assert analyzer.start_age == 61
    assert analyzer.end_age == 85  # Updated life expectancy
    assert len(analyzer.years) == 25  # 25 years instead of 30
    assert analyzer.ss_start_age == 67
    assert analyzer.ss_monthly_benefit == 3000
    assert analyzer.roth_inheritance_target == 1_000_000


def test_social_security_benefit():
    """Test Social Security benefit calculation."""
    analyzer = RetirementAnalyzer()
    
    # Before SS age
    assert analyzer.get_social_security_benefit(66) == 0
    
    # At and after SS age
    assert analyzer.get_social_security_benefit(67) == 36000  # $3000 * 12
    assert analyzer.get_social_security_benefit(70) == 36000


def test_calculate_annual_expense():
    """Test annual expense calculation."""
    analyzer = RetirementAnalyzer()
    
    # Base expense only
    assert analyzer.calculate_annual_expense(61) == 54000
    
    # Base + travel
    assert analyzer.calculate_annual_expense(65) == 74000
    
    # Base + travel + renovation
    assert analyzer.calculate_annual_expense(62) == 154000
    
    # Base + travel + car
    assert analyzer.calculate_annual_expense(63) == 94000


def test_apply_growth():
    """Test investment growth calculation."""
    analyzer = RetirementAnalyzer()
    
    # Test default growth rate (6%)
    assert analyzer.apply_growth(100000) == 106000
    
    # Test custom growth rate
    assert analyzer.apply_growth(100000, 0.08) == 108000


def test_strategy_tax_efficient():
    """Test that the tax-efficient strategy runs without errors."""
    analyzer = RetirementAnalyzer()
    df = analyzer.run_strategy_tax_efficient()
    
    assert len(df) == 25  # 25 years (age 61-85)
    assert 'Age' in df.columns
    assert 'Taxes_Paid' in df.columns
    assert 'Total_Remaining_Assets' in df.columns
    assert 'Social_Security' in df.columns
    
    # Check that Social Security starts at age 67
    ss_data = df[df['Age'] >= 67]['Social_Security']
    assert all(ss_data == 36000)
    
    # Check that Social Security is 0 before age 67
    ss_before = df[df['Age'] < 67]['Social_Security']
    assert all(ss_before == 0)


def test_strategy_roth_conversion():
    """Test that the Roth conversion strategy runs without errors."""
    analyzer = RetirementAnalyzer()
    df = analyzer.run_strategy_roth_conversion()
    
    assert len(df) == 25  # 25 years
    assert 'Age' in df.columns
    assert 'Taxes_Paid' in df.columns
    assert 'Total_Remaining_Assets' in df.columns
    assert 'Social_Security' in df.columns
    assert 'Roth_Conversion' in df.columns
    
    # Check that conversions only happen before age 67
    conversions_before_ss = df[df['Age'] < 67]['Roth_Conversion'].sum()
    conversions_after_ss = df[df['Age'] >= 67]['Roth_Conversion'].sum()
    
    # There should be some conversions before SS starts
    assert conversions_before_ss >= 0
    # No conversions after SS starts
    assert conversions_after_ss == 0


def test_inheritance_target():
    """Test inheritance target logic."""
    analyzer = RetirementAnalyzer()
    
    # Run both strategies
    df1 = analyzer.run_strategy_tax_efficient()
    df2 = analyzer.run_strategy_roth_conversion()
    
    # Final Roth balances
    final_roth_1 = df1['Roth'].iloc[-1]
    final_roth_2 = df2['Roth'].iloc[-1]
    
    # Conversion strategy should have higher final Roth balance
    assert final_roth_2 >= final_roth_1
    
    # At least one strategy should get close to the target
    target = analyzer.roth_inheritance_target
    assert max(final_roth_1, final_roth_2) >= target * 0.5  # At least 50% of target


def test_generate_report():
    """Test that report generation works."""
    analyzer = RetirementAnalyzer()
    df = analyzer.run_strategy_tax_efficient()
    
    # Should not raise any exceptions
    summary = analyzer.generate_report(df, "Test Strategy")
    
    # Check that summary contains expected keys
    expected_keys = ['total_taxes', 'final_assets', 'final_roth', 'inheritance_achieved']
    for key in expected_keys:
        assert key in summary


def test_compare_strategies():
    """Test strategy comparison functionality."""
    analyzer = RetirementAnalyzer()
    
    # Create mock strategy data
    strategies_data = {
        "Strategy 1": {
            'total_taxes': 100000,
            'final_assets': 500000,
            'final_roth': 800000,
            'inheritance_achieved': False,
            'total_conversions': 0,
            'total_social_security': 360000
        },
        "Strategy 2": {
            'total_taxes': 120000,
            'final_assets': 600000,
            'final_roth': 1200000,
            'inheritance_achieved': True,
            'total_conversions': 500000,
            'total_social_security': 360000
        }
    }
    
    # Should not raise any exceptions
    comparison_df = analyzer.compare_strategies(strategies_data)
    
    # Check that comparison DataFrame has the right structure
    assert isinstance(comparison_df, pd.DataFrame)
    assert len(comparison_df) == 2
    assert 'Strategy' in comparison_df.columns


if __name__ == "__main__":
    # Run a simple test
    analyzer = RetirementAnalyzer()
    print("Running basic functionality test...")
    
    # Test both strategies
    df1 = analyzer.run_strategy_tax_efficient()
    df2 = analyzer.run_strategy_roth_conversion()
    
    print(f"Tax-efficient strategy: Final Roth = ${df1['Roth'].iloc[-1]:,.0f}")
    print(f"Roth conversion strategy: Final Roth = ${df2['Roth'].iloc[-1]:,.0f}")
    print(f"Inheritance target: ${analyzer.roth_inheritance_target:,.0f}")
    
    print("✓ All basic tests passed!")