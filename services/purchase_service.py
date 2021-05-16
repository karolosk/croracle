import dash_bootstrap_components as dbc
import dash_html_components as html

from services.graph_service import get_timeline_chart, get_scatter_plot, get_bar_chart


def get_total_purchase_stats(df_crypto_purchase, native_currency):
    df_crypto_purchase["Transaction Description"] = df_crypto_purchase["Transaction Description"].str.replace("Buy", "")
    df_crypto_purchase_grouped = df_crypto_purchase.groupby(["Transaction Kind"]).sum()

    if df_crypto_purchase.empty:
        native_amount = 0
        native_amount_usd = 0
    else:
        native_amount = round(float(df_crypto_purchase_grouped["Native Amount"]), 2)
        native_amount_usd = round(float(df_crypto_purchase_grouped["Native Amount (in USD)"]), 2)

    purchase_total_data = html.Div(
        [
            html.H5("Purchases"),
            html.P(
                children=[
                    html.Span(
                        native_amount,
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
                        native_amount_usd,
                        className="total-info-data",
                    ),
                    html.Span(f" USD", className="total-info-label"),
                ],
                className="total-info-data",
            ),
        ],
        className="total-info",
    )
    return purchase_total_data


def get_purchase_graphs(df_crypto_purchase, native_currency):
    if df_crypto_purchase.empty:
        return [
            html.Div([
                dbc.Row(
                    dbc.Col(
                        dbc.Alert(
                            [
                                html.H4("No purchases found.", className="alert-heading"),
                                html.P("Seems that there are not any crypto purchases in the file you uploaded."),
                                html.Hr(),
                                html.P("Records with Transaction: crypto_purchase are considered as purchase from Croracle.",className="mb-0"),
                            ],
                            color="info"
                        ),
                        width={"size": 6, "offset": 3},
                    )
                )
            ]
            )]

    df_crypto_purchase_grouped_type = df_crypto_purchase.groupby(["Transaction Kind", "Transaction Description"],
                                                                 as_index=False).sum()
    df_crypto_purchase_grouped_type["Transaction Description"] = df_crypto_purchase_grouped_type[
        "Transaction Description"].str.replace("Buy", "")
    df_crypto_purchase_grouped_type_date = (
        df_crypto_purchase.groupby(["YearMonth"], as_index=False).sum().sort_values(by="YearMonth"))

    timeline = get_timeline_chart(df_crypto_purchase_grouped_type_date, 'YearMonth', 'Native Amount', 'purchases',
                                  native_currency)
    purchases_bar_chart = get_bar_chart(df_crypto_purchase_grouped_type, "Transaction Description", "Native Amount",
                                        f"Purchases in {native_currency}", 'purchases')
    scatter_plot = get_scatter_plot(df_crypto_purchase, "Timestamp (UTC)", "Native Amount", "Transaction Description",
                                    "Native Amount", 'purchase')

    graphs = html.Div(
        children=[
            dbc.Row(
                children=[
                    dbc.Col(purchases_bar_chart, width=6),
                    dbc.Col(timeline, width=6)
                ],
            ),
            dbc.Row(
                children=[
                    dbc.Col(children=scatter_plot)
                ],
                no_gutters=True
            )
        ],
    )

    return graphs
