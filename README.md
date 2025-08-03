# Enhanced Retirement Analysis Tool

A comprehensive Python tool for analyzing retirement withdrawal strategies with a focus on Roth conversion optimization, tax efficiency, and inheritance planning for single retirees.

## Features

- **Roth Conversion Strategy**: Intelligent age-based conversions to maximize tax-free inheritance
- **Tax Bracket Management**: Stays within optimal tax brackets (22% for single filers)
- **Social Security Integration**: $36,000/year benefits starting at age 67
- **Inheritance Planning**: Preserves Roth accounts for tax-free legacy
- **Inflation Modeling**: 3% annual inflation on all expenses
- **Market Growth**: 6% annual returns on all investment accounts
- **Comprehensive Reporting**: Year-by-year analysis with detailed tracking
- **Professional Visualizations**: Multi-panel charts showing strategy performance
- **Export Capabilities**: Save results to CSV and charts to PNG

## Strategy Overview

This tool implements an aggressive Roth conversion strategy for a single retiree starting retirement at age 62 in 2026. The strategy prioritizes building a substantial tax-free inheritance while efficiently managing current tax obligations.

### Conversion Timeline
- **Ages 62-66**: Aggressive phase ($80K annual target)
- **Age 67**: Moderate phase when Social Security starts ($60K target)
- **Ages 68-72**: Post-Social Security phase ($50K target)  
- **Ages 73+**: RMD phase with minimal conversions ($30K target)

### Withdrawal Hierarchy (NEVER touches Roth)
1. **Savings** (tax-free)
2. **Brokerage** (15% capital gains tax)
3. **IRA** (22% ordinary income tax)
4. **Roth** - NEVER USED (preserved for inheritance)

## Assumptions and Requirements

### Retiree Profile
- **Filing Status**: Single
- **Retirement Start**: 2026 at age 62
- **Life Expectancy**: 85 years (24-year retirement period)
- **Social Security**: Starts at age 67 (Full Retirement Age)

### Starting Account Balances (2026)
- **Traditional IRA**: $1,250,000
- **Roth IRA**: $250,000
- **Brokerage Account**: $1,200,000
- **Savings**: $300,000
- **Home Equity**: $900,000 (not used for living expenses)
- **Total Liquid Assets**: $3,000,000

### Annual Living Expenses (2026 Base Year)
- **Base Expenses**: $60,000/year
- **Travel Budget**: $20,000/year (ages 62-70, 2026-2034)
- **One-Time Expenses**:
  - Car Purchase: $20,000 at age 63 (2027)
  - Home Renovation: $80,000 at age 64 (2028)

### Tax Brackets (2025 Single Filer)
Based on estimated 2025 tax brackets for single filers:
- **12% Bracket**: $11,926 to $48,475
- **22% Bracket**: $48,476 to $103,350 (target for conversions)
- **24% Bracket**: $103,351 to $197,300
- **Standard Deduction**: $15,000 (estimated)

### Tax Rates Applied
- **Traditional IRA Withdrawals**: 22%
- **Roth Conversions**: 22% (managed to stay in bracket)
- **Brokerage Capital Gains**: 15% (long-term)
- **Roth Withdrawals**: 0% (tax-free, but never used)

### Economic Assumptions
- **Inflation Rate**: 3% annually on all expenses
- **Market Returns**: 6% annually on all investment accounts
- **Social Security Benefit**: $36,000/year starting at age 67

## Key Requirements

### 1. Roth Preservation Rule
**CRITICAL**: The Roth accounts must NEVER be used for living expenses. This is the fundamental requirement for preserving the tax-free inheritance.

### 2. Tax Efficiency
- Conversions are managed to stay within the 22% tax bracket
- Conversion taxes are paid from taxable accounts (savings/brokerage)
- Withdrawal hierarchy optimizes for lowest tax impact

### 3. Cash Flow Management
- Sufficient liquid assets must be maintained for conversion taxes
- Conservative approach ensures no forced Roth withdrawals
- Annual expense projections include inflation adjustments

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Make sure you have `uv` installed.

### Setup the project:

```bash
# Clone or create the project directory
mkdir retirement-analysis
cd retirement-analysis

# Initialize the project
uv init .

# Install dependencies
uv add pandas numpy matplotlib

# Optional: Add development dependencies
uv add --dev pytest black flake8
```

## Usage

### Run the Roth conversion analysis:

```bash
# Run with uv
uv run python roth_conversion_strategy.py

# Or activate the environment and run directly
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python roth_conversion_strategy.py
```

## Expected Outcomes

### Conversion Results
- **Total Conversions**: ~$600,000 - $800,000 over conversion period
- **Final Roth Balance**: $1,000,000+ preserved for inheritance
- **Tax Efficiency**: Conversions managed within 22% bracket
- **Zero Roth Withdrawals**: Complete preservation for heirs

### Performance Metrics
- **Inheritance Preservation**: 100% (no Roth withdrawals for expenses)
- **Tax Optimization**: Strategic bracket management
- **Asset Growth**: 6% annual returns on all accounts
- **Inflation Protection**: All expenses increase at 3% annually

## Output

The tool generates:

1. **Detailed Console Output**: Year-by-year progression showing:
   - Account balances after growth
   - Conversion decisions and amounts
   - Tax calculations and payments
   - Expense coverage methodology
   - End-of-year account balances

2. **Professional Visualizations**: Four-panel dashboard with:
   - Account balances over time (IRA vs Roth)
   - Annual Roth conversion amounts
   - Expenses vs Social Security benefits
   - Cumulative conversions and taxes

3. **CSV Export**: Complete dataset for further analysis including:
   - All account balances and transactions
   - Tax calculations and conversion details
   - Expense breakdowns and coverage sources

4. **Strategy Summary**: Final results showing:
   - Total conversions and taxes paid
   - Final account balances
   - Inheritance preservation status

## Key Insights

### Why This Strategy Works

1. **Tax Bracket Arbitrage**: Converts at 22% rate before potentially higher future rates
2. **Social Security Timing**: Aggressive conversions before SS reduces conversion capacity
3. **Roth Preservation**: Strict no-touch policy ensures maximum inheritance
4. **Liquidity Management**: Maintains sufficient cash for conversion taxes and expenses

### Critical Success Factors

1. **Sufficient Liquid Assets**: $1.5M in savings/brokerage provides conversion tax capacity
2. **Conservative Withdrawal Hierarchy**: Exhausts taxable accounts before touching Roth
3. **Market Growth Assumption**: 6% returns enable account growth despite withdrawals
4. **Reasonable Expenses**: $60K base (inflation-adjusted) is sustainable with this asset level

## Risk Considerations

### Market Risk
- Strategy assumes 6% average returns; poor market performance could force Roth withdrawals
- Consider sequence of returns risk in early retirement years

### Tax Law Changes
- Future tax rates may change, affecting conversion strategy effectiveness
- RMD age could change from current 73

### Longevity Risk
- Analysis assumes death at 85; longer life could require Roth withdrawals
- Consider long-term care costs not included in base expenses

### Inflation Risk
- 3% inflation assumption may be conservative
- Healthcare inflation typically exceeds general inflation

## Configuration

The analysis uses the following default assumptions:

- **Age Range**: 61-85 years (25 years)
- **Social Security**: $3,000/month ($36,000/year) starting at age 67
- **Inheritance Target**: $1,000,000 in tax-free Roth accounts
- **Investment Growth**: 6% annual return on all accounts

- **Initial Assets**:
  - 401k/IRA: $1,250,000
  - Roth Accounts: $250,000
  - Brokerage: $1,200,000
  - Savings: $250,000
  - Home Equity: $900,000

- **Annual Expenses**:
  - Base expenses: $54,000/year
  - Travel (ages 62-72): $20,000/year
  - One-time renovation at 62: $80,000
  - New car at 63: $20,000

- **Tax Rates**:
  - Traditional 401k/IRA: 15%
  - Roth conversions: 15%
  - Brokerage (capital gains): 10%
  - Roth withdrawals: 0%

## Strategies Analyzed

### Strategy 1: Tax-Efficient Withdrawals
- Prioritizes tax-free and low-tax withdrawals first
- Uses Social Security to reduce withdrawal needs
- Preserves Roth accounts for inheritance
- Withdraws from: Savings → Brokerage → Traditional → Roth

### Strategy 2: Roth Conversion Strategy
- Converts traditional IRA to Roth before age 67 (pre-Social Security)
- Targets $1M in tax-free Roth accounts by age 85
- Uses taxable accounts to pay conversion taxes
- Optimizes for tax-free inheritance while minimizing lifetime taxes
- Limits conversions to $100K/year to avoid tax bracket jumps

## Output

The tool generates:

1. **Console Reports**: Detailed year-by-year breakdown for each strategy
2. **Strategy Comparison**: Side-by-side analysis with automatic recommendations
3. **CSV Files**: Exportable data in `output/` directory
4. **Advanced Visualizations**: Strategy-specific charts saved as PNG files:

### Tax-Efficient Strategy Charts:
   - Total remaining assets over time
   - Roth balance vs inheritance target
   - Annual taxes vs Social Security benefits
   - Income sources breakdown by year

### Roth Conversion Strategy Charts:
   - All of the above, plus:
   - Annual Roth conversion amounts
   - Cumulative taxes and conversions over time

## Key Insights

The tool will automatically recommend the best strategy based on:
1. **Primary Goal**: Achieving the $1M tax-free inheritance target
2. **Secondary Goal**: Minimizing total lifetime taxes
3. **Considerations**: Total asset preservation and cash flow

Expected outcomes:
- **Roth Conversion Strategy** typically achieves inheritance goals better
- **Tax-Efficient Strategy** may have lower total taxes but less inheritance
- **Social Security** significantly reduces withdrawal pressure after age 67

## Development

### Running tests:

```bash
uv run pytest
```

### Code formatting:

```bash
uv run black src/
```

### Linting:

```bash
uv run flake8 src/
```

## Project Structure

```
retirement-analysis/
├── src/
│   └── retirement_analysis/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── output/          # Generated reports and charts
├── pyproject.toml   # Project configuration
├── README.md
└── .python-version  # Python version specification
```

## Monte Carlo Analysis

The project now includes comprehensive Monte Carlo simulations to test strategy robustness under market volatility.

### Running Monte Carlo Analysis

```bash
# Run Monte Carlo analysis
uv run monte-carlo-analysis

# Run combined analysis (both deterministic and Monte Carlo)
uv run python src/retirement_analysis/combined_analysis.py
```


### Monte Carlo Features

- **1000+ simulations** across multiple market scenarios
- **5 market scenarios**: Base case, low return, high volatility, stagflation, great recession
- **Comprehensive risk analysis**: Sequence of returns risk, asset shortfall probability
- **Advanced visualizations**: 9-panel dashboard with statistical distributions

### Market Scenarios Tested

- **Base Case**: 6% return, 18% volatility
- **Low Return**: 4% return, 18% volatility  
- **High Volatility**: 6% return, 25% volatility
- **Stagflation**: 3% return, 22% volatility
- **Great Recession**: 2% return, 30% volatility
```

## Step 6: Commands to Execute

```bash
# Navigate to your project
cd retirement-analysis

# Add the Monte Carlo script to the correct location
# (Copy monte_carlo_simulation.py to src/retirement_analysis/)

# Update pyproject.toml with the new configuration

# Install/sync the updated project
uv sync

# Test that everything works
uv run retirement-analysis          # Original strategy
uv run monte-carlo-analysis         # Monte Carlo simulations
uv run basic-strategy              # If you kept the old main.py

# Run tests
uv run pytest
```

## Final Project Structure

```
retirement-analysis/
├── src/
│   └── retirement_analysis/
│       ├── __init__.py
│       ├── main.py                          # Original strategy (if kept)
│       ├── roth_conversion_strategy.py      # Clean standalone strategy
│       ├── monte_carlo_simulation.py        # New Monte Carlo analysis
│       └── combined_analysis.py             # Optional: runs both analyses
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_monte_carlo.py                  # New Monte Carlo tests
├── output/                                  # Generated reports and charts
│   ├── roth_conversion_analysis.png
│   ├── monte_carlo_comprehensive_analysis.png
│   ├── monte_carlo_summary.csv
│   └── monte_carlo_detailed_*.csv
├── pyproject.toml                           # Updated with new entry points
├── README.md                                # Updated with Monte Carlo info
└── .python-version
```

This integration gives you a comprehensive retirement analysis suite with both deterministic and probabilistic modeling!
## Future Enhancements

- [ ] Investment growth modeling (4-7% annual returns)
- [ ] Inflation adjustments for expenses
- [ ] Required Minimum Distribution (RMD) calculations
- [ ] Multiple withdrawal strategies comparison
- [ ] Monte Carlo simulations for market volatility
- [ ] Social Security integration
- [ ] Healthcare cost projections

## License

MIT License - feel free to modify and use for your retirement planning needs.