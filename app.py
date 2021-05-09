import base64
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-6V70GQL792"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-6V70GQL792');
        </script>
        {%metas%}
        <title>Croracle</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

app.layout = html.Div(
    [
        html.Div(
            className="app-header",
            children=[
                html.P("Croracle", className="title"),
                html.P("CDC Export Visualization", className="subtitle"),
            ],
        ),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select File")]),
            style={
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.Div(id="output-data-upload"),
    ]
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        else:
            return html.Div(["Only CSV files are supported at the moment."])
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    # Manipulating Dates
    df["Timestamp (UTC)"] = pd.to_datetime(df["Timestamp (UTC)"]).apply(
        lambda x: x.date()
    )
    df["YearMonth"] = (
            df["Timestamp (UTC)"] + pd.offsets.MonthEnd(-1) + pd.offsets.Day(1)
    )
    # EARN
    df_earn = df[(df["Transaction Kind"] == "crypto_earn_interest_paid")]
    if df_earn.empty:
        data = {'Native Amount': [0], 'Native Amount (in USD)': [0]}
        df_earn_grouped = pd.DataFrame(data, columns=['Native Amount', 'Native Amount (in USD)'])
    else:
        df_earn_grouped = df_earn.groupby("Transaction Kind").sum()

    df_reimbursement = df[(df["Transaction Kind"] == "reimbursement")]
    if df_reimbursement.empty:
        data = {'Native Amount': [0], 'Native Amount (in USD)': [0]}
        df_reimbursement_grouped = pd.DataFrame(data, columns=['Native Amount', 'Native Amount (in USD)'])
    else:
        df_reimbursement_grouped = df_reimbursement.groupby(["Transaction Kind"]).sum()

    df_stake = df[(df["Transaction Kind"] == "mco_stake_reward")]
    if df_stake.empty:
        data = {'Native Amount': [0], 'Native Amount (in USD)': [0]}
        df_stake_grouped = pd.DataFrame(data, columns=['Native Amount', 'Native Amount (in USD)'])
    else:
        df_stake_grouped = df_stake.groupby(
            ["Transaction Kind", "Transaction Description"]
        ).sum()

    df_referral_card_cashback = df[(df["Transaction Kind"] == "referral_card_cashback")]
    if df_referral_card_cashback.empty:
        data = {'Native Amount': [0], 'Native Amount (in USD)': [0]}
        df_referral_card_cashback_grouped = pd.DataFrame(data, columns=['Native Amount', 'Native Amount (in USD)'])
    else:
        df_referral_card_cashback_grouped = df_referral_card_cashback.groupby(
            ["Transaction Kind", "Transaction Description"]
        ).sum()

    # referral gift
    df_referral_gift = df[(df["Transaction Kind"] == "referral_gift")]
    if df_referral_gift.empty:
        data = {'Native Amount': [0], 'Native Amount (in USD)': [0]}
        df_referral_gift_grouped = pd.DataFrame(data, columns=['Native Amount', 'Native Amount (in USD)'])
    else:
        df_referral_gift_grouped = df_referral_gift.groupby(
            ["Transaction Kind", "Transaction Description"]
        ).sum()

    # Earnings
    df_earnings = pd.concat(
        [
            df_referral_card_cashback,
            df_reimbursement,
            df_earn,
            df_referral_gift,
            df_stake,
        ]
    )
    df_earnings_grouped = df_earnings.groupby(
        ["Transaction Kind"], as_index=False
    ).sum()
    df_earnings_grouped = df_earnings_grouped.replace(
        ["crypto_earn_interest_paid"], "earn"
    )
    df_earnings_grouped = df_earnings_grouped.replace(
        ["mco_stake_reward"], "stake rewards"
    )
    df_earnings_grouped = df_earnings_grouped.replace(
        ["referral_card_cashback"], "card cashback"
    )
    df_earnings_grouped = df_earnings_grouped.replace(
        ["referral_gift"], "referral gift"
    )

    # purchase
    df_crypto_purchase = df[(df["Transaction Kind"] == "crypto_purchase")]
    df_crypto_purchase["Transaction Description"] = df_crypto_purchase[
        "Transaction Description"
    ].str.replace("Buy", "")
    df_crypto_purchase_grouped_type = df_crypto_purchase.groupby(
        ["Transaction Kind", "Transaction Description"], as_index=False
    ).sum()
    df_crypto_purchase_grouped_type[
        "Transaction Description"
    ] = df_crypto_purchase_grouped_type["Transaction Description"].str.replace(
        "Buy", ""
    )
    df_crypto_purchase_grouped = df_crypto_purchase.groupby(["Transaction Kind"]).sum()
    df_crypto_purchase_grouped_type_date = (
        df_crypto_purchase.groupby(["YearMonth"], as_index=False)
            .sum()
            .sort_values(by="YearMonth")
    )

    df_crypto_earnings_grouped_type_date = (
        df_earnings.groupby(["YearMonth"], as_index=False).sum().sort_values(by="YearMonth"))

    crypto_purchase_grouped_type_date_type_fig = px.scatter(data_frame=df_crypto_purchase,
                                                            x=df_crypto_purchase["Timestamp (UTC)"],
                                                            y=df_crypto_purchase[
                                                                "Native Amount"],
                                                            color=df_crypto_purchase[
                                                                "Transaction Description"],
                                                            size=df_crypto_purchase[
                                                                "Native Amount"], )

    crypto_purchase_grouped_type_date_type_fig.update_layout(
        title={
            'text': "Purchases Timestamp/Coin",
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    crypto_earnings_grouped_type_date_type_fig = px.scatter(data_frame=df_earnings,
                                                            x=df_earnings["Timestamp (UTC)"],
                                                            y=df_earnings[
                                                                "Native Amount"],
                                                            color=df_earnings[
                                                                "Transaction Description"],
                                                            size=df_earnings[
                                                                "Native Amount"], )

    crypto_earnings_grouped_type_date_type_fig.update_layout(
        title={
            'text': "Earnings Timestamp/Type",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    native_currency = df["Native Currency"][0]

    return html.Div(
        [
            html.Div(
                className="row-wrapper",
                children=[
                    html.Div(
                        [
                            html.H5("Purchases"),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(
                                                df_crypto_purchase_grouped[
                                                    "Native Amount"
                                                ]
                                            ),
                                            2,
                                        ),
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
                                        round(
                                            float(
                                                df_crypto_purchase_grouped[
                                                    "Native Amount (in USD)"
                                                ]
                                            ),
                                            2,
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(f" USD", className="total-info-label"),
                                ],
                                className="total-info-data",
                            ),
                        ],
                        className="total-info",
                    ),
                    html.Div(
                        [
                            html.H5("Earnings"),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(df_earnings["Native Amount"].sum()), 2
                                        ),
                                    ),
                                    html.Span(
                                        f" {native_currency}",
                                        className="total-info-label",
                                    ),
                                ],
                                className="total-info-data",
                            ),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(
                                                df_earnings[
                                                    "Native Amount (in USD)"
                                                ].sum()
                                            ),
                                            2,
                                        ),
                                    ),
                                    html.Span(f" USD", className="total-info-label"),
                                ],
                                className="total-info-data",
                            ),
                        ],
                        className="total-info",
                    ),
                ],
            ),
            html.Hr(),
            html.H3("Breakdown Purchases", className="row-header"),
            html.Div(
                className="row-wrapper",
                children=[
                    dcc.Graph(
                        className="row-content",
                        id="purchases-graph",
                        figure={
                            "data": [
                                {
                                    "x": df_crypto_purchase_grouped_type[
                                        "Transaction Description"
                                    ],
                                    "y": df_crypto_purchase_grouped_type[
                                        "Native Amount"
                                    ],
                                    "type": "bar",
                                },
                            ],
                            "layout": {
                                "title": f"Purchases in {native_currency}",
                                "annotations": "annotations",
                            },
                        },
                    ),
                    dcc.Graph(
                        className="row-content",
                        id="purchases-timeline",
                        figure={
                            "data": [
                                dict(
                                    x=df_crypto_purchase_grouped_type_date["YearMonth"],
                                    y=df_crypto_purchase_grouped_type_date[
                                        "Native Amount"
                                    ],
                                    name="Purchases",
                                    marker=dict(color="rgb(177, 35, 5)"),
                                ),
                            ],
                            "layout": {
                                "title": f"Purchases Timeline ({native_currency})",
                                "annotations": "annotations",
                                "legend": {"x": 0, "y": 1.0},
                            },
                        },
                    ),
                ],
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        className="row-content",
                        id="purchases-timeline-type",
                        figure=crypto_purchase_grouped_type_date_type_fig
                    ),
                ],
            ),
            html.Hr(),
            html.H3("Breakdown Earnings", className="row-header"),
            html.Div(
                className="row-wrapper-earn",
                children=[
                    html.Div(
                        className="total-info",
                        children=[
                            html.H5("Card cashback"),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(
                                                df_referral_card_cashback_grouped[
                                                    "Native Amount"
                                                ]
                                            ),
                                            2,
                                        ),
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
                                        round(
                                            float(
                                                df_referral_card_cashback_grouped[
                                                    "Native Amount (in USD)"
                                                ]
                                            ),
                                            2,
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(f" USD", className="total-info-label"),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="total-info",
                        children=[
                            html.H5("Stake rewards"),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(df_stake_grouped["Native Amount"]), 2
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(
                                        f" {native_currency}",
                                        className="total-info-label",
                                    ),
                                ]
                            ),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(
                                                df_stake_grouped[
                                                    "Native Amount (in USD)"
                                                ]
                                            ),
                                            2,
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(f" USD", className="total-info-label"),
                                ]
                            ),
                        ],
                    ),
                    html.Div(
                        className="total-info",
                        children=[
                            html.H5("Earn"),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(df_earn_grouped["Native Amount"]), 2
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(
                                        f" {native_currency}",
                                        className="total-info-label",
                                    ),
                                ]
                            ),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(
                                                df_earn_grouped[
                                                    "Native Amount (in USD)"
                                                ]
                                            ),
                                            2,
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(f" USD", className="total-info-label"),
                                ]
                            ),
                        ],
                    ),
                    html.Div(
                        className="total-info",
                        children=[
                            html.H5("Reimbursement"),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(
                                                df_reimbursement_grouped[
                                                    "Native Amount"
                                                ]
                                            ),
                                            2,
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(
                                        f" {native_currency}",
                                        className="total-info-label",
                                    ),
                                ]
                            ),
                            html.P(
                                [
                                    html.Span(
                                        round(
                                            float(
                                                df_reimbursement_grouped[
                                                    "Native Amount (in USD)"
                                                ]
                                            ),
                                            2,
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(f" USD", className="total-info-label"),
                                ]
                            ),
                        ],
                    ),

                    html.Div(
                        className="total-info",
                        children=[
                            html.H5("Referral Gift"),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(df_referral_gift_grouped["Native Amount"]), 2
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(
                                        f" {native_currency}",
                                        className="total-info-label",
                                    ),
                                ]

                            ),
                            html.P(
                                children=[
                                    html.Span(
                                        round(
                                            float(
                                                df_referral_gift_grouped[
                                                    "Native Amount (in USD)"
                                                ]
                                            ),
                                            2,
                                        ),
                                        className="total-info-data",
                                    ),
                                    html.Span(
                                        f" USD",
                                        className="total-info-label",
                                    ),
                                ]

                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="row-wrapper",
                children=[
                    dcc.Graph(
                        id="example-graph",
                        style={"display": "inline-block"},
                        figure=go.Figure(
                            data=[
                                go.Pie(
                                    labels=df_earnings_grouped[
                                        "Transaction Kind"
                                    ],
                                    values=df_earnings_grouped["Native Amount"],
                                )
                            ],
                            layout=go.Layout(title="Earnings"),
                        ),
                    ),
                    dcc.Graph(
                        className="row-content",
                        id="earnings-timeline",
                        figure={
                            "data": [
                                dict(
                                    x=df_crypto_earnings_grouped_type_date["YearMonth"],
                                    y=df_crypto_earnings_grouped_type_date[
                                        "Native Amount"
                                    ],
                                    name="Purchases",
                                    marker=dict(color="rgb(177, 35, 5)"),
                                ),
                            ],
                            "layout": {
                                "title": f"Earnings Timeline ({native_currency})",
                                "annotations": "annotations",
                                "legend": {"x": 0, "y": 1.0},
                            },
                        }, ),
                ],
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        className="row-content",
                        id="earnings-timeline-type",
                        figure=crypto_earnings_grouped_type_date_type_fig
                    ),
                ],
            ),
            html.Hr(),  # horizontal line
        ]
    )


@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


if __name__ == "__main__":
    app.run_server(debug=True)
