from dash import Dash, html, dcc, Input, Output
from dash.dependencies import State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import base64
import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# load dfs and annotation data
car_list = pd.read_csv('./data/car_list.csv')
detected_flaws = pd.read_csv('./data/detected_flaws.csv', index_col='index')
flaw_cause = pd.read_csv('./data/flaw_cause.csv')
annotation_path = './data/crop_diagram_data.json'
with open(annotation_path, 'r') as f:
    annotations = json.load(f)

# configure final dfs
explained_detected_flaws = detected_flaws.merge(flaw_cause, how='left', on='flaw_type')
complete_df = explained_detected_flaws.merge(car_list, how='left', on='car_id')
complete_df['arrived_at'] = pd.to_datetime(complete_df['arrived_at'], dayfirst=True)
data = complete_df.sort_values(by='arrived_at')

# set global variables
primary_text_color = '#000000'
secondary_text_color = 'rgba(0, 0, 0, 0.65)'

# create the main diagram on the dashboard
def create_flaw_diagram(filtered_df, filename):
    img_path = './assets/crop_diagram_data.png'
    img = Image.open(img_path)

    draw = ImageDraw.Draw(img, 'RGBA')
    flaw_data = filtered_df.groupby('roi')['flaw_type'].count()
    max_flaws = max(flaw_data) if not flaw_data.empty else 1

    def get_color(flaw_count):
        color_ratio = 255 / max_flaws
        color_intensity = int(min(flaw_count * color_ratio, 255))
        return (55, 90, 127, color_intensity)

    def get_centroid(polygon):
        x_coords = [p[0] for p in polygon]
        y_coords = [p[1] for p in polygon]
        centroid_x = sum(x_coords) / len(polygon)
        centroid_y = sum(y_coords) / len(polygon) - 15
        return (centroid_x, centroid_y)

    font = ImageFont.load_default(size=20)

    for shape in annotations['shapes']:
        part_name = shape['label']
        if part_name in flaw_data:
            polygon = [(x, y) for x, y in shape['points']]
            color = get_color(flaw_data[part_name])
            draw.polygon(polygon, fill=color)
            centroid = get_centroid(polygon)
            draw.text(centroid, str(flaw_data[part_name]), fill='white', font=font, stroke_width=2, stroke_fill='black')

    img_array = np.array(img)
    fig = px.imshow(img_array, title='Amount of Flaws per Car Part')

    fig.update_layout(
        title='Amount of Flaws per Car Part',
        title_y=0.97,
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor='y',
            scaleratio=1
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot background
        title_font=dict(color=primary_text_color, size=24), # White title font
    )

    return dcc.Graph(
            figure=fig,
            config={'displayModeBar': False},
            id='inner_diagram'
        )

def find_polygon(x, y):
    point = Point(x, y)
    for shape in annotations['shapes']:
        polygon = Polygon(shape['points'])
        if polygon.contains(point):
            return shape['label']
    return

def generate_plots(data):
    flaws_by_color = px.bar(
        data.groupby('color').size().reset_index(name='flaws'),
        x='flaws',
        y='color',
        orientation='h',
        text_auto=True,
        color_discrete_sequence=['#375A7F']
    ).update_layout(
        title='Flaws by Color',
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot background
        font=dict(color=primary_text_color),       # White font color
        title_font=dict(color=primary_text_color, size=24), # White title font
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=None),
    ).update_traces(
        marker=dict(
            line=dict(
                color='black',
                width=1
            )
        )
    )

    flaws_by_cause = px.bar(
        data.groupby('cause').size().reset_index(name='flaws'),
        x='flaws',
        y='cause',
        orientation='h',
        text_auto=True,
        color_discrete_sequence=['#375A7F']
    ).update_layout(
        title='Flaws by Cause',
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot background
        font=dict(color=primary_text_color),       # White font color
        title_font=dict(color=primary_text_color, size=24), # White title font
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=None),
    ).update_traces(
        marker=dict(
            line=dict(
                color='black',
                width=1
            )
        )
    )

    flaws_by_type = px.bar(
        data.groupby('flaw_type').size().reset_index(name='flaws'),
        x='flaws',
        y='flaw_type',
        orientation='h',
        text_auto=True,
        color_discrete_sequence=['#375A7F'],
    ).update_layout(
        title='Flaws by Type',
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot background
        font=dict(color=primary_text_color),       # White font color
        title_font=dict(color=primary_text_color, size=24), # White title font
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=None), 
        yaxis=dict(autorange='reversed'),
    ).update_traces(
        marker=dict(
            line=dict(
                color='black',
                width=1
            )
        )
    )

    flaws_by_date = px.line(
        data.groupby('arrived_at').size().reset_index(name='flaws'),
        x='arrived_at',
        y='flaws',
        color_discrete_sequence=['#375A7F'],
    ).update_layout(
        title='Flaws by Time',
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot background
        font=dict(color=primary_text_color),       # White font color
        title_font=dict(color=primary_text_color, size=24), # White title font
        xaxis=dict(showgrid=False, title=None),
        height=490
    )

    diagram_chart = create_flaw_diagram(data, 'lala')
    
    return flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, flaws_by_date


app = Dash(external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            html.H1('Flaws Dashboard', className='fs-1 text-black px-0 font-weight-bold')
                        ], className='px-0'),
                        dbc.Row([
                            html.P('Explore the most common paint-shop flaws amongst 19 car parts. Every graph is interactive and the data is collected from pen and paper sheets (with the help of an OCR) filled by the operators during the production line.', className='px-0 my-0')
                        ], className='px-0'),
                        dbc.Row([
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
                                        inline=True,
                                        className='px-2'
                                    )
                                ],
                                color='secondary'
                            ),
                        ], className='pt-4'),
                        dbc.Row([
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
                                        inline=True,
                                        className='px-2'
                                    ),
                                ],
                                color='secondary'
                            ),
                        ], className='pt-4'),
                        dbc.Row([
                            dcc.DatePickerRange(
                                id='date-picker',
                                start_date=data['arrived_at'].min(),
                                end_date=data['arrived_at'].max(),
                                display_format='YYYY-MM-DD',
                                className='bg-light w-100 px-0 date-picker-container',
                                style={'width': '402.867'}
                            ),
                        ], className='pt-4' ),
                        dbc.Row([
                            dbc.Button(
                                'Clean Filters', id='clean-filter-btn', n_clicks=0, className='btn btn-danger mt-auto'
                            )
                        ], className='pt-4')
                    ], width=12),
                ])
            ], width=3, className='pt-4 bg-light px-0 d-flex flex-column'),
            dbc.Col([
                html.Div(id='flaw-diagram'),
            ], width=5, className='pt-4'),
            dbc.Col([
                dcc.Graph(id='flaws-by-date')
            ], width=4, className='pt-4')
        ], className='px-0 py-0'),
        dbc.Row([
            dbc.Col([   
                dcc.Graph(id='flaws-by-cause'),
            ], width=4),
            dbc.Col([
                dcc.Graph(id='flaws-by-color'),
            ], width=4),
            dbc.Col([
                dcc.Graph(id='flaws-by-type'),
            ], width=4)
        ], className='px-0 py-0'),
    ]),
    dcc.Interval(
        id='load_interval',
        n_intervals=0,
        max_intervals=0,
        interval=1
    )
], className='mx-0 my-0 px-0 py-0 bg-light', fluid=True)

@app.callback(
    [   
        Output("flaws-by-color", "figure"),
        Output("flaws-by-cause", "figure"),
        Output("flaws-by-type", "figure"),
        Output("flaw-diagram", 'children'),
        Output("flaws-by-date", "figure")
    ],
    [
        Input('load_interval', 'n_intervals')
    ],
    prevent_initial_call=False
)
def init_dash(click):
    flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, flaws_by_date = generate_plots(data)
    return flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, flaws_by_date

@app.callback(
    [
        Output("flaws-by-color", "figure", allow_duplicate=True),
        Output("flaws-by-cause", "figure", allow_duplicate=True),
        Output("flaws-by-type", "figure", allow_duplicate=True),
        Output("flaw-diagram", 'children', allow_duplicate=True),
        Output('clean-filter-btn', 'n_clicks'),
        Output('flaws-by-date', 'figure', allow_duplicate=True),
        Output('flaws-by-cause', 'clickData'),
        Output('flaws-by-color', 'clickData'),
        Output('flaws-by-type', 'clickData'),
        Output('inner_diagram', 'clickData'),
        Output('flaws-by-date', 'clickData')
    ],
    [
        Input("color-checkboxes", "value"),
        Input("model-checkboxes", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input('flaws-by-cause', 'clickData'),
        Input('flaws-by-color', 'clickData'),
        Input('flaws-by-type', 'clickData'),
        Input('inner_diagram', 'clickData'),
        Input('clean-filter-btn', 'n_clicks'),
        Input('flaws-by-date', 'clickData')
    ],
    prevent_initial_call=True
)
def update_plots(selected_colors, selected_models, start_date, end_date, click_cause, click_color, click_type, click_diagram, clean_filter, click_flaw_date):
    filtered_df = data.copy()

    n_clicks = 0
    if clean_filter:
        flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, flaws_by_time = generate_plots(filtered_df)

        return flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, n_clicks, flaws_by_time, None, None, None, None, None

    if selected_colors:
        filtered_df = filtered_df[filtered_df['color'].isin(selected_colors)]
    if selected_models:
        filtered_df = filtered_df[filtered_df['model'].isin(selected_models)]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['arrived_at'] >= start_date) & (filtered_df['arrived_at'] <= end_date)]
    if click_cause:
        label = [click_cause['points'][0]['label']]
        filtered_df = filtered_df[filtered_df['cause'].isin(label)]
    if click_color:
        label = [click_color['points'][0]['label']]
        filtered_df = filtered_df[filtered_df['color'].isin(label)]
    if click_type:
        label = [click_type['points'][0]['label']]
        filtered_df = filtered_df[filtered_df['flaw_type'].isin(label)]
    if click_diagram:
        x = click_diagram['points'][0]['x']
        y = click_diagram['points'][0]['y']
        label = find_polygon(x, y)
        if label:
            filtered_df = filtered_df[filtered_df['roi'].isin([label])]
    

    flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, flaws_by_time = generate_plots(filtered_df)

    return flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, n_clicks, flaws_by_time, click_cause, click_color, click_type, click_diagram, click_flaw_date

if __name__ == "__main__":
    app.run_server(debug=True)