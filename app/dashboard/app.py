from dash import Dash, html, dcc, Input, Output
import plotly.express as px
# import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import matplotlib
import plotly.express as px

matplotlib.use('agg')

import matplotlib.pyplot as plt

car_list = pd.read_csv('./data/car_list.csv')
detected_flaws = pd.read_csv('./data/detected_flaws.csv', index_col='index')
flaw_cause = pd.read_csv('./data/flaw_cause.csv')

explained_detected_flaws = detected_flaws.merge(flaw_cause, how='left', on='flaw_type')
complete_df = explained_detected_flaws.merge(car_list, how='left', on='car_id')

complete_df['arrived_at'] = pd.to_datetime(complete_df['arrived_at'], dayfirst=True)

data = complete_df.sort_values(by='arrived_at')

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.DropdownMenu(
                label="Color Filters",
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": color, "value": color}
                            for color in data['color'].unique()
                        ],
                        value=[],
                        id="color-checkboxes",
                        inline=True
                    )
                ],
                toggle_style={"width": "100%"}
            ),
        ]),
        dbc.Col([
            dbc.DropdownMenu(
                label="Week Filters",
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": str(week), "value": week}
                            for week in sorted(data['week'].unique())
                        ],
                        value=[],
                        id="week-checkboxes",
                        inline=True
                    )
                ],
                toggle_style={"width": "100%"}
            ),
        ]),
        dbc.Col([
            dbc.DropdownMenu(
                label="Model Filters",
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": model, "value": model}
                            for model in data['model'].unique()
                        ],
                        value=[],
                        id="model-checkboxes",
                        inline=True
                    )
                ],
                toggle_style={"width": "100%"}
            ),
        ]),
        dbc.Col([
            dcc.DatePickerRange(
                id='date-picker',
                start_date=data['arrived_at'].min(),
                end_date=data['arrived_at'].max(),
                display_format='YYYY-MM-DD'
            ),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='flaws-per-week'),
            dcc.Graph(id='items-by-day'),
            dcc.Graph(id='flaws-by-color'),
            dcc.Graph(id='flaws-by-model'),
            dcc.Graph(id='flaws-by-cause'),
            dcc.Graph(id='flaws-by-type'),
        ])
    ])
])

@app.callback(
    [
        Output("flaws-per-week", "figure"),
        Output("items-by-day", "figure"),
        Output("flaws-by-color", "figure"),
        Output("flaws-by-model", "figure"),
        Output("flaws-by-cause", "figure"),
        Output("flaws-by-type", "figure")
    ],
    [
        Input("color-checkboxes", "value"),
        Input("week-checkboxes", "value"),
        Input("model-checkboxes", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date")
    ]
)
def update_plots(selected_colors, selected_weeks, selected_models, start_date, end_date):
    filtered_df = data

    if selected_colors:
        filtered_df = filtered_df[filtered_df['color'].isin(selected_colors)]

    if selected_weeks:
        filtered_df = filtered_df[filtered_df['week'].isin(selected_weeks)]

    if selected_models:
        filtered_df = filtered_df[filtered_df['model'].isin(selected_models)]

    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['arrived_at'] >= start_date) & (filtered_df['arrived_at'] <= end_date)
        ]

    # Plot: Amount of flaws per week (horizontal bar chart)
    flaws_per_week = px.bar(
        filtered_df.groupby('week').size().reset_index(name='flaws'),
        x='flaws',
        y='week',
        orientation='h',
        title='Amount of Flaws per Week'
    )

    # Plot: Items by day and amount of flaws in the same day (line chart)
    items_by_day = px.line(
        filtered_df.groupby('arrived_at').size().reset_index(name='flaws'),
        x='arrived_at',
        y='flaws',
        title='Items by Day and Amount of Flaws'
    )

    # Plot: Flaws by color (horizontal bar chart)
    flaws_by_color = px.bar(
        filtered_df.groupby('color').size().reset_index(name='flaws'),
        x='flaws',
        y='color',
        orientation='h',
        title='Flaws by Color'
    )

    # Plot: Flaws by model (horizontal bar chart)
    flaws_by_model = px.bar(
        filtered_df.groupby('model').size().reset_index(name='flaws'),
        x='flaws',
        y='model',
        orientation='h',
        title='Flaws by Model'
    )

    # Plot: Flaws by cause (horizontal bar chart)
    flaws_by_cause = px.bar(
        filtered_df.groupby('cause').size().reset_index(name='flaws'),
        x='flaws',
        y='cause',
        orientation='h',
        title='Flaws by Cause'
    )

    # Plot: Amount of flaws by flaw type (horizontal bar chart)
    flaws_by_type = px.bar(
        filtered_df.groupby('flaw_type').size().reset_index(name='flaws'),
        x='flaws',
        y='flaw_type',
        orientation='h',
        title='Flaws by Type'
    )

    return flaws_per_week, items_by_day, flaws_by_color, flaws_by_model, flaws_by_cause, flaws_by_type

if __name__ == "__main__":
    app.run_server(debug=True)