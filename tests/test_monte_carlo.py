import pytest
import numpy as np
from retirement_analysis.monte_carlo_simulation import MonteCarloRothAnalyzer, SimulationResult

def test_monte_carlo_analyzer_init():
    """Test Monte Carlo analyzer initialization."""
    analyzer = MonteCarloRothAnalyzer(num_simulations=10)
    assert analyzer.num_simulations == 10
    assert analyzer.start_age == 62
    assert analyzer.end_age == 85

def test_market_returns_generation():
    """Test market returns generation."""
    analyzer = MonteCarloRothAnalyzer(num_simulations=10)
    returns = analyzer.generate_market_returns('base_case')
    
    assert len(returns) == 24  # 85 - 62 + 1 = 24 years
    assert all(isinstance(r, float) for r in returns)

def test_single_simulation():
    """Test single simulation execution."""
    analyzer = MonteCarloRothAnalyzer(num_simulations=10)
    result = analyzer.run_single_simulation(0, 'base_case')
    
    assert isinstance(result, SimulationResult)
    assert result.simulation_id == 0
    assert result.final_net_worth >= 0
    assert result.final_roth_balance >= 0

def test_scenarios_defined():
    """Test that all scenarios are properly defined."""
    analyzer = MonteCarloRothAnalyzer()
    expected_scenarios = ['base_case', 'low_return', 'high_volatility', 'stagflation', 'great_recession']
    
    for scenario in expected_scenarios:
        assert scenario in analyzer.scenarios
        assert 'mean' in analyzer.scenarios[scenario]
        assert 'volatility' in analyzer.scenarios[scenario]