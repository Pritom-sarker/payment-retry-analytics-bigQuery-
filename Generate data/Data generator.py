import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# =========================
# CONFIG
# =========================

OUTPUT_DIR = Path("./metro_payment_retry_dataset")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMER_COUNT = 1500

MIN_ORDERS_PER_CUSTOMER = 300
MAX_ORDERS_PER_CUSTOMER = 600

DIRTY_RATE = 0.15

# Real retail case: people rarely abandon after payment issue
CANCEL_RATE = 0.05

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31, 23, 59, 59)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


PAYMENT_METHODS = ["TAP", "INSERT_CARD", "CASH"]

STORE_LOCATIONS = [
    "Thunder Bay - Arthur Street",
    "Thunder Bay - River Street",
    "Thunder Bay - Red River Road",
    "Thunder Bay - Memorial Avenue"
]

PRODUCT_CATEGORIES = [
    "Grocery",
    "Bakery",
    "Dairy",
    "Meat",
    "Frozen",
    "Beverage",
    "Household",
    "Personal Care"
]

FAILURE_REASONS = [
    "TAP_NOT_DETECTED",
    "CARD_DECLINED",
    "PIN_FAILED",
    "NETWORK_ERROR",
    "LIMIT_EXCEEDED",
    "CUSTOMER_RETRY_REQUIRED"
]


# =========================
# HELPERS
# =========================

def random_datetime(start, end):
    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, seconds))


def generate_amount():
    amount_type = random.choices(
        ["small", "medium", "large"],
        weights=[0.62, 0.30, 0.08],
        k=1
    )[0]

    if amount_type == "small":
        return round(random.uniform(5, 50), 2)
    elif amount_type == "medium":
        return round(random.uniform(50, 180), 2)
    else:
        return round(random.uniform(180, 650), 2)


def generate_customers():
    first_names = [
        "John", "Sarah", "Michael", "Emma", "David", "Olivia",
        "Daniel", "Sophia", "James", "Ava", "Robert", "Mia",
        "William", "Emily", "Noah", "Lily", "Ethan", "Grace"
    ]

    last_names = [
        "Smith", "Brown", "Johnson", "Williams", "Miller",
        "Davis", "Wilson", "Anderson", "Thomas", "Taylor",
        "Moore", "Martin", "Lee", "Walker", "Hall", "King"
    ]

    rows = []

    for i in range(1, CUSTOMER_COUNT + 1):
        rows.append({
            "customer_id": f"CUST_{i:05d}",
            "customer_name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "customer_segment": random.choice(["REGULAR", "OCCASIONAL", "HIGH_VALUE", "NEW"]),
            "signup_date": random_datetime(datetime(2022, 1, 1), datetime(2024, 12, 31)).date()
        })

    return pd.DataFrame(rows)


def choose_attempt_count():
    """
    Real checkout behavior:
    Most people succeed in 1-2 attempts.
    Some tap several times before switching.
    Very few reach 4 attempts.
    """
    return random.choices(
        [1, 2, 3, 4],
        weights=[58, 27, 11, 4],
        k=1
    )[0]


def choose_payment_method(attempt_number, previous_methods):
    """
    Realistic self-checkout payment behavior.

    Attempt 1:
    - 95% TAP
    - 4% INSERT_CARD
    - 1% CASH

    Attempt 2:
    - 70% TAP again
    - 25% INSERT_CARD
    - 5% CASH

    Attempt 3:
    - 35% TAP
    - 50% INSERT_CARD
    - 15% CASH

    Attempt 4:
    - 15% TAP
    - 55% INSERT_CARD
    - 30% CASH
    """

    if attempt_number == 1:
        return random.choices(
            ["TAP", "INSERT_CARD", "CASH"],
            weights=[95, 4, 1],
            k=1
        )[0]

    elif attempt_number == 2:
        return random.choices(
            ["TAP", "INSERT_CARD", "CASH"],
            weights=[70, 25, 5],
            k=1
        )[0]

    elif attempt_number == 3:
        return random.choices(
            ["TAP", "INSERT_CARD", "CASH"],
            weights=[35, 50, 15],
            k=1
        )[0]

    else:
        return random.choices(
            ["TAP", "INSERT_CARD", "CASH"],
            weights=[15, 55, 30],
            k=1
        )[0]


def choose_success_attempt(attempt_count):
    """
    Most customers eventually complete payment.
    If there are more attempts, success is usually at the final or near-final attempt.
    """
    if attempt_count == 1:
        return 1

    if attempt_count == 2:
        return random.choices([1, 2], weights=[35, 65], k=1)[0]

    if attempt_count == 3:
        return random.choices([1, 2, 3], weights=[20, 35, 45], k=1)[0]

    return random.choices([1, 2, 3, 4], weights=[10, 20, 30, 40], k=1)[0]


def choose_failure_reason(payment_method):
    if payment_method == "TAP":
        return random.choices(
            ["TAP_NOT_DETECTED", "NETWORK_ERROR", "LIMIT_EXCEEDED", "CUSTOMER_RETRY_REQUIRED"],
            weights=[55, 20, 15, 10],
            k=1
        )[0]

    if payment_method == "INSERT_CARD":
        return random.choices(
            ["PIN_FAILED", "CARD_DECLINED", "NETWORK_ERROR", "CUSTOMER_RETRY_REQUIRED"],
            weights=[40, 25, 20, 15],
            k=1
        )[0]

    return random.choices(
        ["CUSTOMER_RETRY_REQUIRED", "NETWORK_ERROR"],
        weights=[80, 20],
        k=1
    )[0]


def inject_order_data_issue(order_row):
    issue_type = random.choice([
        "missing_customer_id",
        "missing_order_time",
        "future_order_time",
        "negative_order_amount",
        "zero_order_amount",
        "missing_order_amount"
    ])

    if issue_type == "missing_customer_id":
        order_row["customer_id"] = None

    elif issue_type == "missing_order_time":
        order_row["order_time"] = None

    elif issue_type == "future_order_time":
        order_row["order_time"] = random_datetime(
            datetime(2026, 1, 1),
            datetime(2026, 12, 31)
        )

    elif issue_type == "negative_order_amount":
        order_row["order_amount"] = -abs(float(order_row["order_amount"]))

    elif issue_type == "zero_order_amount":
        order_row["order_amount"] = 0

    elif issue_type == "missing_order_amount":
        order_row["order_amount"] = None

    return order_row


def inject_payment_data_issue(payment_row, order_time):
    issue_type = random.choice([
        "missing_order_id",
        "missing_attempt_time",
        "future_attempt_time",
        "attempt_before_order",
        "negative_attempt_amount",
        "zero_attempt_amount",
        "missing_attempt_amount"
    ])

    if issue_type == "missing_order_id":
        payment_row["order_id"] = None

    elif issue_type == "missing_attempt_time":
        payment_row["attempt_time"] = None

    elif issue_type == "future_attempt_time":
        payment_row["attempt_time"] = random_datetime(
            datetime(2026, 1, 1),
            datetime(2026, 12, 31)
        )

    elif issue_type == "attempt_before_order":
        payment_row["attempt_time"] = order_time - timedelta(minutes=random.randint(1, 120))

    elif issue_type == "negative_attempt_amount":
        payment_row["attempt_amount"] = -abs(float(payment_row["attempt_amount"]))

    elif issue_type == "zero_attempt_amount":
        payment_row["attempt_amount"] = 0

    elif issue_type == "missing_attempt_amount":
        payment_row["attempt_amount"] = None

    return payment_row


# =========================
# MAIN GENERATOR
# =========================

def generate_dataset():
    customers_df = generate_customers()
    customer_ids = customers_df["customer_id"].tolist()

    orders = []
    payment_attempts = []

    order_counter = 1

    for customer_id in customer_ids:
        customer_order_count = random.randint(
            MIN_ORDERS_PER_CUSTOMER,
            MAX_ORDERS_PER_CUSTOMER
        )

        for _ in range(customer_order_count):
            order_id = f"ORD_{order_counter:09d}"
            order_counter += 1

            order_time = random_datetime(START_DATE, END_DATE)
            order_amount = generate_amount()

            order_row = {
                "order_id": order_id,
                "customer_id": customer_id,
                "order_time": order_time,
                "order_amount": order_amount,
                "store_location": random.choice(STORE_LOCATIONS),
                "country": "Canada",
                "product_category": random.choice(PRODUCT_CATEGORIES)
            }

            if random.random() < DIRTY_RATE:
                order_row = inject_order_data_issue(order_row)

            orders.append(order_row)

            attempt_count = choose_attempt_count()

            # Real retail case: only around 5% abandon/cancel
            will_cancel = random.random() < CANCEL_RATE

            if will_cancel:
                cancel_after_attempt = random.randint(1, attempt_count)
                success_attempt = None
            else:
                cancel_after_attempt = None
                success_attempt = choose_success_attempt(attempt_count)

            previous_methods = []

            for attempt_number in range(1, attempt_count + 1):
                payment_attempt_id = f"PAY_{uuid.uuid4().hex[:14].upper()}"

                attempt_time = order_time + timedelta(minutes=random.randint(0, 5 * attempt_number))

                payment_method = choose_payment_method(
                    attempt_number=attempt_number,
                    previous_methods=previous_methods
                )

                previous_methods.append(payment_method)

                if will_cancel and attempt_number == cancel_after_attempt:
                    payment_status = "CANCELLED"
                    failure_reason = "CUSTOMER_CANCELLED"

                elif will_cancel and attempt_number > cancel_after_attempt:
                    break

                elif success_attempt is not None and attempt_number == success_attempt:
                    payment_status = "SUCCESS"
                    failure_reason = None

                elif success_attempt is not None and attempt_number > success_attempt:
                    break

                else:
                    payment_status = "FAILED"
                    failure_reason = choose_failure_reason(payment_method)

                payment_row = {
                    "payment_attempt_id": payment_attempt_id,
                    "order_id": order_id,
                    "attempt_number": attempt_number,
                    "attempt_time": attempt_time,
                    "payment_method": payment_method,
                    "payment_status": payment_status,
                    "attempt_amount": order_amount,
                    "failure_reason": failure_reason
                }

                if random.random() < DIRTY_RATE:
                    payment_row = inject_payment_data_issue(payment_row, order_time)

                payment_attempts.append(payment_row)

    orders_df = pd.DataFrame(orders)
    payment_attempts_df = pd.DataFrame(payment_attempts)

    # Duplicate around 1% of payment rows silently
    duplicate_rows = payment_attempts_df.sample(frac=0.01, random_state=RANDOM_SEED)
    payment_attempts_df = pd.concat(
        [payment_attempts_df, duplicate_rows],
        ignore_index=True
    )

    # Shuffle final data
    orders_df = orders_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    payment_attempts_df = payment_attempts_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    return customers_df, orders_df, payment_attempts_df


# =========================
# RUN
# =========================

if __name__ == "__main__":
    customers_df, orders_df, payment_attempts_df = generate_dataset()

    customers_path = OUTPUT_DIR / "customers.csv"
    orders_path = OUTPUT_DIR / "orders.csv"
    payments_path = OUTPUT_DIR / "payment_attempts.csv"

    customers_df.to_csv(customers_path, index=False)
    orders_df.to_csv(orders_path, index=False)
    payment_attempts_df.to_csv(payments_path, index=False)

    print("Dataset generated successfully.")
    print(f"Customers: {len(customers_df):,}")
    print(f"Orders: {len(orders_df):,}")
    print(f"Payment attempts: {len(payment_attempts_df):,}")

    print("\nFiles saved:")
    print(customers_path)
    print(orders_path)
    print(payments_path)

    print("\nPayment status distribution:")
    print(payment_attempts_df["payment_status"].value_counts(dropna=False))

    print("\nAttempt count distribution:")
    print(payment_attempts_df["attempt_number"].value_counts(dropna=False).sort_index())

    print("\nPayment method distribution:")
    print(payment_attempts_df["payment_method"].value_counts(dropna=False))

    print("\nPayment method by attempt number:")
    print(
        payment_attempts_df
        .pivot_table(
            index="attempt_number",
            columns="payment_method",
            values="payment_attempt_id",
            aggfunc="count",
            fill_value=0
        )
    )

    print("\nPayment status by attempt number:")
    print(
        payment_attempts_df
        .pivot_table(
            index="attempt_number",
            columns="payment_status",
            values="payment_attempt_id",
            aggfunc="count",
            fill_value=0
        )
    )

    print("\nSample orders:")
    print(orders_df.head())

    print("\nSample payment attempts:")
    print(payment_attempts_df.head())
