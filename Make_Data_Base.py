import sqlite3
import imp
import numpy as np
import math
from datetime import date, time, datetime
import calendar
from netCDF4 import Dataset

foo = imp.load_source('IMMA.py', '..\IMMA\Python\IMMA.py')

def which_pentad(inmonth,inday):
    #take month and day as inputs and return pentad in range 1-73
    month_lengths = [31,28,31,30,31,30,31,31,30,31,30,31]
    count=0
    
    #leap years.
    if inmonth == 2 and inday == 29:
        inmonth = 3
        inday = 1
    for month in range(1,13):
        for day in range(1,month_lengths[month-1]+1):
            if month == inmonth and day == inday:
                pentad = count/5
            count += 1

    return pentad + 1

def get_sst(lat,lon,month,day,sst):

    month_lengths = [31,29,31,30,31,30,31,31,30,31,30,31]

    if  lat >= -90.0 and lat <=90.0 and \
       lon >= -180.0 and lon <= 360.0 and \
       month >= 1 and month <=12 and \
       day >=1 and day <= month_lengths[month-1]:
        
        if lon >= 180.0:
            lon = -180.0 + (lon - 180.0)

    #read sst from grid
        pentad = which_pentad(month,day)
        xindex = int(lon + 180.0)
        if xindex >= 360:
            xindex = 0
        yindex = int(90 - lat)
        if yindex >= 180:
            yindex = 179
        if yindex < 0:
            yindex = 0

        result = sst[pentad-1,yindex,xindex]

    else:

        result = -99


    return result

climatology = Dataset('Data/HadSST2_pentad_climatology.nc')
sst = climatology.variables['sst'][:]
lats = climatology.variables['latitude'][:]
lons = climatology.variables['longitude'][:]
lons, lats = np.meshgrid(lons,lats)


connection = sqlite3.connect('Data\ICOADS.db')
cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS marinereports')
cursor.execute('DROP TABLE IF EXISTS qc')
cursor.execute('DROP TABLE IF EXISTS ob_extras')

cursor.execute('CREATE TABLE marinereports (uid text PRIMARY KEY, id text, year int, \
    month int, day int, hour real, latitude real, longitude real, \
    sst real, at real, country text, sst_method int, deck int, \
    source_id int, platform_type int, ship_course int, ship_speed int)')

cursor.execute('CREATE TABLE qc (uid text PRIMARY KEY, bad_time int, bad_place int, over_land int, \
    track_check int, sst_buddy_check int, bad_sst int, sst_freeze_check int, \
    sst_no_normal int, sst_climatology_check int, fewsome_check int)')

cursor.execute('CREATE TABLE ob_extras (uid text PRIMARY KEY, random_unc real, \
    micro_bias real, bias real, bias_unc real, climatological_average real)')


for year in range(1850,1855):
    for month in range(1,13):

        print year,month
        smn = str(month)
        syr = str(year)
        if month < 10:
            smn = '0'+smn
        yrmn = syr + smn

        print yrmn

        file = open('Data\IMMA_R2.5.'+syr+'.'+smn+'.man',"r")

        x=foo.IMMA()

        test = 0

        while x.read(file):
            
            uid = yrmn + str(test)

            cursor.execute('INSERT INTO marinereports VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
                   ,[uid, x.data['ID'],x.data['YR'],x.data['MO'],x.data['DY'],x.data['HR'], \
                     x.data['LAT'],x.data['LON'],x.data['SST'],x.data['AT'],x.data['C1'], \
                     x.data['SI'],x.data['DCK'],x.data['SID'],x.data['PT'],x.data['DS'], \
                     x.data['VS']])

#initialise QC to be null - neither pass nor fail
            cursor.execute('INSERT INTO qc VALUES (?,?,?,?,?,?,?,?,?,?,?)'
                           ,[uid, None, None, None, None, None, None, None, None, None, None])

            
            clim = float(get_sst(x.data['LAT'],x.data['LON'],x.data['MO'],x.data['DY'],sst))

#set some default values for the ob extra table.
            if x.data['PT'] <= 5:
                cursor.execute('INSERT INTO ob_extras VALUES (?,?,?,?,?,?)'
                               ,[uid, 0.8, 0.8, None, None, clim])
            if x.data['PT'] == 7:
                cursor.execute('INSERT INTO ob_extras VALUES (?,?,?,?,?,?)'
                               ,[uid, 0.5, 0.5,  0.0,  0.0, clim])
            if x.data['PT'] == 6:
                cursor.execute('INSERT INTO ob_extras VALUES (?,?,?,?,?,?)'
                               ,[uid, 0.5, 0.5,  0.0,  0.0, clim])
                
            test=test+1
           
        file.close()

connection.commit()
connection.close()
