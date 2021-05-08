import pandas as pd


def process_file(filepath):
    df = pd.read_csv(filepath)
    return find_sum_expenses(df)


def find_total_earnings():
    pass


def find_categorical_earnings():
    pass


def find_sum_expenses(df):
    return df.groupby(["Transaction Kind", "Currency"])["Native Amount"].sum()[1]


# Transaction Kind
# crypto_purchase # currency, # native ammount # usd ammount
# crypto_earn_interest_paid