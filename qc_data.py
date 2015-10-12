import sqlite3
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import date, time, datetime
from qc import *


#############################
#############################
##
#     START QC!
##
#############################
#############################

#assert False

ship_random_uncertainty = 0.80
ship_micro_bias_uncertainty = 0.80
ship_uncertainty = np.sqrt(ship_random_uncertainty*ship_random_uncertainty + \
                           ship_micro_bias_uncertainty*ship_micro_bias_uncertainty )

connection = sqlite3.connect('Data\ICOADS.db')

#need two cursors, one for reading and one for making QC changes
cursor = connection.cursor()
cursor2 = connection.cursor()


for years in range(1850,1856):
    for months in range(1,13):

        print years,months

        for rows in cursor.execute('SELECT marinereports.uid, marinereports.year, marinereports.month, \
                                    marinereports.day, marinereports.hour, \
                                    marinereports.latitude, marinereports.longitude, marinereports.sst, \
                                    ob_extras.climatological_average FROM marinereports INNER JOIN ob_extras \
                                    ON marinereports.uid = ob_extras.uid \
                                    WHERE marinereports.year=? AND marinereports.month=?',[years,months]):

            uid = rows[0]
            year = rows[1]
            month = rows[2]
            day = rows[3]
            hour = rows[4]
            lat = rows[5]
            lon = rows[6]
            sst = rows[7]
            climav = rows[8]

            #first do positional checks
            if position_check(lat,lon) == 1:
                cursor2.execute('UPDATE qc SET bad_place=1 WHERE uid=:uid',{"uid": str(uid)} )
            else:
                cursor2.execute('UPDATE qc SET bad_place=0 WHERE uid=:uid',{"uid": str(uid)} )

            #do date checks
            if date_check(year,month,day,hour) == 1:
                cursor2.execute('UPDATE qc SET bad_time=1 WHERE uid=:uid',{"uid": str(uid)} )
            else:
                cursor2.execute('UPDATE qc SET bad_time=0 WHERE uid=:uid',{"uid": str(uid)} )
                

            #Do simple SST checks
            if sst_freeze_check(sst,0.0) == 1:
                cursor2.execute('UPDATE qc SET sst_freeze_check=1 WHERE uid=:uid', {"uid": str(uid) } )
            else:
                cursor2.execute('UPDATE qc SET sst_freeze_check=0 WHERE uid=:uid', {"uid": str(uid) } )

            #climatology check
            if sst != None and climav != None:
                if sst_climatology_check(sst,climav) == 1:
                    cursor2.execute('UPDATE qc SET sst_climatology_check=1 WHERE uid=:uid', {"uid": str(uid) } )
                else:
                    cursor2.execute('UPDATE qc SET sst_climatology_check=0 WHERE uid=:uid', {"uid": str(uid) } )
               
            if climav == None:
                cursor2.execute('UPDATE qc SET sst_no_normal=1 WHERE uid=:uid', {"uid": str(uid) } )
            else:
                cursor2.execute('UPDATE qc SET sst_no_normal=0 WHERE uid=:uid', {"uid": str(uid) } )


connection.commit()

#First run through by ID to split IDs that might have been used by more than one ship
#this is preparatory to running the track check because if two ships are making observations
#at the same time in two different oceans under the same ID it will look like a long
#string of track check failures.
#get all unique ids for this month
cursor.execute('SELECT DISTINCT id FROM marinereports')
allids = cursor.fetchall()

for rows in allids:

   if (rows[0] != None):

        thisid = rows[0]
        print "ID,",thisid

        cursor.execute("SELECT COUNT(*) FROM marinereports \
                        INNER JOIN qc ON marinereports.uid = qc.uid \
                        WHERE marinereports.id=:id \
                        AND qc.bad_time = 0 \
                        AND qc.sst_no_normal = 0 \
                        AND qc.sst_climatology_check = 0 \
                        AND qc.sst_freeze_check = 0",{"id": thisid})
        n_elements = cursor.fetchone()[0]

        times        = np.zeros(n_elements)
        longitudes   = np.zeros(n_elements)
        latitudes    = np.zeros(n_elements)
        ssts         = np.zeros(n_elements)
        ship_courses = np.zeros(n_elements)
        ship_speeds  = np.zeros(n_elements)
        uids = []

        cursor.execute('SELECT marinereports.year, marinereports.month, \
                        marinereports.day, marinereports.hour, \
                        marinereports.latitude, marinereports.longitude, \
                        marinereports.sst, marinereports.ship_course, \
                        marinereports.ship_speed, marinereports.uid \
                        FROM marinereports \
                        INNER JOIN qc ON marinereports.uid = qc.uid \
                        WHERE marinereports.id=:id \
                        AND qc.bad_time = 0 \
                        AND qc.sst_no_normal = 0 \
                        AND qc.sst_climatology_check = 0 \
                        AND qc.sst_freeze_check = 0',{"id": thisid})

        for i in range(n_elements):
            row = cursor.fetchone()
            hour = row[3]
            if hour == None:
                hour = 0.0
            times[i] = 24.0*60.*60.*(datetime(row[0],row[1],row[2]).toordinal() + hour/24.)
            latitudes[i] = row[4]
            longitudes[i] = row[5]
            ssts[i] = row[6]
            ship_courses[i] = row[7]
            ship_speeds[i] = row[8]
            uids.append(str(row[9]))

        if n_elements > 5:
            ship_assignments = split_generic_callsign(times,latitudes,longitudes)
            
            if max(ship_assignments) > 500:
                m = Basemap(projection='hammer',lon_0=-160)
                m.fillcontinents(color='#cc9966',lake_color='#99ffff')
                x, y = m(longitudes, latitudes)
                m.drawcoastlines()
                im1 = m.scatter(x,y, s=100, c=ship_assignments)
                cb = m.colorbar(im1,"bottom", size="5%", pad="0%")
                plt.title(thisid, fontsize=14, fontweight='bold')
                plt.show()

#if we found multiple ships then update the newid field in obextras
            print max(ship_assignments)
            if max(ship_assignments) > 1:
                for i in range(n_elements):
                    newid = thisid
                    newid = newid + "_SPLIT_" + str(ship_assignments[i])
                    cursor2.execute('UPDATE ob_extras SET newid=:newid WHERE uid=:uid', {"uid": uids[i], "newid": newid } )
                    print newid, thisid

connection.commit()

#Next stage is to do track check QC using the new ship IDs
#get all unique "new" ids for this month
cursor.execute('SELECT DISTINCT newid FROM ob_extras')
allids = cursor.fetchall()

for rows in allids:

   if (rows[0] != None):

        thisid = rows[0]
        print "ID,",thisid

        cursor.execute("SELECT COUNT(*) FROM marinereports \
                        INNER JOIN qc ON marinereports.uid = qc.uid \
                        INNER JOIN ob_extras ON marinereports.uid = ob_extras.uid \
                        WHERE ob_extras.newid=:id \
                        AND qc.bad_time = 0 \
                        AND qc.sst_no_normal = 0 \
                        AND qc.sst_climatology_check = 0 \
                        AND qc.sst_freeze_check = 0",{"id": thisid})

        n_elements = cursor.fetchone()[0]

        times        = np.zeros(n_elements)
        longitudes   = np.zeros(n_elements)
        latitudes    = np.zeros(n_elements)
        ssts         = np.zeros(n_elements)
        ship_courses = np.zeros(n_elements)
        ship_speeds  = np.zeros(n_elements)
        uids = []

        cursor.execute('SELECT marinereports.year, marinereports.month, \
                        marinereports.day, marinereports.hour, \
                        marinereports.latitude, marinereports.longitude, \
                        marinereports.sst, marinereports.ship_course, \
                        marinereports.ship_speed, marinereports.uid \
                        FROM marinereports \
                        INNER JOIN qc ON marinereports.uid = qc.uid \
                        INNER JOIN ob_extras ON marinereports.uid = ob_extras.uid \
                        WHERE ob_extras.newid=:id \
                        AND qc.bad_time = 0 \
                        AND qc.sst_no_normal = 0 \
                        AND qc.sst_climatology_check = 0 \
                        AND qc.sst_freeze_check = 0',{"id": thisid})

        for i in range(n_elements):
            row = cursor.fetchone()
            hour = row[3]
            if hour == None:
                hour = 0.0
            times[i] = 24.0*60.*60.*(datetime(row[0],row[1],row[2]).toordinal() + hour/24.)
            latitudes[i] = row[4]
            longitudes[i] = row[5]
            ssts[i] = row[6]
            ship_courses[i] = row[7]
            ship_speeds[i] = row[8]
            uids.append(str(row[9]))

#track check if there are more than 5 observations
        if n_elements > 5:
            result = track_check(times,latitudes,longitudes,ship_courses,ship_speeds)

            if sum(result) > 0:
                m = Basemap(projection='hammer',lon_0=-160)
                m.fillcontinents(color='#cc9966',lake_color='#99ffff')
                x, y = m(longitudes, latitudes)
                m.drawcoastlines()
                im1 = m.scatter(x,y, s=100, c=result)
                cb = m.colorbar(im1,"bottom", size="5%", pad="0%")
                im2 = m.plot(x,y)
                plt.title(thisid, fontsize=14, fontweight='bold')
                plt.show()


            for i in range(n_elements):
                cursor2.execute('UPDATE qc SET fewsome_check=0, track_check=:tchk WHERE uid=:uid', {"uid": uids[i], "tchk": result[i] } )
#with 5 observations or fewer, flag all as singletons or fewsomes
        else:
            for i in range(n_elements):
                cursor2.execute('UPDATE qc SET fewsome_check=1 WHERE uid=:uid', {"uid": uids[i]} )
 

connection.commit()
connection.close()

connection = sqlite3.connect('Data\ICOADS.db')
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM qc WHERE track_check = 1")
print "Failed track check ",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE sst_freeze_check = 1")
print "Failed SST freeze check",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE sst_climatology_check = 1")
print "Failed SST climatology check",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE sst_no_normal = 1")
print "Failed No Normal",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE fewsome_check = 1")
print "Failed Fewsome check",cursor.fetchone()[0]

connection.close()

