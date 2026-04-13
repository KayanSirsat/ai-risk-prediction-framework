import pandas as pd
import numpy as np
import os
import random

# Constants
RAW_DATA_PATH = "data/raw_jira_data.csv"
PROCESSED_DATA_PATH = "data/ml_ready_data.csv"
SAMPLE_SIZE = 10000
DAILY_BURN_RATE = 500


def load_and_sample_data(path, sample_size):
    print(f"[1/6] Loading data from {path}...")
    if not os.path.exists(path):
        # Create a dummy raw file if it doesn't exist to avoid crash
        print("[WARNING] Raw file not found. Creating dummy raw dataset for simulation.")
        df = pd.DataFrame(
            {"Issue_ID": range(sample_size), "Summary": ["Draft issue"] * sample_size}
        )
        df.to_csv(path, index=False)

    df = pd.read_csv(path)
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
    return df


def inject_metadata(df):
    print("[2/6] Injecting Project and Developer Metadata...")

    # Categorical Options
    priorities = ["High", "Medium", "Low"]
    issue_types = ["Bug", "Task", "Epic"]
    seniorities = ["Junior", "Mid", "Senior"]
    story_points_options = [1, 2, 3, 5, 8, 13]

    # Synthetic Text components
    actions = ["Fix", "Implement", "Optimize", "Refactor", "Update"]
    targets = [
        "Login API",
        "Database Schema",
        "UI Header",
        "Payment Gateway",
        "Auth Module",
    ]

    df["Priority"] = np.random.choice(priorities, size=len(df))
    df["Issue_Type"] = np.random.choice(issue_types, size=len(df))
    df["Assignee_Seniority"] = np.random.choice(seniorities, size=len(df))
    df["Story_Points"] = np.random.choice(story_points_options, size=len(df))

    # Generate synthetic text
    df["Summary"] = [
        f"{random.choice(actions)} {random.choice(targets)}" for _ in range(len(df))
    ]
    df["Description"] = [
        f"Detail: {random.choice(actions)} the {random.choice(targets)} for improved performance."
        for _ in range(len(df))
    ]

    return df


def generate_metrics_with_signals(df):
    print("[3/6] Generating synthetic metrics with hidden signals...")

    # Base Estimation
    df["Estimated_Days"] = np.random.randint(2, 15, size=len(df))
    df["Budget_Allocated"] = df["Estimated_Days"] * DAILY_BURN_RATE

    # HIDDEN SIGNALS: Determine Actual Days based on metadata
    def calculate_actuals(row):
        base_days = row["Estimated_Days"]
        multiplier = 1.0

        # Signal 1: Junior + High Story Points = Delay
        if row["Assignee_Seniority"] == "Junior" and row["Story_Points"] >= 8:
            multiplier += 0.6

        # Signal 2: Bug + High Priority = Complexity/Delay
        if row["Issue_Type"] == "Bug" and row["Priority"] == "High":
            multiplier += 0.4

        # Signal 3: Senior + Small tasks = Efficiency
        if row["Assignee_Seniority"] == "Senior" and row["Story_Points"] <= 3:
            multiplier -= 0.2

        # Add some random noise
        noise = np.random.normal(1.1, 0.2)
        actual = (base_days * multiplier) * noise
        return max(1, round(actual))

    df["Actual_Days"] = df.apply(calculate_actuals, axis=1)
    df["Cost_Consumed"] = df["Actual_Days"] * DAILY_BURN_RATE

    return df


def calculate_risk_level(df):
    print("[4/6] Calculating target variable: Risk_Level...")

    def determine_risk(row):
        cost_overrun_pct = (row["Cost_Consumed"] / row["Budget_Allocated"]) - 1
        days_overrun = row["Actual_Days"] - row["Estimated_Days"]

        if cost_overrun_pct > 0.25 or days_overrun >= 4:
            return "High"
        elif cost_overrun_pct > 0.10 or days_overrun >= 2:
            return "Medium"
        else:
            return "Low"

    df["Risk_Level"] = df.apply(determine_risk, axis=1)
    print("\nRisk Level Distribution:")
    print(df["Risk_Level"].value_counts())
    print("-" * 30)
    return df


def clean_for_ml(df):
    print("[5/6] Cleaning dataset for ML export...")
    # Preserve ALL signals and metadata
    cols_to_keep = [
        "Priority",
        "Issue_Type",
        "Assignee_Seniority",
        "Story_Points",
        "Estimated_Days",
        "Budget_Allocated",
        "Actual_Days",
        "Cost_Consumed",
        "Summary",
        "Description",
        "Risk_Level",
    ]
    # Filter only existing columns to avoid KeyError
    df_final = df[[col for col in cols_to_keep if col in df.columns]].copy()
    return df_final


def save_processed_data(df, path):
    print(f"[6/6] Saving processed data to {path}...")
    df.to_csv(path, index=False)
    print("Pipeline executed successfully.")


if __name__ == "__main__":
    try:
        data = load_and_sample_data(RAW_DATA_PATH, SAMPLE_SIZE)
        data = inject_metadata(data)
        data = generate_metrics_with_signals(data)
        data = calculate_risk_level(data)
        data = clean_for_ml(data)
        save_processed_data(data, PROCESSED_DATA_PATH)
    except Exception as e:
        print(f"Pipeline failed: {e}")
