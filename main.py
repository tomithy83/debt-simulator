import pandas as pd
import strategies 
import simulator
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Debt Repayment Simulator")
    parser.add_argument("input_csv", nargs="?", type=str, help="Path to input CSV file. Required columns: Loan, Balance, Rate, MinPayment", default=None)
    parser.add_argument("extra", nargs="?", type=float, help="Extra money to be added to payment each month", default=0)
    parser.add_argument("--months", type=int, help="Maximum number of months to simulate, defaults to 600 (50 years)", default=600)
    parser.add_argument("--output_dir", type=str, help="Path to output CSV files, defaults to './output'", default='./output')
    return parser.parse_args()



def main():
    args = parse_args()
    debts = simulator.load_debts(args.input_csv)
    schedules = simulator.run_and_export_strategies(debts, args.extra, args.months, strategies.strategies, export_dir=args.output_dir)
    simulator.summarize_strategies(schedules)


if __name__ == "__main__":
    main()