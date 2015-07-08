#!/usr/bin/python

"""
Create a 1024-host network, and run the CLI on it.
If this fails because of kernel limits, you may have
to adjust them, e.g. by adding entries to /etc/sysctl.conf
and running sysctl -p. Check util/sysctl_addon.
"""

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch
from mininet.topolib import TreeNet

import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import collections
import seaborn as sns
import csv

all_topos={}
rttavg=[]
rttmin=[]
rttmax=[]
rttstd=[]
sent=[]
rec =[]
packLoss=[]
rttavg_dic={}
rttavg_val=[]
all_perf = {}
avg_perf = {}
perf_val=[]

def iperf_clean(perf):
    temp =[]
    for i in perf:
        if i is not '':
            temp.append(i.strip(' Gbits/sec'))
    return temp

def iperf_avg(perf):
    temp =[]
    for i in perf:
        temp.append(float(i))
    return numpy.average(temp)

def run_mininet(depth_val):
    for i in depth_val:
        network = TreeNet( depth=i, fanout=2, switch=OVSKernelSwitch )
        network.start()
        all_topos[i]=network.pingAllFull()
        all_perf[i]=network.iperf(fmt='g')
        proc_ping(i)
        proc_iperf(i)
        network.stop()

def proc_ping(nws):
    rttavg_dic[0]=0
    for x in all_topos[nws]:
        sent.append(x[2][0])
        rec.append(x[2][1])
        rttmin.append(x[2][2])
        rttavg.append(x[2][3])
        rttmax.append(x[2][4])
        rttstd.append(x[2][5])
    rttavg_dic[2**nws] = numpy.average(rttavg)
    save_csv_ping(nws)
    rec[:]=[]
    sent[:]=[]
    rttmin[:]=[]
    rttavg[:]=[]
    rttmax[:]=[]
    rttstd[:]=[]

def proc_iperf(nws):
    avg_perf[0]=0
    perf = all_perf[nws]
    perf = iperf_clean(perf)
    perf = iperf_avg(perf)
    avg_perf[2**nws] = perf
    save_csv_iperf(nws)

def mini_plot():
    rttavg_sort = sorted(rttavg_dic.keys())
    print rttavg_dic 
    print avg_perf
    for t in rttavg_sort:
        rttavg_val.append(rttavg_dic[t])
    
    perf_sort = sorted(avg_perf.keys())
    for t in perf_sort:
        perf_val.append(avg_perf[t])

    f,axrr=plt.subplots(1,2)

    axrr[0].plot(rttavg_sort, rttavg_val, linestyle="dashed", marker="o")
    axrr[0].set_title('Depth and Delay')
    axrr[0].set_xlabel('Depth')
    axrr[0].set_ylabel('Delay')
    
    axrr[1].plot(perf_sort, perf_val ,linestyle="dashed", marker="o");
    axrr[1].set_title('Depth and Bandwidth')
    axrr[1].set_xlabel('Depth')
    axrr[1].set_ylabel('Bandwidth')

    plt.savefig('test'+time.strftime("%S_%M_%H_%d_%m_%Y")+'.png')
    plt.close() 

def save_csv_ping(nws):
    b = open('data_ping_depth'+str(nws)+'.csv','w')
    a = csv.writer(b)
    a.writerow(('rec','sent','rttmin','rttavg','rttmax','rttstd'))
    for i in range(len(rttavg)):
        a.writerow((rec[i], sent[i], rttmin[i], rttavg[i], rttmax[i], rttstd[i]))
    b.close()

def save_csv_iperf(nws):
    b = open('data_ping_iperf'+str(nws)+'.csv','w')
    a = csv.writer(b)
    a.writerow(('host', 'bandwidth'))
    for key,value in avg_perf.items():
        a.writerow((key,value))
    b.close()

if __name__ == '__main__':
    setLogLevel( 'info' )

    run_mininet(range(3,10))
    mini_plot()

