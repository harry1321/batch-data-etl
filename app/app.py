import dash
from dash.dependencies import Output, Input, State

from layouts import Layout, fd_plot, sfd_plot, tp_plot
from query import GCBigQuery
from plot import DFplot
from variables import vd_id, vd_name, vd_dict

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = Layout
server = app.server

gcb = GCBigQuery(dataset_name='test')

@app.callback(
    [Output("graphs", "children"),
    Output('update-button', 'n_clicks')],
    [Input("graphtabs", "value")])
def render_graph_content(gtab):
    if gtab == "Fundamental-Diagram":
        return [fd_plot], 1
    elif gtab == "Speed-Flow-Diagram":
        return [sfd_plot], 1
    elif gtab == "Hour-of-Day-Traffic-Pattern":
        return [tp_plot], 1

@app.callback(
    [Output('location-dropdown', 'value'),
    Output('location-dropdown-active', 'data')],
    [Input('location-dropdown', 'value'),
    State('location-dropdown-active', 'data')],)
def update_loc_none_options(value,active):
    if len(value) < 1:
        return active, active
    else:
        return value, value

@app.callback(
    [Output('weekdays', 'value'),
    Output('weekdays-active', 'data')],
    [Input('weekdays', 'value'),
    State('weekdays-active','data')])
def update_wee_none_options(value,active):
    if len(value) < 1:
        return active, active
    else:
        return value, value

@app.callback(
    [Output(component_id='fundamental_d',component_property='figure')],
    [Input(component_id='update-button', component_property='n_clicks'),
    State(component_id='date-picker',component_property='start_date'),
    State(component_id='date-picker',component_property='end_date'),
    State(component_id='location-dropdown',component_property='value'),
    State(component_id='time-slider',component_property='value'),
    State(component_id='weekdays',component_property='value'),]
)
def update_fd_graph(n_clicks,sdate,edate,loc,time_r,weekdays):
    if n_clicks > 0:
        stime = "{:d}:{:02d}:00".format(*divmod(time_r[0]*60, 60))
        etime = "{:d}:{:02d}:00".format(*divmod(time_r[1]*60, 60))
        loc = [loc[i].split('-')[0] for i in range(len(loc))]
        loc = [ list(vd_dict.keys())[list(vd_dict.values()).index(i)] for i in loc]
        print(loc)
        sql = gcb.standard_query(start_date=sdate, end_date=edate, weekdays=weekdays, stime=stime, etime=etime, locations=loc)
        results = DFplot(gcb.query(sql))
        results = results.replace({'vd': vd_dict})
        results = results[results['vd'] != '29.600']
        return [results.plot_fundamental_d()]

@app.callback(
    [Output(component_id='speedflow_d',component_property='figure')],
    [Input(component_id='update-button', component_property='n_clicks'),
    State(component_id='date-picker',component_property='start_date'),
    State(component_id='date-picker',component_property='end_date'),
    State(component_id='location-dropdown',component_property='value'),
    State(component_id='time-slider',component_property='value'),
    State(component_id='weekdays',component_property='value')]
)
def update_sf_graph(n_clicks,sdate,edate,loc,time_r,weekdays):
    if n_clicks > 0:
        stime = "{:d}:{:02d}:00".format(*divmod(time_r[0]*60, 60))
        etime = "{:d}:{:02d}:00".format(*divmod(time_r[1]*60, 60))
        loc = [loc[i].split('-')[0] for i in range(len(loc))]
        loc = [ list(vd_dict.keys())[list(vd_dict.values()).index(i)] for i in loc]
        sql = gcb.standard_query(start_date=sdate, end_date=edate, weekdays=weekdays, stime=stime, etime=etime, locations=loc)
        results = DFplot(gcb.query(sql))
        results = results.replace({'vd': vd_dict})
        results = results[results['vd'] != '29.600']
        return [results.plot_speedflow_d()]

@app.callback(
    [Output(component_id='trafficpattern',component_property='figure')],
    [Input(component_id='update-button', component_property='n_clicks'),
    State(component_id='date-picker',component_property='start_date'),
    State(component_id='date-picker',component_property='end_date'),
    State(component_id='location-dropdown',component_property='value')]
)
def update_tf_graph(n_clicks,sdate,edate,loc):
    if n_clicks > 0:
        loc = [loc[i].split('-')[0] for i in range(len(loc))]
        sql = gcb.standard_query(start_date=sdate, end_date=edate)
        results = DFplot(gcb.query(sql))
        results = results.replace({'vd': vd_dict})
        results = results[results['vd'] != '29.600']
        return [results.plot_traffic_pattern(loc)]

if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=False, host='0.0.0.0', port=8050)