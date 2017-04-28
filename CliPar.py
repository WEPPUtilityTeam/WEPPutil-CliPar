import csv, argparse
from collections import Counter

import numpy as np
from math import floor

#Created by Dylan Quinn (quinnd@uidaho.edu, dylansquinn@gmail.com)

#This material is based upon work supported by the National Science 
#Foundation under grant no. DMS-1520873


'''
Creates a '.par' file for input into the WEPP or Cligen programs from 15 mintue climate data

Input ('.csv'):
datetime            temp     humid      srad    ws    prcp    wdir
mm/dd/yyyy hh:mm    deg C    percent    W/m2    m/s   mm      degrees from N
...
ex.
datetime          temp   humid    srad    ws    prcp    wdir
4/26/2008 3:15    5.1    61       0       0.3   0       291.9
4/26/2008 3:30    5.4    57       0       0.3   0       282.1
4/26/2008 3:45    5.1    57       0       0.2   0       262

Output ('.par'):
A cligen '.par' file describing monthly climate parameters as mean, std dev, and skewedness.

*Headder information including Station Name, Station Number, Latt, Long, and Elevation may
    require manual editing after the file is created.


References:
Cligen Parameter input file documentation (accessed 03/01/2017) - 
    https://www.ars.usda.gov/ARSUserFiles/50201000/WEPP/cligen/cligenparms.pdf
    
'''



def windDirection(deg):
    if deg >=0.0 and deg < 11.25:  
        return 'N'
    elif deg >=11.25 and deg < 33.75:   
        return 'NNE'
    elif deg >=33.75 and deg < 56.25:  
        return 'NE'
    elif deg >=56.25 and deg < 78.75:  
        return 'ENE'
    elif deg >=78.75 and deg < 101.25:  
        return 'E'
    elif deg >=101.25 and deg < 123.75:  
        return 'ESE'
    elif deg >=123.75 and deg < 146.25:  
        return 'SE'
    elif deg >=146.25 and deg < 168.75:  
        return 'SSE'
    elif deg >=168.75 and deg < 191.25:  
        return 'S'
    elif deg >=191.25 and deg < 213.75:  
        return 'SSW'
    elif deg >=213.75 and deg < 236.25:  
        return 'SW'
    elif deg >=236.25 and deg < 258.75:  
        return 'WSW'
    elif deg >=258.75 and deg < 281.25:  
        return 'W'
    elif deg >=281.25 and deg < 303.75:  
        return 'WNW'
    elif deg >=303.75 and deg < 326.25:  
        return 'NW'
    elif deg >=326.25 and deg < 348.75:  
        return 'NNW'
    elif deg >=348.75 and deg <= 360.0:  
        return 'N'
    else:
        return "NA"

def dateparse(datetime):
    '''Returns a list of date components ([YEAR, YYYY], [MONTH, MM], [DAY, DD], 
     from a string (eg. "mm/dd/yyyy hh:mm")'''
    try:
        date = datetime.split(" ")[0]
        (m,d,y) = date.split("/") 
        return {'y':y, 'm':m, 'd':d}
    except:
        pass


if __name__ == "__main__":
    
    #treat numpy errors as real errors
    np.seterr(all='raise')
    
        #fin = "sotonera.csv"
    fin = "test.csv"
    fout = "test.par"
    
    
   #Create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input 15 minute climate data file name (\'*.csv\')')
    parser.add_argument('-o', '--output', help='Output parameter file name (\'*.par\')')
    args = parser.parse_args()
    
    #handel arguments
    if args.input:
        fin = args.input
    else:
        fin = raw_input('Input 15 minute climate data file name (\'*.csv\'): ')
        
    if '.csv' not in fin:
        print "Using test input file"
        fin = "test.csv"
    
    if args.output:
        fout = args.fout
    else:
        fout = raw_input('Output parameter file name (\'*.par\'): ')
    if '.par' not in fout:
        print "Using test output file"    
        fout = "test.par"
        

    with open(fin, 'rb') as filereader:
        with open(fout, 'w') as o:
            data_arr = csv.DictReader(filereader)
            
            
            
            prcp_hist_list = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0] #moving window of precip, 2 hours
            prcp_hist6_list = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                              0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                              0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0] #moving window of precip, 6 hours
            prcp30_list = [0,0]
            t=0
            pmax = 0
            tf = 0
            tmax = 0
            prcp30_max = 0
            prcp30_record = 0
            prcp6_record = 0
            daynum = 0
            daycount = 0
            srad_list = []
            templistall = []
            calm_list = []
            day0 = []
            day1 = []
            dtempmax = None
            dtempmin = None
            months_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            dd = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            ww = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            wd = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            ttp_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            dew_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            srad_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            tempmax_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            tempmin_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            prcp30_max_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}
            calm_dic = {'1':[0,0],'2':[0,0],'3':[0,0],'4':[0,0],'5':[0,0],'6':[0,0],'7':[0,0],'8':[0,0],'9':[0,0],'10':[0,0],'11':[0,0],'12':[0,0]}
            
            for row in data_arr:
                if row['datetime'] == '' or row['prcp'] == '':
                    prcp_hist_list.insert(0,0.0)
                    prcp_hist_list.pop()
                    prcp30_list.insert(0,0.0)
                    prcp30_list.pop()
                    prcp_hist6_list.insert(0,0.0)
                    prcp_hist6_list.pop()
                    continue
                else:
                    #c    %    w/m2    m/s    mm    degrees
                    try:
                        row['prcp'] = float(row['prcp'])/25.4 #mm to in
                    except:
                        pass
                    try:
                        row['temp'] = float(row['temp'])*1.8+32 #C to F
                    except:
                        pass
                        #row['humid'] = float(row['humid']) #percent
                    try:
                        row['srad'] = float(row['srad'])/0.484583 #w/m2 to lang
                        #row['ws'] = float(row['ws']) ##m/s to 
                        #row['wdir'] = float(row['wdir']) #deg
                    except:
                        pass
                    
                    
                    date = dateparse(row['datetime'])
                    p = float(row['prcp'])
                    
                    
                    prcp_hist_list.insert(0,p)
                    prcp_hist_list.pop()
                    prcp_hist6_list.insert(0,p)
                    prcp_hist6_list.pop()
                    prcp30_list.insert(0,p)
                    prcp30_list.pop()
                    try:
                        if float(row['ws'])<=0.3:
                            calm_dic[date['m']][0] +=1
                        else:
                            calm_dic[date['m']][1] +=1
                    except:
                        pass    
                    if daynum == 0:
                        #its the beginning of the file
                        daynum = int(date['d'])
                        day1.append(p)
                        dtempmax = row['temp']
                        dtempmin = row['temp']
                        srad_list.append(float(row['srad']))
                    elif int(date['d']) == daynum:
                        # its the same day
                        if dtempmax < row['temp']:
                            dtempmax = row['temp']
                        if dtempmin > row['temp']:
                            dtempmin = row['temp']
                        if sum(prcp30_list)> prcp30_max:
                            prcp30_max = sum(prcp30_list)
                        day1.append(p)
                        try:
                            srad_list.append(float(row['srad']))
                        except:
                            pass
                    else:
                        daynum = int(date['d'])
                        daycount += 1
                        #its the next day
                        try:
                            tempmin_dic[date['m']].append(round(float(dtempmin)))
                            tempmax_dic[date['m']].append(round(float(dtempmax)))
                        except:
                            pass
                        if prcp30_max>0:
                            prcp30_max_dic[date['m']].append(prcp30_max/.5)
                        prcp30_max = 0
                        if sum(prcp30_list)> prcp30_max:
                            prcp30_max = sum(prcp30_list)
                        if sum(day1)>0 and sum(day0)>0:
                            #wet wet
                            ww[date['m']].append(sum(day1))
                        elif sum(day1)>0 and sum(day0)<=0:
                            wd[date['m']].append(sum(day1))
                            #wetdry
                        else:
                            #dry dry or dry wet
                            dd[date['m']].append(sum(day1))     
                        srad_dic[date['m']].append(np.mean(srad_list))    
                        dtempmax = row['temp']
                        dtempmin = row['temp']
                        day0 = day1
                        day1 = []
                        srad_list = []
                    
                    
                    if max(prcp_hist_list) > pmax:
                        pmax = max(prcp_hist_list)
                        tmax = t
                        
                    if p > max(prcp_hist_list) and prcp_hist_list[0] <= 0:
                        #storm started, reset counters and max prcp
                        t=0
                        tf = 0
                        pmax = 0
                    if sum(prcp_hist6_list)> prcp6_record:
                          prcp6_record = sum(prcp_hist6_list)
                    if sum(prcp_hist_list[0:4]) == 0 and sum(prcp_hist_list) != 0:
                        #storm over, change the length of searched array to change how long between stormsmeans its over
                        
                        try:
                            tf = t-4
                            ttp_dic[date['m']].append(float(tmax)/tf)
                            
                        except: 
                            #Storm event lasted a time step of 0; only one 15 min precip event recorded
                            pass
                        t=0
                        tf = 0
                        tmax = 0
                        pmax = 0
                        prcp_hist_list = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
                    
                    if prcp30_max > prcp30_record:
                        prcp30_record = prcp30_max
                    
                    #Increment time counter   
                    
                    t += 1    
                    
                    
                    #simple approx
                    try:
                        tmp = float(row['temp'])
                        h = float(row['humid'])
                        dew = 243.04*(np.log(h/100)+((17.625*tmp)/(243.04+tmp)))/(17.625-np.log(h/100)-((17.625*tmp)/(243.04+tmp)))
                        #print type(dew)
                        try:
                            float(dew)
                            dew_dic[date['m']].append(float(dew))
                        except:
                            pass
                        
                    except:
                        pass
                    
                    tup = ()
                    try:
                        dir = windDirection(float(row['wdir']))
                    except:
                        pass
                    try:
                        tup = (float(row['temp']),float(row['prcp']),float(row['humid']),float(row['srad']))
                        wind_tup = (float(row['ws']),dir)
                    except:
                        pass
                    months_dic[date['m']].append([tup,wind_tup])
                    
                    
            #finished reading file    
            
            
            #station info
            '''
             MOSCOW U OF I ID                        106152 0
             LATT=  46.73 LONG=-117.00 YEARS= 45. TYPE= 3
             ELEVATION = 2630. TP5 =  .85 TP6= 1.70
            
            '''
            station_name = fin.split('.')[0].upper()
            station_id = "000000 0"
            coords = (46.73,-117.00)
            itype = 3 # 1-4
            years = floor(daycount/360) #used 360 days to capture a small gaps in a year
            if years < 10:
                print "Number of years ({:.0f}) is less than 10.. Consider using a larger dataset.\nSmall datasets will not adequately capture long-term trends".format(years)
                
            elevation = "0000" #ft
            tp5 = round(prcp30_record,2)
            tp6 = round(prcp6_record,2)
            o.write('{0: <41}{1}\n'.format(station_name, station_id))
            o.write('LATT ={c[0]: >7} LONG={c[1]: >7} YEARS={y: >3}. TYPE= {t}\n'.format(c=coords,y=int(years),t=itype))
            o.write('ELEVATION = {e: >4} TP5 = {tp5: <5} TP6 = {tp6}\n'.format(e=elevation,tp5=tp5,tp6=tp6))
            
            
            
            
            
            month_p_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}  
            for m in ww.keys():
                try:
                    pday = []
                    for i in ww[m]:
                        pday.append(float(i))
                    for i in wd[m]:   
                        pday.append(float(i))
                    month_p_dic[m] = pday
                    
                    
                    
                    totaldays = len(ww[m])+len(wd[m])+len(dd[m])
                    ww[m] = float(len(ww[m]))/totaldays
                    wd[m] = float(len(wd[m]))/totaldays
                    
                    
                except:
                    pass
                
                
            #daily average prcp    
            
            for m in month_p_dic.keys():
                    try:
                        
                        mean =  np.mean(month_p_dic[m]) 
                        median =  np.median(month_p_dic[m]) 
                        std = np.std(month_p_dic[m]) 
                        count = len(month_p_dic[m])
                        skew = 3*(np.array(mean)-np.array(median))/np.array(std)
                        tup = ('%.2f'%(mean),'%.2f'%(std),'%.2f'%(skew))
                        month_p_dic[m] = tup
                    except:
                        pass
            
            
            ww_list = []
            wd_list = []
            p_list = [[],[],[]]
            for m in range(1,13):
                for t in range(0,3):
                    p_list[t].append(month_p_dic[str(m)][t])
                ww_list.append('%.2f'%(ww[str(m)]))
                wd_list.append('%.2f'%(wd[str(m)]))
            
            
            #here
            
            
            
            
            '''
            pct, mean, std, skew  = [],[],[],[]
            for i in dir_dic[dir]:
                pct.append(i[0])
                mean.append(i[1])
                std.append(i[2])
                skew.append(i[3])
            '''
            
            
            
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(p_list[0]),'MEAN P'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(p_list[1]),'S DEV P'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(p_list[2]),'SKEW P'))
            
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(ww_list),'P(W/W)'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(wd_list),'P(W/D)'))
            
            
            
            
            
            
            #monthly calculations for ttp, temp min, max, srad, dew
            
            
            for m in ttp_dic.keys():
                
                ttp_dic[m] = np.mean(ttp_dic[m])
                dew_dic[m] = np.mean(dew_dic[m])
                mean = np.mean(tempmax_dic[m])
                sd = np.std(tempmax_dic[m])
                tempmax_dic[m] = (mean,sd)
                mean = np.mean(tempmin_dic[m])
                sd = np.std(tempmin_dic[m])
                tempmin_dic[m] = (mean,sd)
                
                mean = np.mean(srad_dic[m])
                sd = np.std(srad_dic[m])
                srad_dic[m] = (mean,sd)
                prcp30_max_dic[m] = np.mean(prcp30_max_dic[m])
                
                   
                    
                    
                
            
            
            
            months_stat_dic = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[],'11':[],'12':[]}  
            ttp_list = []
            prcp30_max_list = []
            tmax_list = [[],[]]
            tmin_list = [[],[]]
            srad_list = [[],[]]
            dew_list = []
            for m in range(1,13):
                m = str(m) 
                wind_list = []
                
                
                wind_dic = {'N':[],'NNE':[],'NE':[],'ENE':[],'E':[],'ESE':[],'SE':[],'SSE':[],'S':[],'SSW':[],'SW':[],'WSW':[],'W':[],'WNW':[],'NW':[],'NNW':[]} 
                
            
                for i in months_dic[m]:
                    wind_list.append(i[1])
                for i in wind_list:               
                    wind_dic[i[1]].append(i[0])
                for key in wind_dic.keys():
                    try:
                        
                        mean =  np.mean(wind_dic[key]) 
                        median =  np.median(wind_dic[key]) 
                        std = np.std(wind_dic[key]) 
                        count = len(wind_dic[key])
                        skew = 3*(np.array(mean)-np.array(median))/np.array(std)
                        percent = float(count)/len(wind_list)*100
                        tup = ('%.2f'%(percent),'%.2f'%(mean),'%.2f'%(std),'%.2f'%(skew))
                        months_stat_dic[m].append([key,tup])
                    except:
                        pass
                 
                ttp_list.append('%.3f'%(ttp_dic[m]))
                dew_list.append('%.2f'%(dew_dic[m]))
                prcp30_max_list.append('%.2f'%(prcp30_max_dic[m]))
                for i in (0,1):
                    tmin_list[i].append('%.2f'%(tempmin_dic[m][i]))
                    tmax_list[i].append('%.2f'%(tempmax_dic[m][i]))
                    srad_list[i].append('%.0f'%(srad_dic[m][i]))   
            dir_dic = {'N':[],'NNE':[],'NE':[],'ENE':[],'E':[],'ESE':[],'SE':[],'SSE':[],'S':[],'SSW':[],'SW':[],'WSW':[],'W':[],'WNW':[],'NW':[],'NNW':[]}
            for m in range(1,13):
                #print "month: %s   calm pct: %s    not calm pct: %s"%(m,calm_dic[str(m)][0],calm_dic[str(m)][1])
                calmpct = round((float(calm_dic[str(m)][0])/(calm_dic[str(m)][0]+calm_dic[str(m)][1]))*100,2)
                
                calm_list.append(calmpct)
                for c in months_stat_dic[str(m)]:
                    
                    dir_dic[c[0]].append(c[1])
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(tmax_list[0]),'TMAX AV'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(tmin_list[0]),'TMIN AV'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(tmax_list[1]),'SD TMAX'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(tmin_list[1]),'SD TMIN'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(srad_list[0]),'SOL.RAD'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(srad_list[1]),'SD SOL'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(prcp30_max_list),'MX .5 P'))
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(dew_list),'DEW PT'))
            
            
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(ttp_list),'Time Pk'))
            
            
                
            
            for dir in ('N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'):
                
                pct, mean, std, skew  = [],[],[],[]
                
                for i in dir_dic[dir]:
                    pct.append(i[0])
                    mean.append(i[1])
                    std.append(i[2])
                    skew.append(i[3])
                o.write('% {1: <6}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(pct),dir))   
                o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(mean),'MEAN'))   
                o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(std),'STD DEV'))   
                o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(skew),'SKEW'))   
            o.write('{1: <8}{0[0]: >6}{0[1]: >6}{0[2]: >6}{0[3]: >6}{0[4]: >6}{0[5]: >6}{0[6]: >6}{0[7]: >6}{0[8]: >6}{0[9]: >6}{0[10]: >6}{0[11]: >6}\n'.format(tuple(calm_list),'CALM'))         
            
            o.write('\nINTERPOLATED DATA (station & weighting factor)\n\n')
            o.write('---Wind Stations---\n') 
            o.write('---Solar Radiation and Max .5 P Stations---\n') 
            o.write('---Dewpoint Stations---\n') 
            o.write('---Time Peak Stations---\n')         
            
        o.close()  
        
        
        
        
        