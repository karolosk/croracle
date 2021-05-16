from errors.custom import FileMissingColumn
from services.purchase_service import get_total_purchase_stats, get_purchase_graphs
from services.earnings_service import get_total_earning_stats, get_total_earnings_breakdown, get_earnings_graphs
from utils.constants import NEEDED_DF_COLUMNS
import pandas as pd


def get_stats(data):

    are_columns_valid = all(item in list(data) for item in NEEDED_DF_COLUMNS)

    if not are_columns_valid:
        raise FileMissingColumn()

    native_currency = data["Native Currency"][0]

    data["Timestamp (UTC)"] = pd.to_datetime(data["Timestamp (UTC)"]).apply(lambda x: x.date())
    data["YearMonth"] = (data["Timestamp (UTC)"] + pd.offsets.MonthEnd(-1) + pd.offsets.Day(1))

    df_crypto_purchase = data[(data["Transaction Kind"] == "crypto_purchase")]
    df_crypto_earnings = data[(data["Transaction Kind"] == "crypto_earn_interest_paid") |
                              (data["Transaction Kind"] == "reimbursement") |
                              (data["Transaction Kind"] == "mco_stake_reward") |
                              (data["Transaction Kind"] == "referral_card_cashback") |
                              (data["Transaction Kind"] == "referral_gift")
                              ]
    return {
        "total_purchases": get_total_purchase_stats(df_crypto_purchase, native_currency),
        "total_earnings": get_total_earning_stats(df_crypto_earnings, native_currency),
        "purchase_graphs": get_purchase_graphs(df_crypto_purchase, native_currency),
        "earnings_break_down": get_total_earnings_breakdown(df_crypto_earnings, native_currency),
        "earning_graphs": get_earnings_graphs(df_crypto_earnings, native_currency)
    }


