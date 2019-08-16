from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from dash.dependencies import Input,Output

# styling framework
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
input_dataset = './data/processed/op_data.csv'

# data load
sets_data = pd.read_csv(input_dataset)

# input limits
min_year = sets_data.year.min()
max_year = sets_data.year.max()
min_parts = sets_data.num_parts.min()
max_parts = sets_data.num_parts.max()
themes_unique = np.sort(sets_data.parent_theme_name.unique()).tolist()

# create a label-value dictionary for creating a checklist
checklist_dict = [{key:theme for key in ['label','value']} for theme in sets_data.parent_theme_name.unique().tolist()]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# consists of tree of components defining the layout
app.layout = html.Div(className='row',children=[
    html.H3(children='Lego Visualization'),

    #html.Div(children='''
    #    XYZ
    #'''),
    html.Div(className='row',children=[
    html.Div(className='four columns',
       style={'background-color':'whitesmoke'},
    children=[
    
    html.Div(className='ten columns offset-by-one',
    style={'margin-top':35},
    children=[
    html.Label(dcc.Markdown('**Timeline:**')),
    dcc.RangeSlider(
        count=1,
        min=min_year,
        max=max_year,
        step=1,
        marks={i: str(i) for i in range(min_year, max_year+1,10)},
        value=[1960,1990],
        allowCross=False,
        id='year-slider'
    )]),

    html.Div(className='ten columns offset-by-one',
    style={'margin-top':35},
    children=[
    html.Label(dcc.Markdown('**Number of Pieces:**')),
    dcc.RangeSlider(
        count=1,
        min=min_parts,
        max=max_parts,
        step=1,
        marks={i: str(i) for i in range(min_parts, max_parts+1,1000)},
        value=[0,5000],
        allowCross=False,
        id='num-parts-slider'
    ),]),


    html.Div(className='ten columns offset-by-one',
    style={'margin-top':35},    
    children=[
    html.Label(dcc.Markdown('**LEGO Themes:**')),
    dcc.Checklist(
                    options=checklist_dict,
                    value=themes_unique,
                    id='themes-checkbox'
                )
    ])
    ]),
    
    html.Div(className='seven columns offset-by-one',
            children=[
                    # plotly interactive graphs
                    dcc.Graph(
                                id='sets-year-graph'
                            ),

                    dcc.Graph(
                                id='themes-year-graph'
                            ),

                            dcc.Graph(
                                id='parts-year-graph'
                            )
                    ]
            )
    ])
])

app.title = 'Lego Visualization'

@app.callback(
    [Output('sets-year-graph', 'figure'),
    Output('themes-year-graph', 'figure'),
    Output('parts-year-graph', 'figure')],
    [Input('year-slider', 'value'),
    Input('num-parts-slider', 'value'),
    Input('themes-checkbox', 'value')])
def update_figures(selected_years,selected_parts,selected_themes):
    
    # apply filter on data based on user inputs
    sets_data_filt = sets_data[(sets_data['year']>=selected_years[0])&(sets_data['year']<=selected_years[1])
                              &(sets_data['num_parts']>=selected_parts[0])&(sets_data['num_parts']<=selected_parts[1])
                              &(sets_data['parent_theme_name'].isin(selected_themes))
                              ]
    #print(str(selected_parts[0])+str(selected_parts[1]))
    #print(str(selected_years[0])+str(selected_years[1]))
    #print(selected_themes)
    # datasets for individual graphs
    # graph 1 data
    graph1_data = sets_data_filt[['year','set_num']].groupby('year')['set_num'].nunique()
    graph1_data = pd.DataFrame({'year':graph1_data.index,'total_sets':graph1_data.values})

    # graph 2 data
    graph2_data = sets_data_filt[['year','parent_theme_name']].groupby('year')['parent_theme_name'].nunique()
    graph2_data = pd.DataFrame({'year':graph2_data.index,'total_themes':graph2_data.values})

    # graph 3 data
    graph3_data = sets_data_filt[['year','set_num','name','parent_theme_name','num_parts']]

    # hover text for graph3
    hovertext_graph3 = ['<b>Set Name:</b> '+x+'<br><b>Theme:</b> '+y\
    for x,y in zip(graph3_data['name'].values.tolist(),\
    graph3_data['parent_theme_name'].values.tolist())]


    return [

            {
            'data': [
                        {   'x': graph1_data['year'],\
                            'y': graph1_data['total_sets'],\
                            'type': 'scatter',
                            'name': 'total_sets',
                            'fill':'tozeroy'
                        }
                    ],
            'layout': {
                        'title': 'Number of Sets by Year',
                        'yaxis':{'title':'Number of Sets'},
                        'xaxis':{'title':'Year'}
                    }
            },

            {
            'data': [
                        {   'x': graph2_data['year'],\
                            'y': graph2_data['total_themes'],\
                            'type': 'bar',
                            'name': 'total_themes'
                        }
                    ],
            'layout': {
                        'title': 'Number of Themes by Year',
                        'yaxis':{'title':'Number of Themes'},
                        'xaxis':{'title':'Year'}
                    }
            },

            {
            'data': [
                        {   'x': graph3_data['year'],\
                            'y': graph3_data['num_parts'],\
                            'type': 'scatter',
                            'name': 'total_sets',
                            'mode':'markers',
                            'marker':{'opacity':0.3},
                            'text':hovertext_graph3
                        }
                    ],
            'layout': {
                        'title': 'Number of Pieces by Year',
                        'yaxis':{'title':'Number of Pieces'},
                        'xaxis':{'title':'Year'},
                        'hovermode':'closest'
                        }
            }

           ]


if __name__ == '__main__':
    app.run_server(debug=False,port=33507)