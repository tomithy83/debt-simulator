# Debt Repayment Simulator

A Python CLI tool to simulate and compare multiple debt repayment strategies — including snowball, avalanche, and hybrid approaches — using real amortization math.

## Features

- Load debts from a CSV file (e.g., student loans, car loans, credit cards).
- Simulate multiple repayment strategies:
  - Snowball (lowest balance first)
  - Avalanche (highest interest first)
  - Split 50/50
  - Proportional by interest
  - Smart Snowball (interest-weighted)
  - Snowball → Avalanche hybrid
  - Reverse variants of Snowball/Avalanche
- Output amortization schedules to CSV
- Summary report with payoff months, interest paid, and total cost
- CLI support with sensible defaults
- Drop-in fallback debt data if no CSV is provided

## Folder Structure

```bash
debt-simulator/
├── main.py               # Entry point
├── simulator.py          # Core logic
├── strategies.py         # Repayment strategies definitions
├── input/
│   └── debts.csv         # Your debt data here (not required)
├── output/
│   └── [date]/...        # Generated reports
└── README.md
```

## Usage

Clone this repo:

```bash
git clone https://github.com/yourusername/debt-simulator.git
cd debt-simulator
```

(Optional) Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the simulation:

```bash
python main.py path\to\your.csv --extra 2000 --months 240
```

### Arguments

| Argument        | Description                              | Default       |
| --------------- | ---------------------------------------- | ------------- |
| `input.csv`     | Path to CSV file of debt items           | fallback data |
| `extra`         | Extra monthly payment applied to debts   | `2000`        |
| `--months`      | Max number of months to simulate         | `600`         |
| `--output_dir`  | Output directory for generated CSV files | `./output`    |



## Input CSV Format

Case-sensitive columns required:
| Column       | Description                                                                             |
|--------------|-----------------------------------------------------------------------------------------|
| `Loan`       | A name or label for the debt item (e.g. "Car Loan", "Student Loan 01-03", "House")      |
| `Balance`    | The current total owed on the loan or debt (e.g. 10000.00)                              |
| `Rate`       | The annual interest rate as a percentage (e.g. 6.55 for 6.55%)                          |
| `MinPayment` | The required minimum monthly payment for the debt (e.g. 500)                            |


```csv
Item,Rate,Balance,MinPayment
Car,11.97,12054.76,412.00
Student Loan,5.75,1166.99,16.20
Mortgage,3.625,153,458.55, 1423.70
...
```

## Output

- A subfolder with today’s date is created under ./output/
- Each strategy generates:
    - A CSV monthly amortization of all loans for detailed analysis, showing:
        - Starting balance each month per loan
        - Interest paid each month per loan
        - Principle Paid each month per loan
        - Ending balance each month per loan 
    - A CSV summary of all loans to provide an overview of each strategy, showing:
        - Payoff date per loan
        - Months until payoff per loan
        - Principle paid per loan
        - Interest paid per loan
        - Total pais per loan
    - A CLI summary row for quick comparison showing:
        - Total interest paid
        - Total months to payoff
        - Final loan's payoff date