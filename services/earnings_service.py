import dash_bootstrap_components as dbc
import dash_html_components as html

from services.graph_service import get_timeline_chart, get_scatter_plot, get_pie_chart


def get_total_earning_stats(df_earnings, native_currency):
    if df_earnings.empty:
        native_amount = 0
        native_amount_usd = 0
    else:
        native_amount = round(float(df_earnings["Native Amount"].sum()), 2)
        native_amount_usd = round(float(df_earnings["Native Amount (in USD)"].sum()), 2)

    earnings_total_data = html.Div(
        [
            html.H5("Earnings"),
            html.P(
                children=[
                    html.Span(native_amount, ),
                    html.Span(f" USD", className="total-info-label", ),
                ],
                className="total-info-data",
            ),
            html.P(
                children=[
                    html.Span(native_amount_usd),
                    html.Span(f" {native_currency}", className="total-info-label", ),
                ],
                className="total-info-data",
            ),
        ],
        className="total-info",
    )

    return earnings_total_data


def get_total_earnings_breakdown(df_earnings, native_currency):
    referral_card_cashback = get_earnings_by_transaction_type(df_earnings, "referral_card_cashback", native_currency)
    stake_rewards = get_earnings_by_transaction_type(df_earnings, "mco_stake_reward", native_currency)
    earn_rewards = get_earnings_by_transaction_type(df_earnings, "crypto_earn_interest_paid", native_currency)
    reimbursement_rewards = get_earnings_by_transaction_type(df_earnings, "reimbursement", native_currency)
    referral_gift_rewards = get_earnings_by_transaction_type(df_earnings, "referral_gift", native_currency)

    return [dbc.Col(width=1), referral_card_cashback, stake_rewards, earn_rewards, reimbursement_rewards,
            referral_gift_rewards]


def get_earnings_by_transaction_type(df, earning_category, native_currency):
    df_earning_category = df[(df["Transaction Kind"] == earning_category)]

    if df_earning_category.empty:
        native_earnings = 0
        usd_earnings = 0
    else:
        df_earning_category_grouped = df_earning_category.groupby(
            ["Transaction Kind", "Transaction Description"]).sum()
        native_earnings = round(float(df_earning_category_grouped["Native Amount"].sum()), 2, )
        usd_earnings = round(float(df_earning_category_grouped["Native Amount (in USD)"].sum()), 2, )

    return dbc.Col(
        className="total-info",
        children=[
            html.H5(map_transaction_type_to_title(earning_category)),
            html.P(
                children=[
                    html.Span(
                        native_earnings,
                        className="total-info-data",
                    ),
                    html.Span(
                        f" {native_currency}",
                        className="total-info-label",
                    ),
                ],
            ),
            html.P(
                children=[
                    html.Span(
                        usd_earnings,
                        className="total-info-data",
                    ),
                    html.Span(f" USD", className="total-info-label"),
                ],
            ),
        ],
        width=2
    )


def get_earnings_graphs(df_earnings, native_currency):
    df_crypto_earnings_grouped_type_date = (df_earnings.groupby(["YearMonth"], as_index=False).sum().sort_values(by="YearMonth"))
    timeline = get_timeline_chart(df_crypto_earnings_grouped_type_date, 'YearMonth', 'Native Amount', 'earnings',native_currency)
    scatter_plot = get_scatter_plot(df_earnings, 'Timestamp (UTC)', 'Native Amount', 'Transaction Description','Native Amount', 'earnings')

    graphs = html.Div(
        children=[
            dbc.Row(
                children=[
                    dbc.Col(get_earnings_pie_chart(df_earnings), width=6),
                    dbc.Col(timeline, width=6)
                ],
            ),
            dbc.Row(
                children=[
                    dbc.Col(children=scatter_plot)
                ],
                no_gutters=True
            )
        ], )

    return graphs


def get_earnings_pie_chart(df_earnings):
    df_earnings_grouped = df_earnings.groupby(["Transaction Kind"], as_index=False).sum()
    df_earnings_grouped = df_earnings_grouped.replace(["crypto_earn_interest_paid"],
                                                      map_transaction_type_to_title("crypto_earn_interest_paid"))
    df_earnings_grouped = df_earnings_grouped.replace(["mco_stake_reward"],
                                                      map_transaction_type_to_title("mco_stake_reward"))
    df_earnings_grouped = df_earnings_grouped.replace(["referral_card_cashback"],
                                                      map_transaction_type_to_title("referral_card_cashback"))
    df_earnings_grouped = df_earnings_grouped.replace(["referral_gift"], map_transaction_type_to_title("referral_gift"))
    df_earnings_grouped = df_earnings_grouped.replace(["reimbursement"], map_transaction_type_to_title("reimbursement"))

    return get_pie_chart(df_earnings_grouped, "Transaction Kind", "Native Amount", "earnings-pie", "Earnings")


def map_transaction_type_to_title(transaction_type):
    if transaction_type == "referral_card_cashback":
        return "Card cashback"
    elif transaction_type == "mco_stake_reward":
        return "Stake rewards"
    elif transaction_type == "crypto_earn_interest_paid":
        return "Earn"
    elif transaction_type == "reimbursement":
        return "Reimbursement"
    elif transaction_type == "referral_gift":
        return "Referral Gift"
    else:
        return transaction_type


