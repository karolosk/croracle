import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objs as go


def get_timeline_chart(df, x_axis_data, y_axis_data, timeline_name, native_currency):
    return dcc.Graph(
        id="purchases-timeline",
        figure={
            "data": [
                dict(
                    x=df[x_axis_data],
                    y=df[y_axis_data],
                    name=timeline_name,
                    marker=dict(color="rgb(177, 35, 5)"),
                ),
            ],
            "layout": {
                "title": f"{timeline_name.title()} Timeline ({native_currency})",
                "annotations": "annotations",
                "legend": {"x": 0, "y": 1.0},
            },
        },
    )


def get_bar_chart(df, x_axis_data, y_axis_data, title, name):
    return dcc.Graph(
        id=f"{name}-graph",
        figure={
            "data": [
                {
                    "x": df[x_axis_data],
                    "y": df[y_axis_data],
                    "type": "bar",
                },
            ],
            "layout": {
                "title": title,
                "annotations": "annotations",
            },
        },
    ),


def get_scatter_plot(df, x_axis_data, y_axis_data, color, size, name):
    return dcc.Graph(
        className="row-content",
        id=f"{name}-timeline-type",
        figure=get_scatter_plot_image(df, x_axis_data, y_axis_data, color, size)
    ),


def get_scatter_plot_image(df, x_axis_data, y_axis_data, color, size):
    if df.empty:
        return px.scatter()
    else:
        return px.scatter(data_frame=df,
                          x=df[x_axis_data],
                          y=df[y_axis_data],
                          color=df[color],
                          size=df[size], )


def get_pie_chart(df, labels, values, name, title):
    return dcc.Graph(
        className="row-content",
        id=f"{name}-graph",
        style={"display": "inline-block", "width": "100%"},
        figure=go.Figure(
            data=[
                go.Pie(
                    labels=df[labels],
                    values=df[values],
                    hole=.3
                )
            ],
            layout=go.Layout(title=title),
        ),
    ),