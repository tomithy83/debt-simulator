

def snowball_strategy(debts, plan, extra_total):
    unpaid = sorted([(i, debts.at[i, "Remaining"]) for i in range(len(debts)) if not debts.at[i, "PaidOff"]],
                    key=lambda x: x[1])
    priority = [i for i, _ in unpaid]
    return allocate_extra_funds_fully(plan, priority, extra_total)

def reverse_snowball_strategy(debts, plan, extra_total):
    unpaid = sorted(
        [(i, debts.at[i, "Remaining"]) for i in range(len(debts)) if not debts.at[i, "PaidOff"]],
        key=lambda x: x[1],
        reverse=True  # Biggest balances first
    )
    priority = [i for i, _ in unpaid]
    return allocate_extra_funds_fully(plan, priority, extra_total)


def avalanche_strategy(debts, plan, extra_total):
    unpaid = sorted([(i, debts.at[i, "Rate"]) for i in range(len(debts)) if not debts.at[i, "PaidOff"]],
                    key=lambda x: x[1], reverse=True)
    priority = [i for i, _ in unpaid]
    return allocate_extra_funds_fully(plan, priority, extra_total)

def reverse_avalanche_strategy(debts, plan, extra_total):
    unpaid = sorted(
        [(i, debts.at[i, "Rate"]) for i in range(len(debts)) if not debts.at[i, "PaidOff"]],
        key=lambda x: x[1]  # Lowest rates first
    )
    priority = [i for i, _ in unpaid]
    return allocate_extra_funds_fully(plan, priority, extra_total)


def split_50_50_strategy(debts, plan, extra_total):
    unpaid = [(i, debts.at[i, "Rate"], debts.at[i, "Remaining"])
              for i in range(len(debts)) if not debts.at[i, "PaidOff"]]
    if not unpaid:
        return {}

    highest_interest = sorted(unpaid, key=lambda x: x[1], reverse=True)[0][0]
    lowest_balance = sorted(unpaid, key=lambda x: x[2])[0][0]

    half = extra_total // 2
    first_alloc = allocate_extra_funds_fully(plan, [highest_interest], half)
    remaining = extra_total - sum(first_alloc.values())
    second_alloc = allocate_extra_funds_fully(plan, [lowest_balance], remaining)

    return {**first_alloc, **second_alloc}

def proportional_interest_strategy(debts, plan, extra_total):
    unpaid = [(i, debts.at[i, "Rate"]) for i in range(len(debts)) if not debts.at[i, "PaidOff"]]
    total_rate = sum(rate for _, rate in unpaid)
    if total_rate == 0:
        return {}

    allocation = {}
    remaining = extra_total
    for i, rate in unpaid:
        proportion = rate / total_rate
        max_extra = next((p["max_extra"] for p in plan if p["index"] == i), 0)
        alloc = min(remaining, extra_total * proportion, max_extra)
        if alloc > 0:
            allocation[i] = alloc
            remaining -= alloc
        if remaining <= 0:
            break

    return allocation

def fastest_payoff_strategy(debts, plan, extra_total):
    estimates = []
    for p in plan:
        i = p["index"]
        if debts.at[i, "PaidOff"]:
            continue
        remaining = debts.at[i, "Remaining"]
        base = p["base"]
        if base > 0:
            months = remaining / base
            estimates.append((i, months))

    priority = [i for i, _ in sorted(estimates, key=lambda x: x[1])]
    return allocate_extra_funds_fully(plan, priority, extra_total)

def smart_snowball_strategy(debts, plan, extra_total):
    scores = []
    for i in range(len(debts)):
        if debts.at[i, "PaidOff"]:
            continue
        balance = debts.at[i, "Remaining"]
        rate = debts.at[i, "Rate"]
        score = (rate ** 1.5) / (balance + 1)
        scores.append((i, score))

    priority = [i for i, _ in sorted(scores, key=lambda x: x[1], reverse=True)]
    return allocate_extra_funds_fully(plan, priority, extra_total)


def snowball_then_avalanche_strategy(debts, payment_plan, monthly_extra):
    # Count how many loans are paid off
    paid_off = sum(debts["PaidOff"])

    # Switch strategy after x are paid off
    if paid_off < 3:
        return snowball_strategy(debts, payment_plan, monthly_extra)
    else:
        return avalanche_strategy(debts, payment_plan, monthly_extra)

def avalanche_then_snowball_strategy(debts, payment_plan, monthly_extra):
    # Count how many loans are paid off
    paid_off = sum(debts["PaidOff"])

    # Switch strategy after x are paid off
    if paid_off >= 2:
        return snowball_strategy(debts, payment_plan, monthly_extra)
    else:
        return avalanche_strategy(debts, payment_plan, monthly_extra)



def allocate_extra_funds_fully(plan, priority_indices, extra_total):
    allocation = {i: 0 for i in priority_indices}
    remaining = extra_total

    for i in priority_indices:
        max_extra = next((p["max_extra"] for p in plan if p["index"] == i), 0)
        allocatable = min(remaining, max_extra)
        allocation[i] = allocatable
        remaining -= allocatable
        if remaining <= 0:
            break

    return {i: amt for i, amt in allocation.items() if amt > 0}

strategies = {
    "snowball": snowball_strategy,
    "avalanche": avalanche_strategy,
    "split_50_50": split_50_50_strategy,
    "proportional": proportional_interest_strategy,
    "fastest_payoff": fastest_payoff_strategy,
    "smart_snowball": smart_snowball_strategy,
    "snowball_then_avalanche": snowball_then_avalanche_strategy,
    "avalanche_then_snowball": avalanche_then_snowball_strategy,
    "reverse_snowball": reverse_snowball_strategy,
    "reverse_avalanche": reverse_avalanche_strategy,
}