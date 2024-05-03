import pandas as pd
from dash import Dash, dcc, html

from variables import vd_id, vd_name, vd_dict

corporate_colors = {
    'dark_blue': '#14274E',
    'gray_blue': '#394867',
    'light_blue': '#D0E8F2',
    'gray_white': '#D0E8F2',
    'white': '#FFFFFF'
}
c_class = {
    'psc': '小客車(Passnger Car)',
    'bus': '客運(Highway Bus)',
    'truck': '拖車(Truck)'
}
weekdays_dict = {0:"Monday", 1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday", 6:"Sunday"}
########## tabs inline style ##########
tabs_style = {
    'width':'70vw',
    'height': '60px'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'borderRadius': '10px',
    'backgroundColor': 'navy',
    'color': 'white',
    'paddingTop': '16px',
}
########## layout design ##########
date = html.Div([
    html.P("Date", className='labels'),
    html.Div([
        dcc.DatePickerRange(
            display_format='YYYY-MM-DD',
            start_date = '2020-11-08',
            end_date = '2020-11-14',
            min_date_allowed = '2020-11-01',
            max_date_allowed = '2020-12-31',
            minimum_nights = 0,
            id = 'date-picker')
    ])
])

loc = html.Div([
    html.P("VDLocation", className='labels'),
    html.Div([
        dcc.Dropdown(
            multi=True,
            options = [vd_id[i]+'-K' for i in range(len(vd_id))],
            value=['26.705-K'],
            id = 'location-dropdown',
            maxHeight=800),
        dcc.Store(data='26.705-K',id='location-dropdown-active')
    ])
])

car = html.Div([
    html.P("Car Class", className='labels'),
    html.Div([
        dcc.Dropdown(
            multi=True,
            options = list(c_class.values()),
            value='Montreal',
            id = 'car-dropdown')
    ])
])

time = html.Div([
    html.P("Time", className='labels'),
    html.Div([
        dcc.RangeSlider(
            0, 24,0.5, value=[14.0, 18.0],
            marks={i: str(i) for i in range(0,25,1)},
            id = 'time-slider')
    ])
])

weekdays = html.Div([
    html.P("DayofWeek", className='labels'),
    html.Div([
        dcc.Checklist(
            options = [
            {'label': v, 'value': k}
            for k, v in weekdays_dict.items()
            ],
            value = list(weekdays_dict.keys()),
            inline = True,
            id = 'weekdays'),
        dcc.Store(data=list(weekdays_dict.keys()),id='weekdays-active')
    ])
])

update = html.Div([
    html.Button("Update", n_clicks=0, id='update-button')
])

tabs = dcc.Tabs([
        dcc.Tab(label='Fundamental Diagram',value='Fundamental-Diagram', selected_style=tab_selected_style),
        dcc.Tab(label='Speed Flow Diagram',value='Speed-Flow-Diagram', selected_style=tab_selected_style),
        dcc.Tab(label='Hour of Day Traffic Pattern',value='Hour-of-Day-Traffic-Pattern', selected_style=tab_selected_style),
],value='Fundamental-Diagram',id='graphtabs',style=tabs_style)

fd_plot = dcc.Graph(id='fundamental_d')
sfd_plot = dcc.Graph(id='speedflow_d')
tp_plot = dcc.Graph(id='trafficpattern')

side_bar = html.Div([
    html.Div([html.H1(['Traffic Performance Dashboard'])],className = 'objbox'),
    html.Div([
        html.A(
            [html.Img([],id = 'linkedin', alt='Link to LinkedIn', src = ('assets/linkedin_icon.png'))],
            href="https://www.linkedin.com/in/haoyu-yang-a474b0247", target="_blank"
        ),
        html.A(
            [html.Img([],id = 'mail', alt='Link to Mail Address', src = ('assets/mail_icon.png'))],
            href="mailto:r08521524@ntu.edu.tw", target="_blank"
        ),
        html.A(
            [html.Img([],id = 'essay', alt='Link to My Essay', src = ('assets/essay_icon.png'))],
            href="https://hdl.handle.net/11296/3sr735", target="_blank"
        )
    ],className = 'objbox'),
    html.Div([
        html.P([
            '這是依據交通部高速公路局「交通資料庫」提供之車流數據，所製作的"非官方"交通狀況儀表板。',
            '涵蓋國道5號北上方向全線(不包含匝道)，數據資料為各車輛偵測器測得之：\n',
            '\t•  車流量( Flow，veh/hr )\n',
            '\t•  車流速率( Speed，km/hr )\n',
            '\t•  佔有率( Occupancy，% )\n',
            '此儀表板以每5分鐘為基礎單位進行分析，可分析項目包含：\n',
            '○  基本構圖( Fundmantal Diagram )：\n\t基本構圖能表示流量、速率和密度三者之間的關係，用於分析道路容量'
            '也可觀察在不同條件下道路容量會如何變化，並找出關鍵密度、關鍵速率對交通狀況進行績效評估。\n'
            '○  速率-流量基本構圖比較\n( Speed-Flow Diagram )：\n\t包含在基本構圖中的速率-流量構圖，能以較直觀的方式呈現車流速率如何隨流量變化，'
            '並判斷交通是自由車流狀態、穩定狀態或不穩定狀態三種狀態之一。\n'
            '○  日交通型態( Traffic Pattern )：\n\t以流量的時間序列圖搭配速率時空熱圖，快速找出衝擊波發生的時間、地點以及影響範圍，以更宏觀的角度分析所採取的交通管制措施對交通狀態的變化。'
        ],className='sidebartxt')
    ],className = 'objbox'),
    html.Div([
        html.A(
            [html.Img([],id = 'motc', alt='Link to TISV Cloud', src = ('assets/FBMOTC_icon.png'))],
            href='https://tisvcloud.freeway.gov.tw/', target="_blank"
        )
    ],className = 'objbox')
],id = 'sidebar')

main_content=html.Div([
    html.Div([
        #control panel
        html.Div([
            #filiter1
            html.Div([
                html.Div([date],id = 'date-box',className='box'),
                html.Div([loc],id = 'loc-box',className='box')
            ],className = 'row'),
            #html.Br(),
            
            #filiter2
            html.Div([
                html.Div([time],id = 'time-box',className='box'),
            ],className = 'row'),
            #html.Br(),
            
            #filiter3
            html.Div([
                #weekdays
                html.Div([weekdays],id = 'week-box',className='box'),
                #update botton
                html.Div([update],id = 'botton-box')
            ],className = 'row'),
            #html.Br(),
        ],id = 'control-panel'),
    ],className = 'page'),

    html.Div([
        #graph area
        #html.Div(html.Div([tabs],id='graph-content'),className = 'graph-area')
        html.Div([
            #tabs
            html.Div([
                tabs
            ],style={
                    'position': 'relative',
                    'height': 'auto',
                    'width': 'auto',
                    'marginBottom':'-1px'
            },className = 'row'),
            html.Div(id='graphs',className='graph-content')
        ],id = 'graph-area')
    ],className = 'page')
],id = 'maincontent')

Layout = html.Div([side_bar,main_content],className = 'page')