import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from variables import vd_id, vd_name, vd_dict

class DFplot(pd.DataFrame):
    palette = ['#007bff','#6610f2','#6f42c1','#e83e8c','#dc3545','#fd7e14','#ffc107','#28a745','#20c997','#17a2b8']
    width = 1344
    height = 1008
    _column_names = ['time_tz','vd','volume','speed','occupancy']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @property
    def _constructor(self):
        if len(set(DFplot._column_names) & set(self.columns.to_list())) != len(set(DFplot._column_names)):
            raise Exception("DFplot dataframe must include these columns: {}, {}, {}, {}, {}".format(*DFplot._column_names))
        else:
            return DFplot

    def plot_fundamental_d(self):
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{}, {}],
                    [{}, None]],
            horizontal_spacing=0.1,
            vertical_spacing=0.1,
            subplot_titles=('Speed-Occupany Diagram',
                            'Speed-Flow Diagram',
                            'Flow-Occuoancy Diagram'),
        )

        for vd, vd_group in self.groupby(['vd']):
            c = DFplot.palette[vd_id.index(vd)%10]
            marker = dict(size=4,color=c)
            fig.add_trace(go.Scatter(x=vd_group.occupancy, y=vd_group.speed, name=f"VD {vd} K", legendgroup=f"VD {vd} K", mode='markers',marker=marker), row=1,col=1)
            fig.add_trace(go.Scatter(x=vd_group.volume, y=vd_group.speed, name=f"VD {vd} K", legendgroup=f"VD {vd} K", showlegend=False, mode='markers',marker=marker), row=1,col=2)
            fig.add_trace(go.Scatter(x=vd_group.occupancy, y=vd_group.volume, name=f"VD {vd} K", legendgroup=f"VD {vd} K", showlegend=False, mode='markers',marker=marker), row=2,col=1)

        fig.update_layout(
            autosize=False,
            width=DFplot.width,
            height=DFplot.height,
            # set fig, x and y axis tiltles & font
            title='Multi VD Comparison Fundemental Diagram',
            xaxis_title="Flow (veh/hr)",
            yaxis_title="Speed (km/hr)",
            font=dict(
                #family="Courier New, monospace",
                size=16,
                #color="RebeccaPurple",
                color="#411530"
            ),
            showlegend = True,
            legend_title_text='VD Location'
        )
        # Update yaxis properties
        fig.update_yaxes(
            title_text="Speed (km/hr)", 
            range=[0, 100],
            minor=dict(ticklen=6, tickcolor="black", showgrid=True), 
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=1)
        fig.update_yaxes(
            title_text="Speed (km/hr)",
            range=[0, 100],
            minor=dict(ticklen=6, tickcolor="black", showgrid=True),
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=2)
        fig.update_yaxes(
            title_text="Flow (veh/hr)",
            range=[0, 3500],
            minor=dict(ticklen=6, tickcolor="black", showgrid=True),
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)

        # Update xaxis properties
        fig.update_xaxes(
            title_text="Occupany (%)",
            range=[0, 100],
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=1)
        fig.update_xaxes(
            title_text="Flow (veh/hr)",
            range=[0, 3500],minor=dict(ticklen=6, tickcolor="black", showgrid=True),
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=2)
        fig.update_xaxes(
            title_text="Occupany (%)",
            range=[0, 100],
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)
        return fig

    def plot_speedflow_d(self):
        col_num = 4
        locations = list(self.groupby(['vd']).groups.keys())
        if len(locations)%col_num == 0:row_num = (len(locations)//col_num)
        else:row_num = ((len(locations)//col_num)+1)
        fig = make_subplots(
            rows=row_num, cols=col_num,
            specs=[[
                {"rowspan": 1,"colspan": 1},
                {"rowspan": 1,"colspan": 1},
                {"rowspan": 1,"colspan": 1},
                {"rowspan": 1,"colspan": 1}] for x in range(row_num)],
            subplot_titles=['VD '+l+' K' for l in locations],
            shared_yaxes=True
        )

        rcount, ccount = 1, 1
        marker = dict(size=4,color='#6f42c1')
        for vd, vd_group in self.groupby(['vd']):
            fig.add_trace(go.Scatter(x=vd_group.volume, y=vd_group.speed, name=f"VD {vd} K", mode='markers',marker=marker),row=rcount,col=ccount)
            if ccount%4 == 0: 
                ccount=1
                rcount+=1
            else: ccount += 1

        fig.update_layout(
            autosize=False,
            height=400*row_num,
            width=(DFplot.width/4)*col_num,
            # set fig, x and y axis tiltles & font
            title=' Speed-Flow Diagram',
            font=dict(
                #family="Courier New, monospace",
                size=16,
                #color="RebeccaPurple",
                color="#411530"
            ),
            showlegend = False
        )
        fig.for_each_xaxis(lambda x: x.update(range=[0,3500]))
        fig.for_each_yaxis(lambda x: x.update(range=[0,100]))
        return fig

    def plot_traffic_pattern(self, loc):
        row_num, col_num = 3,1
        fig = make_subplots(
            rows=row_num, cols=col_num,
            specs=[[{}],[{"rowspan": 2}],[None]],
            subplot_titles=['Hour of Day Flow Pattern','Speed Heat Map over Time & Spatial']
        )
        fig.update_layout(
            autosize=False,
            width=self.width,
            height=1080,
            # set fig, x and y axis tiltles & font
            title='Day by Day Trffic Pattern',
            font=dict(
                #family="Courier New, monospace",
                size=16,
                #color="RebeccaPurple",
                color="#411530"
            )
        )
        self.__plot_time_series_flow(loc,fig)
        self.__plot_speed_heatmap(fig)
        return fig

    def __plot_time_series_flow(self, loc, fig):
        for vd, vd_group in self.groupby(['vd']):
            if vd in loc:
                c = DFplot.palette[loc.index(vd)%10]
                marker = dict(size=4,color=c)
                trace = go.Scatter(x=vd_group.time_tz,y=vd_group.volume,name=f"VD {vd} K",mode='lines+markers',showlegend=True,marker=marker)
                fig.add_trace(trace,row=1,col=1)

    def __plot_speed_heatmap(self, fig):
        self.speed = self.speed.fillna(90)
        self.speed[(self.speed == 0) & (self.volume == 0)] = 90
        Z = self.pivot(index='vd', columns='time_tz', values='speed')
        Z.rename(index=vd_dict, inplace=True)
        Z.index = Z.index.astype(float)
        Z.sort_index(inplace=True)
        Z.index = Z.index.astype(str)
        X = Z.columns.to_list()
        Y = Z.index.to_list()
        trace = go.Heatmap(z=Z,x=X,y=Y,
                    hoverongaps = False,
                    colorscale='portland',
                    #reverse color bar
                    reversescale=True,
                    colorbar=dict(
                        title="Speed",
                        thicknessmode="pixels", thickness=30,
                        lenmode="pixels", len=1008*0.67,
                        #set color position base on top side
                        yanchor="top",y=0.7,
                        ticks="outside", ticksuffix=" (km/hr)",
                        dtick=20))
        fig.add_trace(trace,row=2,col=1)
        fig.update_yaxes(
            autorange="reversed",
            title_text="VD Location (veh/hr)", 
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)
        fig.update_xaxes(
            title_text="Time",
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)
