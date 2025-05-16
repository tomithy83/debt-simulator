from typing import List, Dict, Callable
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


FALLBACK_DATA = [
    {"Loan": "HomeLoan", "Rate": 3.0, "Balance": 200000.0, "MinPayment": 800.0},
    {"Loan": "CreditCard1", "Rate": 24.0, "Balance": 10000.0, "MinPayment": 50.0},
    {"Loan": "CreditCard2", "Rate": 22.0, "Balance": 12000.0, "MinPayment": 60.0},
    {"Loan": "CarLoan", "Rate": 18.0, "Balance": 25000.0, "MinPayment": 100.0}
]

def load_debts(csv_path=None):
    if csv_path and os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        print("⚠️ No valid input CSV found. Using fallback data.")
        return pd.DataFrame(FALLBACK_DATA)
    
# Function to simulate snowball or avalanche method
def simulate_repayment(
            debts: pd.DataFrame,
            strategy_func: Callable,
            monthly_extra: float,
            max_months: int 
            ) -> List[Dict]:
    debts = initialize_debts(debts.copy())
    schedule = []
    month = 1

    extra_pool = monthly_extra

    while not debts["PaidOff"].all() and month <= max_months:
        payment_plan = calculate_monthly_interest_and_base(debts)
        extra_allocation = strategy_func(debts, payment_plan, extra_pool)
        freed_up = apply_payments(debts, payment_plan, extra_allocation, extra_pool)
        schedule.extend(log_month(debts, payment_plan, month))

        # Add newly freed-up payments into the extra pool
        extra_pool += freed_up
        month += 1

    return schedule

def initialize_debts(debts: pd.DataFrame) -> pd.DataFrame:
    debts["Remaining"] = debts["Balance"]
    debts["PaidOff"] = False
    return debts

def calculate_monthly_interest_and_base(debts: pd.DataFrame) -> List[Dict]:
    plan = []
    for i, row in debts.iterrows():
        if row["PaidOff"]:
            continue
        interest = (row["Remaining"] * row["Rate"] / 100) / 12
        base_payment = min(row["MinPayment"], row["Remaining"] + interest)
        plan.append({
            "index": i,
            "interest": interest,
            "base": base_payment,
            "max_extra": max(0, row["Remaining"] + interest - base_payment)
        })
    return plan

def apply_payments(
        debts: pd.DataFrame,
        plan: List[Dict],
        extra_allocation: Dict[int, float],
        monthly_extra: float
        ) -> float:
    remaining_extra = monthly_extra
    freed_payment_total = 0.0  

    for p in plan:
        i = p["index"]
        if debts.at[i, "PaidOff"]:
            continue

        extra = min(extra_allocation.get(i, 0), p["max_extra"], remaining_extra)
        total_payment = min(p["base"] + extra, debts.at[i, "Remaining"] + p["interest"])
        principal_paid = total_payment - p["interest"]

        debts.at[i, "Remaining"] -= principal_paid
        if debts.at[i, "Remaining"] <= 0.01:
            debts.at[i, "Remaining"] = 0
            debts.at[i, "PaidOff"] = True
            freed_payment_total += debts.at[i, "MinPayment"] 

        p["extra"] = extra
        p["total_payment"] = total_payment
        p["principal_paid"] = principal_paid

        remaining_extra -= extra

    return freed_payment_total  

def month_to_date(month: int, start_month: datetime = None) -> List[str]:
    """Returns a list of YYYY-MM month strings going back `months` from `start_month`."""
    if start_month is None:
        start_month = datetime.today().replace(day=1)

    result_date = start_month + relativedelta(months=month - 1)
    return result_date.strftime("%b %Y")  # e.g., "Jan 2025"


def log_month(debts: pd.DataFrame, plan: List[Dict], month: int) -> List[Dict]:
    log = []
    for p in plan:
        i = p["index"]
        if debts.at[i, "PaidOff"] and debts.at[i, "Remaining"] == 0:
            pass  # Include final zeroing-out payment if you want
        log.append({
            "Month": month,
            "Date": month_to_date(month),
            "Loan": debts.at[i, "Loan"],
            "Original Balance": round(debts.at[i, "Balance"], 2),
            "Interest Rate": debts.at[i, "Rate"],
            "Min Payment": round(debts.at[i, "MinPayment"], 2),
            "Starting Balance": round(debts.at[i, "Remaining"] + p["principal_paid"], 2),
            "Monthly Payment": round(p["total_payment"], 2),
            "Interest Paid": round(p["interest"], 2),
            "Principal Paid": round(p["principal_paid"], 2),
            "Ending Balance": round(debts.at[i, "Remaining"], 2)
        })
    return log

def generate_strategy_summary(debts_df, schedule_df):
    report = []

    for loan in debts_df.itertuples(index=False):
        loan_id = loan.Loan  # adjust this if your ID field is different
        loan_schedule = schedule_df[schedule_df["Loan"] == loan_id]

        if loan_schedule.empty:
            payoff_month = None
            months = 0
            principal_paid = 0.0
            interest_paid = 0.0
        else:
            payoff_month = month_to_date(loan_schedule["Month"].max())
            months = len(loan_schedule)
            principal_paid = loan_schedule["Principal Paid"].sum()
            interest_paid = loan_schedule["Interest Paid"].sum()

        total_paid = principal_paid + interest_paid

        report.append({
            "Loan": loan_id,
            "Original Balance": loan.Balance,
            "Rate": loan.Rate,
            "Min Payment": loan.MinPayment,  # NEW
            "Payoff Month": payoff_month,
            "Months to Payoff": months,
            "Principal Paid": round(principal_paid, 2),
            "Interest Paid": round(interest_paid, 2),
            "Total Paid": round(total_paid, 2),
        })
    sorted_report = sorted(report, key=lambda x: x['Months to Payoff'])
    return pd.DataFrame(sorted_report)

def summarize_strategies(strategies: dict):
    for name, schedule in strategies.items():
        df = pd.DataFrame(schedule)
        total_interest = round(df["Interest Paid"].sum(), 2)
        total_months = df["Month"].max()
        last_month = month_to_date(total_months)
        print(f"{name:<25} → Interest: ${total_interest:>10,.2f}   Months: {total_months:>5} ({last_month})")


def run_and_export_strategies(debts, monthly_extra, max_months, strategies, export_dir="output"):
    today = datetime.today().strftime('%Y-%m-%d')
    full_export_dir = os.path.join(export_dir, today)
    os.makedirs(full_export_dir, exist_ok=True)
    results = {}

    for name, strategy_func in strategies.items():
        schedule = simulate_repayment(debts, strategy_func, monthly_extra, max_months)
        df = pd.DataFrame(schedule)
        amortization_path = os.path.join(full_export_dir, f"{name}_amortization.csv")
        df.to_csv(amortization_path, index=False)

        summary_df = generate_strategy_summary(debts, df)
        summary_path = os.path.join(full_export_dir, f"{name}_summary.csv")
        summary_df.to_csv(summary_path, index=False)

        results[name] = schedule


    return results