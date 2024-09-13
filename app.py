import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash import callback_context
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
import dash_table as dtab
import datetime as dtt

### app:
app = dash.Dash(__name__, title='STAT 430 US COVID-19 DATA TRACKER')


### load data
juris = pd.read_csv('COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv')

county = pd.read_csv('COVID-19_Vaccinations_in_the_United_States_County.csv')

trans = pd.read_csv('United_States_COVID-19_County_Level_of_Community_Transmission_as_Originally_Posted.csv')



### state data stuff:
dat1 = juris[["Date", 'Location', 'Administered_Dose1_Pop_Pct', 'Series_Complete_Pop_Pct']]
dat1.rename(columns = {'Administered_Dose1_Pop_Pct' : 'At Least 1 Dose', 'Series_Complete_Pop_Pct' : 'Fully Vaccinated'}, inplace = True)
dat1['Date'] = pd.to_datetime(dat1['Date'])
dat1.sort_values(by = ['Date'], inplace = True)
numdate= [x for x in range(len(dat1['Date'].unique()))]
mark = {numd:date.strftime('%m/%d/%Y') for numd,date in zip(numdate, dat1['Date'].dt.date.unique())}
marks = pd.DataFrame.from_dict(mark, orient = 'index')
marks['numdate'] = numdate

### county data stuff:
dat2 = county[['Date', 'Recip_County', 'Recip_State', 'Series_Complete_Pop_Pct', 'Administered_Dose1_Pop_Pct']]
dat2.rename(columns = {'Recip_County' : 'Name', 'Recip_State': 'State', 'Administered_Dose1_Pop_Pct' : 'At Least 1 Dose %', 'Series_Complete_Pop_Pct' : 'Fully Vaccinated %'}, inplace = True)
dat2['Date'] = pd.to_datetime(dat2['Date'])
dat2.sort_values(by = ['Date'], inplace = True)
dat2.drop(dat2[dat2['Name'] == 'Unknown County'].index, inplace = True)
dat2fil = dat2[['Name', 'At Least 1 Dose %', 'Fully Vaccinated %']]

numdate2= [x for x in range(len(dat2['Date'].unique()))]
mark2 = {numd:date.strftime('%m/%d/%Y') for numd,date in zip(numdate2, dat2['Date'].dt.date.unique())}
marks2 = pd.DataFrame.from_dict(mark2, orient = 'index')
marks2['numdate'] = numdate2

### transmitted data stuff:
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

sup_dict = {'suppressed' : np.nan}

dat3 = trans[['state_name', 'county_name', 'report_date', 'cases_per_100K_7_day_count_change', 
                'percent_test_results_reported_positive_last_7_days']]
dat3.rename(columns = {'state_name' : 'State', 'county_name' : 'County', 'report_date': 'Date', 
                'percent_test_results_reported_positive_last_7_days' : 'Positive Test',
                 'cases_per_100K_7_day_count_change' : 'New Cases'}, inplace = True)
dat3.replace({'State' : us_state_to_abbrev}, inplace = True)
dat3.replace({'New Cases' : sup_dict}, inplace = True)
dat3['New Cases'] = dat3['New Cases'].str.replace(',', '')
dat3['New Cases'] = pd.to_numeric(dat3['New Cases'])
#dat3.fillna(0, inplace = True)
dat3['Date'] = pd.to_datetime(dat3['Date'])
dat3.sort_values(by = ['Date'], inplace =True)
numdate3= [x for x in range(len(dat3['Date'].unique()))]
mark3 = {numd:date.strftime('%m/%d/%Y') for numd,date in zip(numdate2, dat3['Date'].dt.date.unique())}
marks3 = pd.DataFrame.from_dict(mark3, orient = 'index')
marks3['numdate'] = numdate3



### layout:
app.layout = html.Div([

    # app title:
    html.H1(
        'STAT 430 US COVID-19 DATA TRACKER',
        style={'textAlign': 'center', 'padding': 10, 'flex': 1}
    ),

    ### graph 1 layouts
    dcc.Graph(id='graph-with-slider'),

    html.Div(children='''
        Please Select Desired Vaccination Status:
    ''', style={'padding': 10, 'flex': 1}),

    html.Div([
        dcc.RadioItems(
            id = 'radio-vaccine-status',
            options=[{'label': i, 'value': i} for i in ['Fully Vaccinated', 'At Least 1 Dose']],
            value='Fully Vaccinated',
            labelStyle={'display': 'inline-block'}
        )
    ], style={'padding': 10, 'flex': 1}),

    html.Div(children='''
        Please Select Desired Date(up-to):
    ''', style={'padding': 10, 'flex': 1}),

    html.Div([
        dcc.Slider(
            id='date-slider',
            min=numdate[0],
            max=numdate[-1],
            value=numdate[-1],
            step=1,
            #marks = {str(numd):date.strftime('%m/%d/%Y') for numd,date in zip(numdate, datt2['Date'].dt.date.unique())},
            marks = {1 : '12/13/2020', int(numdate[-1]) : 'Today'}
        )
    ]),

    html.Div(id='display-selected-values', style={'padding': 10, 'flex': 1}),

    html.Hr(style={'padding': 10}),

    html.Div([
        html.H2(
            'County Level Statistics',
            style={'textAlign': 'center', 'padding': 10, 'flex': 1}
        ),

        html.Div([
            html.Div([
                ### table 2 layouts:
                html.Label('Please Select Desired State:', style={'padding': 10, 'flex': 1}),

                html.Div([
                    dcc.Dropdown(
                        id='state-select',
                        options=[{'label': i, 'value': i} for i in dat2['State'].sort_values().unique()],
                        value='IL'
                    ),
                ], style={'padding': 10, 'flex': 1}),
            
                html.Label('Sort By:', style={'padding': 10, 'flex': 1}),

                html.Div([
                    dcc.RadioItems(
                        id = 'radio-sort',
                        options=[{'label': i, 'value': i} for i in ['Name', 'Fully Vaccinated %', 'At Least 1 Dose %']],
                        value='Name',
                        labelStyle={'display': 'inline-block'}
                    ),
                ], style={'padding': 10, 'flex': 1}),

                html.Label('Order:', style={'padding': 10, 'flex': 1}),

                html.Div([
                    dcc.RadioItems(
                        id = 'radio-order',
                        options=[{'label': i, 'value': i} for i in ['Increasing', 'Decreasing']],
                        value='Increasing',
                        labelStyle={'display': 'inline-block'}
                    ),
                ], style={'padding': 10, 'flex': 1}),

                html.H3(
                    "Table of County Level Vaccination Status By State",
                    style={'textAlign': 'center', 'padding': 10, 'flex': 1}
                ),
                
                html.Div([
                    dtab.DataTable(
                        id='table2',
                        data = dat2fil.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in dat2fil.columns],
                        editable = True,
                        style_cell={'textAlign': 'left'}
                    ),
                ], style={'padding': 10, 'flex': 1}),
                

                html.Div([
                    dcc.Slider(
                        id='date-slider2',
                        min=numdate2[0],
                        max=numdate2[-1],
                        value=numdate2[-1],
                        step=1,
                        marks = {1 : '12/13/2020', int(numdate2[-1]) : 'Today'}
                    ),
                ], style={'padding': 10, 'flex': 1}),

                html.Div(id='display-selected-values2', style={'padding': 10, 'flex': 1}),
                
            ], style={'width': '48%', 'display': 'inline-block', 'padding': 10, 'flex': 1}),

            html.Div([
                ### graph 3, 4 layouts:
                html.Label('Please Select Desired County (Only for Displayed Graphs):', style={'padding': 10, 'flex': 1}),

                html.Div([
                    dcc.Dropdown(
                        id='county-select',
                        options=[{'label': i, 'value': i} for i in dat3['County'].sort_values().unique()],
                        value='Champaign County'
                    ),
                ], style={'padding': 10, 'flex': 1}),

                html.Label('Please Press Submit to Display Graphs', style={'padding': 10, 'flex': 1}),

                html.Div([
                    html.Button(
                        "Submit",
                        id='submit-btn',
                        n_clicks=0
                    )
                ], style={'padding': 20, 'flex': 1}),

                html.Label('  ', style={'padding': 10, 'flex': 1}),

                html.Label('  ', style={'padding': 10, 'flex': 1}),

                html.H3(
                    "County Level Transmission Graphs",
                    style={'textAlign': 'center', 'padding': 20, 'flex': 1}
                ),

                html.Label('  ', style={'padding': 10, 'flex': 1}),

                html.Label('  ', style={'padding': 10, 'flex': 1}),

                html.Label('  ', style={'padding': 10, 'flex': 1}),

                html.Label('  ', style={'padding': 10, 'flex': 1}),

                html.Div([
                    dcc.Graph(id='graph3'),
                ], style={'padding': 10, 'flex': 1}),

                html.Div([
                    dcc.Graph(id='graph4'),
                ], style={'padding': 10, 'flex': 1}),

                html.Div([
                    dcc.RangeSlider(
                        id='date-range-slider',
                        min=numdate3[0],
                        max=numdate3[-1],
                        value=[numdate3[0], numdate3[-1]],
                        step=1,
                        marks = {int(numdate3[0]) : '08/16/2021', int(numdate3[-1]): 'Today'}
                    )
                ], style={'padding': 10, 'flex': 1}),

                html.Div(id='display-selected-values3', style={'padding': 10, 'flex': 1}),
                
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block', 'padding': 10, 'flex': 1})
            
        ], style={'padding': 10, 'flex': 1}),

    ]),

    html.H5(
        'A Dash Web App by Yuchen Wang (yuchenw7)',
        style={'textAlign': 'right'}
    ),

    html.Hr(),

])


### callbacks:

### graph 1 callbacks
@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('date-slider', 'value'),
    Input('radio-vaccine-status', 'value'))
def update_figure(date, status):
    sdate = marks.iloc[marks.loc[marks['numdate'] == date].index[0],0]
    filtered_df = dat1.loc[(dat1["Date"] == sdate)]
    if status == 'Fully Vaccinated':
        filtered_df = filtered_df[['Date', 'Location', 'Fully Vaccinated']]
    else:
        filtered_df = filtered_df[['Date', 'Location', 'At Least 1 Dose']]
    
    fig = go.Figure(data=go.Choropleth(
        locations=filtered_df['Location'], # Spatial coordinates
        z = filtered_df.iloc[:, 2].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Blues',
        colorbar_title = "Percentage",
    ))
    fig.update_layout(
        title_text = 'Covid Vaccine Status By State',
        geo_scope='usa', # limite map scope to USA
    )

    return fig



### slider 1 display
@app.callback(
    Output('display-selected-values', 'children'),
    Input('date-slider', 'value'))
def update_output_s1(date):
    sdate = marks.iloc[marks.loc[marks['numdate'] == date].index[0],0]
    return 'You have selected "{}"'.format(sdate)

### slider 2 display
@app.callback(
    Output('display-selected-values2', 'children'),
    Input('date-slider2', 'value'))
def update_output_s2(date):
    sdate = marks2.iloc[marks2.loc[marks2['numdate'] == date].index[0],0]
    return 'You have selected "{}"'.format(sdate)

### slider 3 display
@app.callback(
    Output('display-selected-values3', 'children'),
    Input('date-range-slider', 'value'))
def update_output_s3(dates):
    date1 = dates[0]
    date2 = dates[1]
    sdate1 = marks3.iloc[marks3.loc[marks3['numdate'] == date1].index[0],0]
    sdate2 = marks3.iloc[marks3.loc[marks3['numdate'] == date2].index[0],0]
    return 'You have selected the period between "{}" and "{}"'.format(sdate1, sdate2)



### table2 callbacks
@app.callback(
    Output('table2', 'data'),
    Input('date-slider2', 'value'),
    Input('state-select', 'value'),
    Input('radio-sort', 'value'),
    Input('radio-order', 'value')
)
def update_table(date, state, sort, order):
    sdate = marks2.iloc[marks2.loc[marks2['numdate'] == date].index[0],0]
    statename = str(state)
    filtered_dat2 = dat2.loc[(dat2['State'] == statename) & (dat2['Date'] == sdate)]
    filtered_df2 = filtered_dat2[['Name', 'At Least 1 Dose %', 'Fully Vaccinated %']]
    if (sort == 'Name') & (order == 'Increasing'):
        filtered_df2.sort_values(by = ['Name'], inplace = True)
    elif (sort == 'At Least 1 Dose %') & (order == 'Increasing'):
        filtered_df2.sort_values(by = ['At Least 1 Dose %'], inplace = True)
    elif (sort == 'Fully Vaccinated %') & (order == 'Increasing'):
        filtered_df2.sort_values(by = ['Fully Vaccinated %'], inplace = True)
    elif (sort == 'Name') & (order == 'Decreasing'):
        filtered_df2.sort_values(by = ['Name'], ascending = False, inplace = True)
    elif (sort == 'At Least 1 Dose %') & (order == 'Decreasing'):
        filtered_df2.sort_values(by = ['At Least 1 Dose %'], ascending = False, inplace = True)
    else:
        filtered_df2.sort_values(by = ['Fully Vaccinated %'], ascending = False, inplace = True)

    return filtered_df2.to_dict('records')



### dynamic slider
@app.callback(
    Output('date-slider2', 'min'),
    Output('date-slider2', 'max'),
    Output('date-slider2', 'value'),
    Output('date-slider2', 'marks'),
    Input('state-select', 'value')
)
def update_slider2(state):
    statename = str(state)
    filtered_slider_date2 = dat2.loc[(dat2['State'] == statename)]
    filtered_slider_date2['Date'] = pd.to_datetime(filtered_slider_date2['Date'])
    numdate_slider2 = [x for x in range(len(filtered_slider_date2['Date'].unique()))]
    date_dict_slider2 = {numd:date.strftime('%m/%d/%Y') for numd,date in zip(numdate_slider2, filtered_slider_date2['Date'].dt.date.unique())}
    fd = date_dict_slider2.get(numdate_slider2[0])
    return numdate_slider2[0], numdate_slider2[-1], numdate_slider2[-1], {1 : fd, int(numdate_slider2[-1]) : 'Today'}



### dynamic county dropdown:
@app.callback(
    Output('county-select', 'options'),
    [Input('state-select', 'value')]
)
def update_county_dropdown(state):
    selstate = dat3.loc[(dat3['State'] == str(state))]
    
    return [{'label': i, 'value': i} for i in selstate['County'].sort_values().unique()]

@app.callback(
    Output('county-select', 'value'),
    Input('county-select', 'options')
)
def update_county_dropdown_val(options):
    
    return options[0]['value']



### dynamic rangeslider
@app.callback(
    Output('date-range-slider', 'min'),
    Output('date-range-slider', 'max'),
    Output('date-range-slider', 'value'),
    Output('date-range-slider', 'marks'),
    Input('submit-btn', 'n_clicks'),
    State('state-select', 'value'),
    State('county-select', 'value')
)
def update_range_slider(nclicks, state, county):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'submit-btn' in changed_id:
        statename = str(state)
        countyname = str(county)
        filtered_slider_date3 = dat3.loc[(dat3['State'] == statename) & (dat3['County'] == countyname)]
        filtered_slider_date3['Date'] = pd.to_datetime(filtered_slider_date3['Date'])
        filtered_slider_date3.sort_values(by=['Date'], inplace=True)
        numdate_slider3 = [x for x in range(len(filtered_slider_date3['Date'].unique()))]
        date_dict_slider3 = {numd:date.strftime('%m/%d/%Y') for numd,date in zip(numdate_slider3, filtered_slider_date3['Date'].dt.date.unique())}
        fd = date_dict_slider3.get(numdate_slider3[0])
        return numdate_slider3[0], numdate_slider3[-1], [numdate_slider3[0], numdate_slider3[-1]], {0 : fd, int(numdate_slider3[-1]) : 'Today'}
    else:
        return dash.no_update


### graph3, 4 callbacks:
@app.callback(
    Output('graph3', 'figure'),
    Output('graph4', 'figure'),
    Input('date-range-slider', 'value'),
    State('state-select', 'value'),
    State('county-select', 'value')
)
def update_figure34(dates, state, county):
    date1 = dates[0]
    date2 = dates[1]
    sdate1 = marks3.iloc[marks3.loc[marks['numdate'] == date1].index[0],0]
    sdate2 = marks3.iloc[marks3.loc[marks['numdate'] == date2].index[0],0]
    filt = dat3.loc[(dat3['State'] == str(state)) & (dat3['County'] == str(county))]
    filtered_df3 = filt.loc[(filt['Date'].dt.date >= dtt.datetime.strptime(sdate1, '%m/%d/%Y').date()) 
                    & (filt['Date'].dt.date <= dtt.datetime.strptime(sdate2, '%m/%d/%Y').date())]
    filtered_df3.sort_values(by = ['Date'], inplace = True)
    fig = px.line(filtered_df3, x = 'Date', y = 'New Cases', title="Daily New Cases -- 7-day Moving Average per 100k", 
                    labels = {'New Cases' : 'Cases Per 100k'})
    fig2 = px.line(filtered_df3, x = 'Date', y = 'Positive Test', title="Daily % Positivity -- 7-day Moving Average",
                    labels = {'Positive Test' : 'Positivity %'})
    return fig, fig2



if __name__ == '__main__':
    app.run_server(debug=True)