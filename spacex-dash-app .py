
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load the SpaceX dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Calculate payload limits
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()

app = Dash(__name__)

# Application layout
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard"),

    dcc.Dropdown(
        id="site-dropdown",
        options=[
            {"label": "All Sites", "value": "ALL"}
        ] + [
            {"label": site, "value": site}
            for site in sorted(
                spacex_df["Launch Site"].dropna().unique()
            )
        ],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    dcc.Graph(id="success-pie-chart"),

    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        marks={
            0: "0",
            2500: "2500",
            5000: "5000",
            7500: "7500",
            10000: "10000"
        },
        value=[
            max(0, min_payload),
            min(10000, max_payload)
        ],
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    dcc.Graph(id="success-payload-scatter-chart")
])


# Callback 1: Update the pie chart
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):

    if entered_site == "ALL":
        # Success launches grouped by launch site
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Success Launches by Site"
        )

    else:
        # Success and failure distribution for one site
        filtered_df = spacex_df[
            spacex_df["Launch Site"] == entered_site
        ]

        fig = px.pie(
            filtered_df,
            names="class",
            title=f"Success vs Failure Launches: {entered_site}"
        )

    return fig


# Callback 2: Update the scatter plot
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value")
)
def get_scatter_chart(entered_site, payload_range):

    low, high = payload_range

    # Filter by payload mass
    filtered_df = spacex_df[
        spacex_df["Payload Mass (kg)"].between(low, high)
    ]

    # Filter by launch site if a specific site is selected
    if entered_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title="Launch Success vs Payload Mass",
        labels={
            "Payload Mass (kg)": "Payload Mass (kg)",
            "class": "Launch Outcome",
            "Booster Version Category": "Booster Version"
        }
    )

    return fig
    
app.run(debug=False, port=8051)
