#!/usr/bin/env python3
import subprocess
import re
import pickle
import time
import json
import os

try:
    data = pickle.load(open("modem_status.pickle","rb"))
    print("Loaded old data, size: ",len(data))
except Exception as ex:
    print("Old data could not be loaded",str(ex))
    data = []

arfcn_seq = [638016]
#arfcn_seq = range(638016,638200,2)
#arfcn_seq = range(620000,653332,2*100) # 2* because 30kHz
#https://www.sqimway.com/nr_band.php
# Band n78 min/max arfcn: 620000 653332 for 30kHz

arfcn_state = -1
arfcn_iterations = 9999999

class ModemWrapper(object):
    def __init__(self, port):
        import serial
        self.port = serial.Serial(port,baudrate=115200,timeout=1)
        import time
        #time.sleep(2) # Nice race condition in quectel fw otherwise!
        
        # consume all stale output
        while True:
            resp = self.port.readline()
            print(resp)
            if resp == b'':
                break
        
        self.port.write('AT\r\n'.encode('utf-8'))
        print(self.port.readline())
        print(self.port.readline())
        print(self.port.readline())
        print(self.port.readline())
        print("Connection ready")
        #print("Setting: ",self.port)
    
    def query(self, s):
        self.port.write((s+'\r\n').encode('utf-8'))
        results = []
        for read_idx in range(10):
            resp = self.port.readline()
            if resp == b'\r\n':
                continue
            #print("read_idx=",read_idx,"got line",resp.decode('utf-8').strip())
            if resp == b'OK\r\n':
                if len(results)>0:
                    #print("returning",results)
                    return results
                else:
                    raise Exception("No result from query \"",s,"\"")
            #print("appending")
            results.append(resp.decode('utf-8').strip())
        raise Exception("Timeout from query \"",s,"\"")
    
    def query_servingcell(self):
        raw_list = self.query('AT+QENG="servingcell"')
        results = {}
        for raw in raw_list:
            #raw = '+QENG: "servingcell","NOCONN","LTE","FDD",302,720,99B815,0,675,2,4,4,73A0,-67,-6,-42,26,0,-,60'
            #raw = '+QENG: "NR5G-NSA",302,720,0,-60,30,-11,638016,78,8,1'
            #print("raw=",raw)
            import re
            if raw.find("LTE")!=-1:
                res1 = re.match(r'\+QENG: "LTE","(?P<is_tdd>.*?)",(?P<MCC>.*?),(?P<MNC>.*?),(?P<cellid>.*?),(?P<pcid>.*?),(?P<earfcn>.*?),(?P<freq_band_ind>.*?),(?P<UL_bandwidth>.*?),(?P<DL_bandwidth>.*?),(?P<TAC>.*?),(?P<RSRP>.*?),(?P<RSRQ>.*?),(?P<RSSI>.*?),(?P<SINR>.*?),(?P<CQI>.*?),(?P<tx_power>.*?),(?P<SRXLEV>.*?)',raw)
                res2 = re.match(r'\+QENG: "servingcell","NOCONN","LTE","(?P<is_tdd>.*?)",(?P<MCC>.*?),(?P<MNC>.*?),(?P<cellid>.*?),(?P<pcid>.*?),(?P<earfcn>.*?),(?P<freq_band_ind>.*?),(?P<UL_bandwidth>.*?),(?P<DL_bandwidth>.*?),(?P<TAC>.*?),(?P<RSRP>.*?),(?P<RSRQ>.*?),(?P<RSSI>.*?),(?P<SINR>.*?),(?P<CQI>.*?),(?P<tx_power>.*?),(?P<SRXLEV>.*?),(?P<dltime>.*?)',raw)
                if not res1 and not res2:
                    print("Failed to match response: \""+raw+"\"")
                    continue
                if res1 and res2:
                    print("LTE mode: logic error")
                    continue
                if res1:
                    res = res1
                if res2:
                    res = res2
                #print("LTE mode, res=",res)
                results.update({'LTE': res.groupdict()})
            elif raw.find("NR5G-NSA")!=-1:
                res = re.match(r'\+QENG: "NR5G-NSA",(?P<MCC>.*?),(?P<MNC>.*?),(?P<pcid>.*?),(?P<rsrp>.*?),(?P<sinr>.*?),(?P<rsrq>.*?),(?P<arfcn>.*?),(?P<band>.*?),(?P<NR_DL_bandwidth>.*?),(?P<scs>.*?)',raw)
                if not res:
                    print("Failed to match response: \""+raw+"\"")
                    continue
                #print("5G mode, res=",res)
                results.update({'5G': res.groupdict()})
            elif raw=='+QENG: "servingcell","NOCONN"':
                #print("normal result")
                pass
            elif raw=='AT+QENG="servingcell"':
                #print("normal result")
                pass
            else:
                print("connection type unknown",raw)
        return results

m = ModemWrapper('/dev/ttyUSB2')

counter = 0

while True:
    blob = {
        'timestamp': time.time()}
    
    try:
        blob.update(m.query_servingcell())
    except Exception as ex:
        print("Exception getting serving cell info",ex, flush=True)
    
    print(blob, flush=True)
    
    try:
        data.append(blob)
        if counter % 300 == 0: # 300s
            cutoff_timestamp = time.time() - 3600 * 24 * 14
            data = list(filter(lambda x: x['timestamp'] > cutoff_timestamp, data))
            #print("reduced data size: ",len(new_data))
            pickle.dump(data,open("modem_status.pickle.tmp","wb"))
            import os
            os.rename("modem_status.pickle.tmp","modem_status.pickle") # overwrite old db
        
        if counter % 300 == 0: # 300s
            subprocess.check_output("./teleop_plotter.py modem_status.pickle", shell=True)
            subprocess.check_output("curl -s -T bandwidth_over_time_of_day.pdf https://robohub.eng.uwaterloo.ca/share/",shell=True)
            subprocess.check_output("curl -s -T bandwidth_over_time.pdf https://robohub.eng.uwaterloo.ca/share/",shell=True)
    except Exception as ex:
        print("Exception",ex, flush=True)
    
    time.sleep(1) # TODO: fixed wait
    counter = counter + 1
