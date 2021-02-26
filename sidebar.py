#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import locale


# In[ ]:


#Initiating data
df = pd.read_csv('cleaned_df.csv')
df.head()


# In[ ]:


df['Gross PM']=np.multiply(np.divide(df['Profit'],df['Sales']),100).round(2)
def state_(dataframe):
    states=dataframe.groupby(['State','state_code','Region'], as_index=False).agg({'Sales':'sum', 
                                                                        'Profit':'sum', 
                                                                        'Discount':'mean',
                                                                        'Quantity':'sum'})
    # Calculating Relative Profit
    states['Gross PM']=np.multiply(np.divide(states['Profit'],states['Sales']),100).round(2)
    states = states.sort_values('Sales',ascending=False,ignore_index=True)
    return states

def group_by(df,col):
    grouped = df.groupby(by=col,as_index=False).agg({'Sales':'sum',
                                                      'Profit':'sum',
                                                      'Quantity':'sum',
                                                      'Discount':'mean'
                                                     })
    grouped['Gross PM']=np.multiply(np.divide(grouped['Profit'],grouped['Sales']),100).round(2)
    return grouped


# ### Creating dash app

# In[ ]:


# Creating dash app

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI],
                suppress_callback_exceptions=True,
               meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
               )
server=app.server


# ### Generating Graphs

# In[ ]:


title_font={'size':20,'color':'black'}
legend_font={'size':16,'color':'black'}
global_font=dict(family="Balto")


# In[ ]:


# BoxPlot Discount vs gross profit margin
fig_1 = px.box(df, x='Discount', y='Gross PM',
               title='Gross Profit Margin Behaviour Under Range of Discounts',
               labels={'Discount':'Product Discount',
                       'Gross PM':'Gross Profit Margin'}
              ).update_traces(marker={'color':'#3399CC'}
                             ).update_layout(height=500, width=900,
                                             title={'font':title_font,
                                                    'x':0.5, 'y':0.9,
                                                    'xanchor':'center', 'yanchor':'middle'},
                                             font=global_font,
                                             legend={'font':legend_font}, 
                                             font_color='black',
                                             plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)')
fig_1.add_hline(y=0, line_dash="dot",
              annotation_text="Zero Profit", 
              annotation_position="bottom right")
fig_1.add_vrect(x0=0.35, x1=0.45, 
              annotation_text="Decline", annotation_position="top left",
              fillcolor='red', opacity=0.20, line_width=0)
fig_1.add_vline(x=0.41, line_width=1, line_dash="dash", line_color="red")
    
# Sunburst Plot
fig_2 = px.sunburst(data_frame=df, 
                    path = ['Category','Sub-Category'],
                    values='Quantity',
                    color='Profit',
                    color_continuous_scale='blues',
                    hover_data={'Quantity':True,'Profit':True},)
fig_2.update_traces(textfont={'family':'arial'},
                    textinfo='label+percent entry',
                    insidetextorientation='radial',
                    marker={'line':{'color':'black'}})   
fig_2.update_layout(title={'text':'Quantity sold and profit gained for each product type',
                           'font':title_font,
                           'x':0.5, 'y':0.02,
                           'xanchor':'center', 'yanchor':'bottom'},
                    legend={'font':legend_font}, font_color='black',
                    font=global_font,
                    plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)')

# Choropleth Map
states=state_(df)
us_map=px.choropleth(data_frame=states,
                    locationmode ='USA-states',
                    locations='state_code',
                    scope='usa',
                    color='Gross PM',color_continuous_scale='blues_r',color_continuous_midpoint=0,
                    hover_name='State',
                    hover_data={'State':False,'Sales':True,'Discount':True,'state_code':False, 'Region':True},
                    labels={'Gross PM':'Gross Profit Margin','Discount_mean':'Avg. Discount'},)

us_map.update_layout(title={'text':'Gross Profit Margin - USA Map', 
                            'font':title_font,
                            'x':0.5, 'y':0.9,
                            'xanchor':'center', 'yanchor':'middle'},
                     font=global_font,
                     font_color='black',
                     geo=dict(bgcolor='rgba(0,0,0,0)'),
                     paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')


# ### Side Bar

# In[ ]:


# Side bar component
sidebar = html.Div(
    [      
        html.H4("Retail Data", 
                className="text-white p-1",
                style={'marginTop':'1rem'}),
        html.H6('Exploratory Data Analysis',
               className="text-white p-1",),
        html.Hr(style={"borderTop": "1px dotted white"}),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/", active="exact"),
                dbc.NavLink("Profit Analysis", href="/page-1", active="exact"),
                dbc.NavLink("Conclusion", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
            style={'fontSize':16}
        ),
        html.P(u"\u00A9"+" Sayali Bachhav", className='fixed-bottom text-white p-2'),

    ],
    className='bg-dark',
    style={"position": "fixed",
           "top": 0,
           "left": 0,
           "bottom": 0,
           "width": "14rem",
           "padding": "1rem",},
)


# ### Home Page Layout

# In[ ]:


# Tabs Style
tab_style = {
    'border': '1px solid black',
    'padding': '6px',
    'fontWeight': 'bold',
    'margin':'0.5rem',
}

tab_selected_style = {
    'border': '1px solid white',
    'background-color': '#3399CC',
    'padding': '6px',
    'margin':'0.5rem'
}

# to format thousands commas in numbers
locale.setlocale(locale.LC_ALL, '')


# In[ ]:


h_container = dbc.Container(
    [        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Tabs(id="radio_options",
                             value='Transactions',
                             children=[dcc.Tab(label='Total Transactions',
                                               value='Transactions',
                                               style=tab_style, selected_style=tab_selected_style,
#                                                selected_className='bg-dark text-white',
                                              ),
                                       dcc.Tab(label='Sales',
                                               value='Sales',
                                               style=tab_style, selected_style=tab_selected_style,
#                                                selected_className='bg-dark text-white',
                                              ),
                                       dcc.Tab(label='Profit',
                                               value='Profit', 
                                               style=tab_style, selected_style=tab_selected_style,
#                                                selected_className='bg-dark text-white',
                                              ),
                                       dcc.Tab(label='Quantity',
                                               value='Quantity',
                                               style=tab_style, selected_style=tab_selected_style,
#                                                selected_className='bg-dark text-white',
                                              ),
                                       dcc.Tab(label='Average Discount',
                                               value='Discount',
                                               style=tab_style, selected_style=tab_selected_style,
#                                                selected_className='bg-dark text-white',
                                              ),
                                      ],
                            )
                )
            ],no_gutters=True, justify = 'around',
        ),       
        
        dbc.Row(
            [     
                dbc.Col(
                    [
                        html.P('Total Sales', 
                                style={
                                       'margin':'1rem', 
                                       'textAlign':'center',
                                      'border':'1px solid white'},
                                className='text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        html.P('USD {}'.format(str(locale.format("%.4f", df.Sales.sum().round(2), grouping=True))),
                                style={'textAlign':'center','fontColor':'black'}),
                        
                        html.P('Total Profit', 
                                style={
                                       'margin':'1rem', 
                                       'textAlign':'center',
                                      'border':'1px solid white'},
                                className='text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        html.P('USD {}'.format(str(locale.format("%.4f", df.Profit.sum().round(2), grouping=True))),
                                style={'textAlign':'center','color':'black'}),
                        
                    ],width=2, style={"border": "2px solid black", 'borderRight':False},
                ),
                
                dbc.Col(
                    [
                        dcc.Graph(id='subplot',figure={})
                    ],width={'size':5, 'offset':0}, style={"border": "2px solid black"},
                ),
                
                dbc.Col(
                    [
                        dcc.Graph(id='map',figure=us_map)
                    ],width={'size':5, 'offset':0},style={"border": "2px solid black", 'borderLeft':False})
            ],no_gutters=True, justify = 'around',
        ), 
        
        dbc.Row([
            dbc.Col(dcc.Graph(id='bar',figure={}),
                   style={"border": "2px solid black", 'borderTop':False})
        ],no_gutters=True, justify = 'around',),
    ], fluid=True,
)


# ### Page-1 Layout

# In[ ]:


# Tab style
tab_style = {
    'border': '1px solid black',
    'padding': '6px',
    'margin':'1rem',
    'fontWeight': 'bold',
}

tab_selected_style = {
    'border':'1px solid white' ,
    'background-color': '#3399CC',
    'color':'white',
    'margin':'1rem',
    'padding': '6px'
}

dropdown = dcc.Dropdown(id='product-dropdown',
                        options=[{'label': x, 'value': x} for x in sorted(df['Sub-Category'].unique())],
                        placeholder="Select a product",
                        style={'margin':'1rem',}
                       )

options = dcc.Tabs(id="tabs",
                   value="Profit",
                   children=[dcc.Tab(label="Profit", value="Profit",
                                     style=tab_style,selected_style=tab_selected_style),
                             dcc.Tab(label="Quantity", value="Quantity",
                                     style=tab_style,selected_style=tab_selected_style)],
                             vertical=False,
                  )
p1_container = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([
                    
                    dbc.Row(
                        [
                            dbc.Col(dropdown, width=6),
                            dbc.Col(options, width=6),
                        ],
                    ),
                    
                    dcc.Graph(id='heat',figure={}),
                    
                ], width={'size':7},style={"border": "1px solid black",}),
                
                dbc.Col(
                    dcc.Graph(id='sunburst',figure=fig_2, responsive=True),
                    width={'size':5},style={"border": "1px solid black",},
                ),
            ],no_gutters=True,justify = 'around',
        ),
        
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='box',figure=fig_1),),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.P(
                                        ['There is a progressive decline in the profit margin as discount increases.',
                                         html.Hr(),
                                        'Red region denotes the transition of all transactions to negative profit margin.',],
                                        className="card-text",),
                                ],),
                        ],color='red',style={'background-color':'rgba(255, 0, 0, 0.2)', 'font-color':'black'},
                    ),
                    className='d-flex justify-content-center align-items-center',
                    style={'margin':'1rem'},
                ),
            ], no_gutters=True,justify = 'around',
        ),
    ],fluid=True,
)


# ### Conclusion Layout

# In[ ]:


# Creating card components

card_main = dbc.Card(
    [
        dbc.CardHeader(html.H4("Initial Insights", className="card-title"),
                       className='bg-primary text-white',
                      ),
        dbc.CardBody(
            [         
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem("1. Total 9977 customer transactions"),
                        dbc.ListGroupItem("2. An average sales of USD 230.14 per customer transaction"),
                        dbc.ListGroupItem("3. An average profit of USD 28.69 per customer transaction"),
                    ],
                ),
            ], className='bg-info',
        ),
    ],
)



card_con = dbc.Card(
    [
        dbc.CardHeader(html.H4("Weak Areas", className="card-title"),
                      className='bg-primary text-white',),
        dbc.CardBody(
            [
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem("1. Gross profit margin seem to be decreasing with increment in discount on products."),
                        dbc.ListGroupItem("2. Beyond 40% discount, the store has experienced loss only"),
                        dbc.ListGroupItem("3. The quantities sold are not increasing with increasing discount."),
                    ],
                ),
            ],className='bg-info',
        ),
    ],
)

card_final = dbc.Card(
    [
        dbc.CardHeader(html.H4("Conclusion", className="card-title"),
                      className='bg-primary text-white',),
        dbc.CardBody(
            [
                html.P([
                    "The store has performed well when no discount or less than 20% discount is applied",
                    html.Hr(), 
                    'The store might benefit by reducing discount on loss making product items.',
                    html.Hr(),
                    'Marketing and advertisement in regions with less customer base might help to increase the store presence.',               
                ],
                    className="card-text",
                ),
            ],className='bg-info',
        ),
        
        dbc.CardLink("GitHub Link", 
                     className='text-center font-weight-bold',
                     href="https://github.com/sayaliba01/The-Sparks-Foundation-GRIPJAN21/tree/main/EDA-Retail%20Data")
    ],
    color='primary',
    outline=True,
)

# Conclusion page container
p2_container=dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(card_main, width={'size':4,'offset':1}, style={'marginTop':'2rem'}),
                dbc.Col(card_con, width={'size':4,'offset':1}, style={'marginTop':'2rem'}),
            ], no_gutters=True,justify="around"
        ),
        
        dbc.Row(
            [
                dbc.Col(card_final, width={'size':6}, style={'marginTop':'2rem', 'marginBottom':'2rem'}),
            ], no_gutters=True,justify="around"
        ),
    ]
)


# ### Main content Layout

# In[ ]:


""" Main app body components"""
CONTENT_STYLE = {
    "marginLeft": "13rem",
    "margin-right": "1rem",
    "padding": "0rem 0rem",
    'background-color':'#F0F4F5',
}

content = html.Div(id="page-content", children=[], 
                   style=CONTENT_STYLE )


# ### Whole app layout

# In[ ]:


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        content
    ]
)


# ### App Callback Functions

# __Sidebar Callback__

# In[ ]:


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
                h_container
                ]
    elif pathname == "/page-1":
        return [
                p1_container,
                ]
    elif pathname == "/page-2":
        return [
                p2_container,
                ]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# __Home container callback__

# In[ ]:


@app.callback(
    [Output(component_id='subplot', component_property='figure'),
     Output(component_id='bar', component_property='figure'),],
    [Input(component_id='radio_options', component_property='value')]
)


def update_output(option):
    
    dff=df.copy()
    dff.round(2)
    
    if option=='Transactions':
        
        fig = make_subplots(rows=2, cols=2, shared_yaxes=True)
        
        fig.add_trace(go.Histogram(x=dff['Ship Mode'],name='Shipping Mode'),
              row=1, col=1)
        
        fig.add_trace(go.Histogram(x=dff['Segment'],name='Customer Segment'),
              row=1, col=2)
        
        fig.add_trace(go.Histogram(x=dff['Region'],name='USA Region'),
              row=2, col=1)
        
        fig.add_trace(go.Histogram(x=dff['Category'],name='Product Category'),
              row=2, col=2)
        fig.update_layout(xaxis={'categoryorder':'category ascending'})
        
    else:
        fig = make_subplots(rows=2, cols=2, shared_yaxes=True)
        
        ship=group_by(dff,'Ship Mode') 
        fig.add_trace(go.Bar(x=ship['Ship Mode'],y=ship[option],name='Shipping Mode'),
              row=1, col=1)
        
        seg=group_by(dff,'Segment')
        fig.add_trace(go.Bar(x=seg['Segment'],y=seg[option],name='Customer Segment'),
              row=1, col=2)
        
        reg=group_by(dff,'Region')
        fig.add_trace(go.Bar(x=reg['Region'],y=reg[option],name='USA Region'),
              row=2, col=1)
        
        cat=group_by(dff,'Category')
        fig.add_trace(go.Bar(x=cat['Category'],y=cat[option],name='Product Category'),
              row=2, col=2)
        
    fig.update_layout(xaxis={'categoryorder':'category ascending'},
                      legend=dict(orientation="h",
                                  yanchor="bottom", y=1.2, 
                                  xanchor="left",x=0),
                      font=global_font,
                      font_color='black',
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    if option=='Transactions':
        option='Sales'
        
    fig_3=px.bar(data_frame=states, x = 'State', y = option, 
                 color='Gross PM', 
                 color_continuous_scale='blues_r',color_continuous_midpoint=0,
                 title = ('{} Across US States'.format(option))
                ).update_traces(marker_line_color='rgb(8,48,107)',
                                marker_line_width=1
                               ).update_layout(title={'font':title_font, 'x':0.5, 'y':0.9,
                                                      'xanchor':'center', 'yanchor':'middle'},
                                               font=global_font,
                                               legend={'font':legend_font}, font_color='black',
                                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    return fig, fig_3


# __Page-1 Callback__

# In[ ]:


@app.callback(
    Output(component_id='heat', component_property='figure'),
    [Input(component_id='tabs', component_property='value'),
     Input(component_id='product-dropdown', component_property='value'),]
)


def update_output(tab, product):
    dff=df.copy()
    dff['Gross PM']=np.multiply(np.divide(dff['Profit'],dff['Sales']),100).round(2)
    dff.round(2)
    
    legend={'font':legend_font,
            'title':{'text':'Click categories to select/deselect', 'side':'top'},
            'orientation':"h",
            'yanchor':"bottom", 'y':1.2,  
            'xanchor':"center",'x':0.5,
            'bordercolor':'grey','borderwidth':1
           }
    
    if product==None:
        data = group_by(dff,['Discount','Category']).sort_values('Discount',ascending=True,ignore_index=True)
        fig_3=px.bar(data, x='Discount', y=tab,
                    color="Category", barmode="group")
    else:
        data = group_by(dff[dff['Sub-Category']==product],'Discount').sort_values('Discount',ascending=True,ignore_index=True)
        fig_3=px.bar(data, x='Discount', y=tab)
        
        
    fig_3.update_layout(xaxis=dict(tickmode='linear',tick0=0,dtick=0.1),
                        font=global_font,
                        legend=legend, 
                        font_color='black',
                        plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)')
    
    fig_3.update_xaxes(showgrid=True)
    
    return fig_3
    


# ### Launching web application dashboard

# In[ ]:


if __name__=='__main__':
    app.run_server(debug=True, use_reloader=False)  


# In[ ]:




