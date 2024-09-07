from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import base64
import json


car_list = pd.read_csv('./data/car_list.csv')
detected_flaws = pd.read_csv('./data/detected_flaws.csv', index_col='index')
flaw_cause = pd.read_csv('./data/flaw_cause.csv')

explained_detected_flaws = detected_flaws.merge(flaw_cause, how='left', on='flaw_type')
complete_df = explained_detected_flaws.merge(car_list, how='left', on='car_id')

complete_df['arrived_at'] = pd.to_datetime(complete_df['arrived_at'], dayfirst=True)

data = complete_df.sort_values(by='arrived_at')

def create_flaw_diagram(filtered_df, filename):
    img_path = '../data_visualization/crop_diagram_data.png'
    annotation_path = '../data_visualization/crop_diagram_data.json'
    img = Image.open(img_path)
    with open(annotation_path, 'r') as f:
        annotations = json.load(f)

    draw = ImageDraw.Draw(img, 'RGBA')
    flaw_data = filtered_df.groupby('roi')['flaw_type'].count()
    max_flaws = max(flaw_data) if not flaw_data.empty else 1

    def get_color(flaw_count):
        color_ratio = 255 / max_flaws
        color_intensity = int(min(flaw_count * color_ratio, 255))
        return (99, 110, 250, color_intensity)

    def get_centroid(polygon):
        x_coords = [p[0] for p in polygon]
        y_coords = [p[1] for p in polygon]
        centroid_x = sum(x_coords) / len(polygon)
        centroid_y = sum(y_coords) / len(polygon)
        return (centroid_x, centroid_y)

    font = ImageFont.load_default(size=20)

    for shape in annotations['shapes']:
        part_name = shape['label']
        if part_name in flaw_data:
            polygon = [(x, y) for x, y in shape['points']]
            color = get_color(flaw_data[part_name])
            draw.polygon(polygon, fill=color)
            centroid = get_centroid(polygon)
            draw.text(centroid, str(flaw_data[part_name]), fill='black', font=font)

    img_array = np.array(img)
    fig = px.imshow(img_array, title='Amount of Flaws per Car Part')

    fig.update_layout(
        title='Amount of Flaws per Car Part',
        title_y=0.91,
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
        plot_bgcolor='white',
        paper_bgcolor='white',
    )

    return dcc.Graph(
            figure=fig,
            config={'displayModeBar': True}
        )

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.H1('Flaws Dashboard')
            ]),
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
                            inline=True
                        )
                    ],
                    toggle_style={"width": "100%"}
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
                            inline=True
                        )
                    ],
                    toggle_style={"width": "100%"}
                ),
            ], className='pt-4'),
            dbc.Row([
                dcc.DatePickerRange(
                    id='date-picker',
                    start_date=data['arrived_at'].min(),
                    end_date=data['arrived_at'].max(),
                    display_format='YYYY-MM-DD'
                ),
            ], className='pt-4'),
            dbc.Row([
                dbc.Button(
                    'Clean Filters', id='clean-filter-btn', n_clicks=0
                )
            ], className='pt-4')
        ], width=2, className='pt-4'),
        dbc.Col([
            dcc.Graph(id='flaws-by-cause'),
            dcc.Graph(id='flaws-by-color'),
        ], width=5),
        dbc.Col([
            html.Div(id='flaw-diagram'),
            dcc.Graph(id='flaws-by-type'),
        ], width=5),
    ])
], className='mx-0 my-0', fluid=True)

@app.callback(
    [
        Output("flaws-by-color", "figure"),
        Output("flaws-by-cause", "figure"),
        Output("flaws-by-type", "figure"),
        Output("flaw-diagram", 'children'),
        Output('clean-filter-btn', 'n_clicks')
    ],
    [
        Input("color-checkboxes", "value"),
        Input("model-checkboxes", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input('flaws-by-cause', 'clickData'),
        Input('flaws-by-color', 'clickData'),
        Input('flaws-by-type', 'clickData'),
        Input('clean-filter-btn', 'n_clicks')
    ]
)
def update_plots(selected_colors, selected_models, start_date, end_date, click_cause, click_color, click_type, clean_filter):
    filtered_df = data
    if selected_colors and clean_filter == 0:
        filtered_df = filtered_df[filtered_df['color'].isin(selected_colors)]

    if selected_models and clean_filter == 0:
        filtered_df = filtered_df[filtered_df['model'].isin(selected_models)]

    if start_date and end_date and clean_filter == 0:
        filtered_df = filtered_df[
            (filtered_df['arrived_at'] >= start_date) & (filtered_df['arrived_at'] <= end_date)
        ]
    
    if click_cause and clean_filter == 0:
        print(click_cause)
        label = [click_cause['points'][0]['label']]
        filtered_df = filtered_df[filtered_df['cause'].isin(label)]

    if click_color and clean_filter == 0:
        label = [click_color['points'][0]['label']]
        filtered_df = filtered_df[filtered_df['color'].isin(label)]
    
    if click_type and clean_filter == 0:
        label = [click_type['points'][0]['label']]
        filtered_df = filtered_df[filtered_df['flaw_type'].isin(label)]
    
    n_clicks = 0

    # Plot: Flaws by color (horizontal bar chart)
    flaws_by_color = px.bar(
        filtered_df.groupby('color').size().reset_index(name='flaws'),
        x='flaws',
        y='color',
        orientation='h',
        title='Flaws by Color'
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
    ).update_yaxes(autorange='reversed')

    diagram_chart = create_flaw_diagram(filtered_df, 'lala')

    return flaws_by_color, flaws_by_cause, flaws_by_type, diagram_chart, n_clicks

if __name__ == "__main__":
    app.run_server(debug=True)