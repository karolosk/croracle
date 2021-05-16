import base64
import io
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State

import settings
from services.stats_service import get_stats
from errors.messages import file_format_error

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.index_string = settings.INDEX_GA_STRING

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(html.Div(
                className="app-header",
                children=[
                    html.P("Croracle", className="title"),
                    html.P("CDC Export Visualization", className="subtitle"),
                ],
            ))
        ),
        dbc.Row(
            dbc.Col(dcc.Upload(
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
            ))),
        dcc.Loading(
            id="loader",
            type="circle",
            fullscreen=True,
            children=html.Div(id="output-data-upload")
        ),
    ],
    fluid=True
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        else:
            return dbc.Container(html.Div(
                [
                    dbc.Row(
                        dbc.Col([
                            dbc.Alert([
                                html.H4("Wrong file format.", className="alert-heading"),
                                html.P("Only CSV files are allowed at the moment."),
                                html.Hr(),
                                html.P("Please make sure that the file you are using has csv extension.",
                                       className="mb-0"),

                            ],
                                dismissable=True,
                                color="danger"
                            )
                        ],
                            width={"size": 6, "offset": 3}
                        ))
                ]
            )
            )
    except Exception as e:
        return dbc.Container(html.Div(
            [
                dbc.Row(dbc.Alert([
                    html.H4("An error has occured", className="alert-heading"),
                    html.P("There is no descriptive info for this eror"),
                    html.Hr(),
                    html.P("Please contact us and mention the below:", className="mb-0"),
                    html.P(f"Error message: {str(e)}"),
                    html.P(f"Error class: {type(e)}")
                ],
                    dismissable=True,
                    color="danger")
                )
            ]
        )
        )

    try:
        stats = get_stats(df)
    except Exception as e:
        print(str(e))
        return dbc.Container(html.Div(
            [
                dbc.Row(dbc.Alert([
                    html.H4("There was an error processing the file", className="alert-heading"),
                    html.P(file_format_error),
                    html.Hr(),
                    html.P("If everything of those are ok please contact us and mention the below:", className="mb-0"),
                    html.P(f"Error message: {str(e)}"),
                    html.P(f"Error class: {type(e)}")
                ],
                    dismissable=True,
                    color="danger")
                )
            ]
        ))

    return dbc.Container(html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(stats.get('total_purchases')),
                    dbc.Col(stats.get('total_earnings')),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Hr()),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.H3("Breakdown Purchases", className="row-header"), ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(children=stats.get('purchase_graphs')), )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Hr()),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.H3("Breakdown Earnings", className="row-header"), ),
                ]
            ),
            dbc.Row(
                stats.get('earnings_break_down')
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(children=stats.get('earning_graphs')), )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Hr()),
                ]
            ),
        ]
    ),
        fluid=True
    )


@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    time.sleep(0.5)
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


if __name__ == "__main__":
    app.run_server(debug=True)
