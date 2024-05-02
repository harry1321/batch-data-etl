import os
from pathlib import Path
import gzip
import requests
import shutil
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

class GenData:
    def __init__(self):
        #!!重要!!可視需要更改下載檔案儲存位置
        self.subdir = Path.cwd().joinpath(*['data','downloadzip'])
        self.spath = Path.cwd().joinpath(*['data','unprocessed'])
        self.URL = 'https://tisvcloud.freeway.gov.tw/history/motc20/VD/'
        self.VD_LIST = 'https://raw.githubusercontent.com/harry1321/Traffic-Dashboard/test/data/vd_static_mainline.csv'
        
        #建立資料夾
        if Path.is_dir(self.subdir):
            pass
        else:
            Path.mkdir(self.subdir, parents=True)

    def download_data(self, url):
        target_path = self.subdir.joinpath(*[url.split('/')[-1]])
        file_name = os.getcwd() + '/data/downloadzip/' + url.split('/')[-1].split('.')[0]+'.xml'
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(response.raw.read())
        with gzip.open(target_path, 'rb') as f_in:
            with open(file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return file_name

    #VD 2.0
    #資料處理從XML抓資料
    def get_data(self, file_name, time, vd_list, speed, occ, psg, lag, tr):
        #xml namespace
        NS = 'http://traffic.transportdata.tw/standard/traffic/schema/'
        tree = ET.parse(file_name)
        root = tree.getroot()

        for vd in vd_list:
            #find specific VD
            for vd_id in root.findall("./{%s}VDLives/{%s}VDLive/[{%s}VDID = '%s']"%(NS,NS,NS,vd)):
                lane_count = 0
                veh_count = 0
                psg_count = 0
                lag_count = 0
                tr_count = 0
                wavg_speed = 0.0
                avg_occ = 0
                
                #find lanes in each VD
                for lane in vd_id.iter("{%s}Lane"%NS):
                    if int(lane.find("{%s}LaneID"%NS).text) < 2:#不含路肩資料
                        lane_count += 1
                        #print(lane.find("{%s}LaneType"%NS).text,lane.find("{%s}LaneID"%NS).text)
                        
                        #抓佔有率資料
                        if int(lane.find("{%s}Occupancy"%NS).text) >= 0 and avg_occ != -999:
                            avg_occ += int(lane.find("{%s}Occupancy"%NS).text)
                        else:
                            avg_occ = -999 #error code
                        
                        #抓速率跟流量
                        for veh in lane.iter("{%s}Vehicle"%NS):
                            veh_type = veh.find("{%s}VehicleType"%NS).text
                            #流量
                            veh_volume = int(veh.find("{%s}Volume"%NS).text)
                            #速率
                            veh_speed = int(veh.find("{%s}Speed"%NS).text)
                            #分車種計
                            if veh_type == 'S':
                                psg_count += veh_volume
                            elif veh_type == 'L':
                                lag_count += veh_volume
                            elif veh_type == 'T':
                                tr_count += veh_volume
                                #print("Truck!!")
                            
                            #重新估計速率
                            veh_count += veh_volume
                            if veh_speed >= 0 and wavg_speed != -999:
                                wavg_speed += veh_speed*veh_volume
                            else:
                                wavg_speed = -999 #error code

                #save flow, speed, occ into dataframe
                if veh_count != 0: speed.loc[time, vd] = wavg_speed/veh_count
                occ.loc[time, vd] = avg_occ/lane_count #佔有率
                psg.loc[time, vd] = psg_count*60 #小車流量
                lag.loc[time, vd] = lag_count*60 #大型車流量
                tr.loc[time, vd] = tr_count*60 #聯結車流量

    #以2021/05/30 10:00至14:00為例 格式為date=20210530,start_time=1000,end_time=1400
    def gen_data(self, date, start_time=0, end_time=2359):
        #create time index
        time = [int(i/60)*100+i%60 for i in range(0,1439)]
        for i in range(0,10): time[i] = '000' + str(time[i])
        for i in range(10,60): time[i] = '00' + str(time[i])
        for i in range(60,600): time[i] = '0' + str(time[i])
        for i in range(600,1439): time[i] = str(time[i])

        URL = self.URL + date + "/"

        #重要
        #這裡需要讀取你所需的VD編碼
        #get vd list
        col = pd.read_csv(self.VD_LIST, encoding='big5')
        col = col.iloc[:,0]
        cols = [ col[i] for i in range(0,len(col))]
        
        #create new dataframe
        vd_list = cols
        rows = [ i for i in range(0,1439)]
        #速率
        speed = pd.DataFrame(np.zeros([len(rows),len(cols)]), columns = col, index = rows)
        #佔有率
        occ = pd.DataFrame(np.zeros([len(rows),len(cols)],dtype='int'), columns = col, index = rows)
        #小客車流量
        psg = pd.DataFrame(np.zeros([len(rows),len(cols)],dtype='int'), columns = col, index = rows)
        #大客車流量
        lag = pd.DataFrame(np.zeros([len(rows),len(cols)],dtype='int'), columns = col, index = rows)
        #大型車流量
        tr = pd.DataFrame(np.zeros([len(rows),len(cols)],dtype='int'), columns = col, index = rows)
        
        start_time = int(start_time/100)*60+start_time%100
        end_time = int(end_time/100)*60+end_time%100
        print(start_time,end_time)
        #load data from tisvcloud
        for i in range(start_time,end_time):
            url = URL + 'VDLive_' + time[i] + '.xml.gz'
            print(url)
            
            processing_file = self.download_data(url)
            self.get_data(processing_file, i, vd_list, speed, occ, psg, lag, tr)
            
            os.remove(processing_file)
            os.remove(self.subdir + 'VDLive_' + time[i] +'.xml.gz')
        
        flow = psg.add(lag, fill_value=0)
        flow = flow.add(tr, fill_value=0)

        subdir = self.spath.joinpath(*[date])
        #自動依日期建立資料夾，名稱為日期
        if Path.is_dir(subdir):
            print(f"Folder path: {subdir} exists.")
            flow.to_csv(subdir.joinpath(*[f'{date}_volume_1min.csv']), sep=',', encoding = 'big5')
            speed.to_csv(subdir.joinpath(*[f'{date}_speed_1min.csv']), sep=',',encoding='big5')
            occ.to_csv(subdir.joinpath(*[f'{date}_occupancy_1min.csv']), sep=',',encoding='big5')
            psg.to_csv(subdir.joinpath(*[f'{date}_psg_1min.csv']), sep=',',encoding='big5')
            lag.to_csv(subdir.joinpath(*[f'{date}_lag_1min.csv']), sep=',',encoding='big5')
            tr.to_csv(subdir.joinpath(*[f'{date}_tr_1min.csv']), sep=',',encoding='big5')
        else:
            Path.mkdir(subdir, parents=True)
            flow.to_csv(subdir.joinpath(*[f'{date}_volume_1min.csv']), sep=',', encoding = 'big5')
            speed.to_csv(subdir.joinpath(*[f'{date}_speed_1min.csv']), sep=',',encoding='big5')
            occ.to_csv(subdir.joinpath(*[f'{date}_occupancy_1min.csv']), sep=',',encoding='big5')
            psg.to_csv(subdir.joinpath(*[f'{date}_psg_1min.csv']), sep=',',encoding='big5')
            lag.to_csv(subdir.joinpath(*[f'{date}_lag_1min.csv']), sep=',',encoding='big5')
            tr.to_csv(subdir.joinpath(*[f'{date}_tr_1min.csv']), sep=',',encoding='big5')
