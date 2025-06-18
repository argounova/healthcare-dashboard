# Imports
import dash
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html
import pandas as pd
import plotly.express as px


# Data Loading Function
def load_data():
    data = pd.read_csv('assets/healthcare.csv')
    data['Billing Amount'] = pd.to_numeric(data['Billing Amount'], errors='coerce')
    data['Date of Admission'] = pd.to_datetime(data['Date of Admission'], errors='coerce')
    data['YearMonth'] = data['Date of Admission'].dt.to_period('M')
    return data

data = load_data()

num_records = len(data)
avg_billing_amount = data['Billing Amount'].mean()


# App Initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App Layout and Design 
app.layout = dbc.Container([
  dbc.Row([
    dbc.Col([html.H1("Healthcare Dashboard")], width=12, className="text-center mb-4")
  ]),

  # Hospital Statistics Section
  dbc.Row([
    dbc.Col([
      html.Div(f"Total Records: {num_records}", className="text-center my-3 top-text")],
      width=5),
    dbc.Col([
      html.Div(f"Average Biling Amount: {avg_billing_amount:.2f}", className="text-center my-3 top-text")],
      width=5),
  ], className="mb-5"),

  # Male or Female Demographics
  dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4("Patient Demographics", className="card-title"),
                dcc.Dropdown(
                    id='gender-filter',
                    options=[{"label" : gender, "value" : gender} for gender in data['Gender'].unique()],
                    value=None,
                    placeholder="Select a Gender",
                ),
                dcc.Graph(id='age-distribution')
            ])
        ])
    ], width=6),

    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4("Medical Condition Distribution", className="card-title"),
                dcc.Graph(id='condition-distribution')
            ])
        ])
    ], width=6)
  ]),

  # Insurance Provider Section
  dbc.Row([
      dbc.Col([
          dbc.Card([
              dbc.CardBody([
                  html.H4("Insurance Provider Comparison", className="card-title"),
                  dcc.Graph(id='insurance-comparison')
              ])
          ])
      ], width=12),
  ]),

  # Billing Distribution Section
  dbc.Row([
      dbc.Col([
          dbc.Card([
              dbc.CardBody([
                html.H4("Billing Amount Distribution", className="card-title"),
                dcc.Slider(
                    id='billing-slider',
                    min=data['Billing Amount'].min(),
                    max=data['Billing Amount'].max(),
                    value=data['Billing Amount'].median(),
                    marks={int(value) : f"${int(value):,}" for value in data['Billing Amount'].quantile([0, 0.25, 0.5, 0.75, 1]).values},
                    step=100
                ),
                dcc.Graph(id='billing-distribution')
              ])
          ])
      ], width=12)
  ]),

  # Trends in Admission Section
  dbc.Row([
      dbc.Col([
          dbc.Card([
              dbc.CardBody([
                html.H4("Trends in Admissions", className="card-title"),
                dcc.RadioItems(
                    id='chart-type',
                    options=[
                        {'label' : 'Line Chart', 'value' : 'line'},
                        {'label' : 'Bar Chart', 'value' : 'bar'}
                    ],
                    value='line',
                    inline=True,
                    className='mb-4'
                ),
                dcc.Dropdown(
                    id='condition-filter',
                    options=[{ 'label' : condition, 'value' : condition } for condition in data['Medical Condition'].unique()],
                    value=None,
                    placeholder='Select a Medical Condition'
                ),
                dcc.Graph(
                    id='admission-trends',
                    
                )
              ])
          ])
      ], width=12)
  ])
], fluid=True)


## Create Callbacks

# Male or Female Demographics
@app.callback(
    Output('age-distribution', 'figure'),
    Input('gender-filter', 'value')
)
def update_distribution(selected_gender):
    if selected_gender:
        filtered_df = data[data['Gender'] == selected_gender]
    else:
        filtered_df = data

    if filtered_df.empty:
        return{}
    
    fig = px.histogram(
        filtered_df,
        x='Age',
        nbins=10,
        color='Gender',
        title='Age Distribution by Gender',
        color_discrete_sequence=['#636efa', '#ef553b']
    )

    return fig

# Medical Condition Distribution
@app.callback(
    Output('condition-distribution', 'figure'),
    Input('gender-filter', 'value')
)
def update_medical_condition(selected_gender):
    filtered_df = data[data['Gender'] == selected_gender] if selected_gender else data
    fig = px.pie(filtered_df, names='Medical Condition', title='Medical Condition Distribution')
    return fig

# Insurance Provider Comparison
@app.callback(
    Output('insurance-comparison', 'figure'),
    Input('gender-filter', 'value')
)
def update_insurance(selected_gender):
    filtered_df = data[data['Gender'] == selected_gender] if selected_gender else data
    fig = px.bar(
        filtered_df, x='Insurance Provider', y='Billing Amount', color='Medical Condition',
        barmode='group',
        title='Insurance Provider Price Comparison',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    return fig

# Billing Distribution
@app.callback(
    Output('billing-distribution', 'figure'),
    [Input('gender-filter', 'value'),
     Input('billing-slider', 'value')]
)
def update_billing(selected_gender, slider_value):
    filtered_df = data[data['Gender'] == selected_gender] if selected_gender else data
    filtered_df = filtered_df[filtered_df['Billing Amount'] <= slider_value]
    fig = px.histogram(filtered_df, x='Billing Amount', nbins=10, title='Billing Amount Distribution')
    return fig

#Trends in Admission
@app.callback(
    Output('admission-trends', 'figure'),
    [Input('chart-type', 'value'),
     Input('condition-filter', 'value')]
)
def update_admission(chart_type, selected_condition):
    filtered_df = data[data['Medical Condition'] == selected_condition] if selected_condition else data
    trend_df = filtered_df.groupby('YearMonth').size().reset_index(name='Count')
    trend_df['YearMonth'] = trend_df['YearMonth'].astype(str)
    if chart_type == 'line':
        fig = px.line(trend_df, x='YearMonth', y='Count', title='Admission Trends Over Time')
    else:
        fig = px.bar(trend_df, x='YearMonth', y='Count', title='Admission Trends Over Time')
    return fig




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)