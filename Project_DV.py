import dash
from dash import dcc
from dash import html
from dash import Input, Output, State

import pandas as pd

import plotly.graph_objects as go

import os

cwd = os.getcwd()

df = pd.read_excel(cwd + '\\World_Energy_Generation_DV_Project.xlsx')

continents_list = list(df['continent'].unique())

gseven = ['Germany', 'Canada', 'United States','Japan','France','Italy','United Kingdom']

# The App itself
app = dash.Dash(__name__)

server = app.server

app.layout = html.Div((

    #Title
    html.Div([
        html.Div([
            html.Div([
                html.H1('WORLD ELECTRICITY GENERATION', style = {'margin-bottom': '0px', 'color': 'white'}),
                html.H4('quick look at electricity Generation around the world',
                        style = {'margin-top': '0px', 'color': 'white'}),
                html.H6('Original dataset by Our World in Data with modifications.',
                        style = {'margin-top': '0px', 'color': 'white'}),

            ]),

        ], className='six column', id = 'title')

    ], id='header', className = 'row flex-display', style = {'margin-bottom': '25px'}),

    #Year Range
    html.Div([
        html.Div([
            html.P('Select Year:', className = 'fix_label', style = {'color':'white', 'margin-left':'1%'}),
            dcc.RangeSlider(
                id='select_years',
                min=df['year'].min(),
                max=df['year'].max(),
                dots=True,
                value=[2001,2010],
                marks={str(year): str(year) for year in range(df['year'].min(), df['year'].max(), 4)}
            ),

        ], className = 'create_container twelve columns', style = {'width': '98%', 'margin-left': '1%'}),

    ], className = 'row flex-display'),

    #Dropdowns + Bar Plot + Line Plot
    html.Div([
        html.Div([
            html.P('Select Continent:', className = 'fix_label', style = {'color': 'white'}),
            dcc.Dropdown(
                id='continents',
                multi=False,
                clearable=True,
                disabled=False,
                style={'display':True},
                value='Europe',
                placeholder='Select Continent',
                options=[{'label': c, 'value': c} for c in continents_list],
                className = 'dcc_compon'
            ),

            html.P('Select Country:', className = 'fix_label', style = {'color': 'white'}),
            dcc.Dropdown(
                id='countries',
                multi=False,
                clearable=True,
                disabled=False,
                style={'display':True},
                value='Europe',
                placeholder='Select Countries',
                options=[],
                className='dcc_compon'
            )
        ], className = 'create_container three columns'),

        html.Div([
            dcc.Graph(
                id='bar_line_1',
                config={'displayModeBar': 'hover'}
            ),
        ], className = 'create_container six columns'),

        html.Div([
            dcc.Graph(
                id='pie',
                config={'displayModeBar': 'hover'}
            ),
        ], className = 'create_container three columns', style={'width':'44%'}),

    ], className = 'row flex-display', style={'display': 'flex'}),

    #Map
    html.Div([
        html.Div([
            dcc.Graph(
                id='map_1',
                config={'displayModeBar': 'hover'}
            ),
        ], className='create_container twelve columns'),

    ], className='row flex-display'),

    #HeatMap
    html.Div([
        html.Div([
            dcc.Graph(
                id='heat',
                config={'displayModeBar': 'hover'}
            ),
        ], className='create_container twelve columns'),

    ], className='row flex-display'),

), id='mainContainer', style={'display':'flex', 'flex-direction':'column'})

@app.callback(
    Output('countries', 'options'),
    Input('continents', 'value')
)
def get_countries_options(countries):
    df_c = df.loc[df['continent'] == countries]
    return [{'label': a, 'value': a} for a in df_c['country'].unique()]

@app.callback(
    Output('countries', 'value'),
    Input('countries', 'options')
)
def get_country_value(countries):
    return [c['value'] for c in countries][0]

#Combination bar 
@app.callback(
    Output('bar_line_1', 'figure'),
    [Input('continents', 'value')],
    [Input('countries', 'value')],
    [Input('select_years', 'value')]
)
def update_graph(continents, countries, select_years): 
    #Data for bar plot
    df_energy = df.groupby(by=['continent', 'country', 'year'])['renewables_electricity',
    'fossil_electricity'].sum().reset_index()
    df_energy_ = df_energy.loc[
        (df_energy['continent'] == continents) & 
        (df_energy['country'] == countries) & 
        (df_energy['year'] >= select_years[0]) &
        (df_energy['year'] < select_years[1])]
    
    return {
        'data': [
            go.Bar(
                x=df_energy_['year'],
                y=df_energy_['renewables_electricity'],
                text=df_energy_['renewables_electricity'].round(2),
                #texttemplate='%{text:.2}',
                textposition='auto',
                name='Renewable',
                marker=dict(color='#ffb703')
            ),

            go.Bar(
                x=df_energy_['year'],
                y=df_energy_['fossil_electricity'],
                text=df_energy_['fossil_electricity'].round(2),
                #texttemplate='%{text:.2}',
                textposition='auto',
                name='Fossil',
                marker=dict(color='#d62828')
            )

        ],
        'layout': go.Layout(
            barmode='stack',
            plot_bgcolor='#010915',
            paper_bgcolor='#010915',
            title={
                'text': 'Energy Generation by Country',
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 20
            },
            hovermode='x',
            xaxis=dict(
                title='Year',
                tick0=0,
                dtick=1,
                color='white',
                showline=True,
                showgrid=True,
                linewidth=2
            ),
            yaxis=dict(
                title='Energy (TWh)',
                color='white',
                showline=True,
                showgrid=True
            )
        )
    }

#Pie Chart
@app.callback(
    Output('pie', 'figure'),
    [Input('continents', 'value')],
    [Input('countries', 'value')],
    [Input('select_years', 'value')]
)
def display_content(continents, countries, select_years):
    df_f = df.groupby(by=['continent', 'country', 'year'])['pct_share'].mean().reset_index()
    df_f_ = df_f.loc[
        (df_f['continent'] == continents) & 
        (df_f['country'] == countries) & 
        (df_f['year'] >= select_years[0]) &
        (df_f['year'] < select_years[1])]
    
    return {
        'data': [
            go.Scatter(
                x = df_f_['year'],
                y=df_f_['pct_share'],
                mode='lines+markers',
                name='GDP',
                line=dict(shape='spline', smoothing=1.3, width=3, color='red'),
                marker=dict(size=10, symbol='circle', color='white', 
                            line=dict(color='#ff00ff', width=2)),
                hoverinfo='text',
                hovertext=''
            )
        ],
        'layout': go.Layout(
            plot_bgcolor='#010915',
            paper_bgcolor='#010915',
            hovermode='closest',
            title={
                'text': 'Share of Renewable Energy by Country',
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 20
            },
        xaxis = dict(
        title='Year',
        tick0=0,
        dtick=1,
        color='white',
        showline=True,
        showgrid=True,
        linewidth=2
    ),
        yaxis = dict(
        title='%',
        color='white',
        showline=True,
        showgrid=True
        ))
    }

@app.callback(
    Output('map_1', 'figure'),
    [Input('continents', 'value')],
    [Input('countries', 'value')],
    [Input('select_years', 'value')]
)
def update_graph(continents, countries, select_years):
    df_r = df.groupby(by=['continent', 'country', 'year', 'latitude', 'longitude'])['renewables_electricity',
    'fossil_electricity'].sum().reset_index()
    df_r_ = df_r.loc[
    #    (df_r['continent'] == continents) &
    #    (df_r['country'] == countries) &
        (df_r['year'] >= select_years[0]) &
        (df_r['year'] < select_years[1])]

    return {
        'data': [
           # go.Scattermapbox(
           #    lon=df_r_['longitude'],
           #    lat=df_r_['latitude'],
           #    mode='markers',
           #    marker=go.scattermapbox.Marker(
           #        size=df_r_['renewables_electricity']/3,
           #        color=df_r_['renewables_electricity'],
           #        colorscale='hsv',
           #        showscale=False,
           #        sizemode='area'
           #    ),
           #    hoverinfo='text'
           # )

            go.Choropleth(
                locations=df_r_['country'],
                locationmode='country names',
                z=df_r_['renewables_electricity'] + df_r_['fossil_electricity'],
                colorscale=[[0.0, "#ffba08"],
                            [0.1111111111111111, "#ffba08"],
                            [0.2222222222222222, "#f48c06"],
                            [0.3333333333333333, "#dc2f02"],
                            [0.4444444444444444, "#dc2f02"],
                            [0.5555555555555556, "#dc2f02"],
                            [0.6666666666666666, "#9d0208"],
                            [0.7777777777777778, "#9d0208"],
                            [0.8888888888888888, "#9d0208"],
                            [1.0, "#370617"]]
            )
        ],

        'layout': go.Layout(
            title={
                'text': 'Worldwide Energy Generation',
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 20
            },
            hovermode='closest',
            margin=dict(l=30, r=20, t=80, b=30),
            paper_bgcolor = 'black',
            plot_bgcolor = 'black',
            font = dict(color = 'white'),
            autosize = True,

        )
    }

@app.callback(
    Output('heat', 'figure'),
    #[Input('continents', 'value')],
    #[Input('countries', 'value')],
    [Input('select_years', 'value')])

def display_plot(select_years):
    df_h = df.loc[df['country'].isin(gseven) & (df['year'] >= select_years[0]) & (df['year'] < select_years[1])]
    df_h_ = df_h.groupby(by=['country'])['nuclear_electricity','biofuel_electricity','hydro_electricity',
    'solar_electricity','wind_electricity','other_renewable_electricity'].sum().reset_index()
    df_h_ = df_h_.set_index('country')
    df_h_ = df_h_.rename(columns = {'nuclear_electricity': 'nuclear', 'biofuel_electricity': 'biofuel',
                                    'hydro_electricity': 'hydro', 'solar_electricity': 'solar',
                                    'wind_electricity': 'wind', 'other_renewable_electricity': 'other'})
    
    return {
        'data': [
            #go.Scattermapbox(
            #    lon=df_r_['longitude'],
            #    lat=df_r_['latitude'],
            #    mode='markers',
            #    marker=go.scattermapbox.Marker(
            #        size=df_r_['renewables_electricity']/3,
            #        color=df_r_['renewables_electricity'],
            #        colorscale='hsv',
            #        showscale=False,
            #        sizemode='area'
            #    ),
            #    hoverinfo='text'
            #)

            go.Heatmap(
                x = df_h_.columns,
                y = df_h_.index,
                z = df_h_.values.round(2),

                hoverongaps = False,
                colorscale='solar',
                text=df_h_.values.round(2),
                texttemplate="%{text}",
                textfont={"size": 10})
        ],

        'layout': go.Layout(
            title={
                'text': 'G7 Renewable Energy Generation (TWh)',
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 20
            },
            hovermode='closest',
            margin=dict(l=120, r=100, t=70, b=70),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            autosize=True)

    }

if __name__ == '__main__':
    app.run_server(debug=True)
