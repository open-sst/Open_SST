import sqlite3
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import date, time, datetime

def sst_freeze_check(insst, sst_unc):
#fail if SST below the freezing point by more than twice the uncertainty
    result = 0
    if (insst != None):
        if (insst < -1.93-2*sst_unc):
            result = 1
    return result

def position_check(inlat, inlon):
    result = 0
    if (inlat < -90 or inlat > 90):
        result = 1
    if (inlon <-180 or inlon > 360):
        result = 1
    return result

def date_check(inyear, inmonth, inday, inhour):
    result = 0

    if (inyear > 2024 or inyear < 1850):
        result = 1

    if (inmonth < 1 or inmonth > 12):
        result = 1
        
    month_lengths = [31,29,31,30,31,30,31,31,30,31,30,31]
    if (inday < 1 or inday > month_lengths[inmonth-1]):
        result = 1

    if (inhour != None and (inhour >= 24 or inhour < 0)):
        result = 1

    return result

def sphere_distance(lat1,lon1,lat2,lon2):
    lat1 = lat1 * np.pi / 180.
    lon1 = lon1 * np.pi / 180.
    lat2 = lat2 * np.pi / 180.
    lon2 = lon2 * np.pi / 180.
    delta_lambda = abs(lon1-lon2)
    bit1 = (np.cos(lat2)*np.sin(delta_lambda))
    bit1 = bit1*bit1
    bit2 = ( np.cos(lat1)*np.sin(lat2) - np.sin(lat1)*np.cos(lat2)*np.cos(delta_lambda) )
    bit2 = bit2 * bit2
    topbit = bit1 + bit2
    topbit = np.sqrt(topbit)
    bottombit = np.sin(lat1)*np.sin(lat2) + np.cos(lat1)*np.cos(lat2)*np.cos(delta_lambda)
    delta = 6400. * np.arctan2(topbit, bottombit)
    return delta

def track_check(times,latitudes,longitudes,reported_course,reported_speed):

    knots_conversion     = 0.51444444
    miles_to_km         = 1.609344 
    median_to_max_speed = 1.25
    lowest_max_speed    = 8.51
    default_max_speed   = 15.0

    max_dist_from_interp_pos = 150 * miles_to_km

    absolute_max_speed = 40.0 * knots_conversion
    max_speed_change   = 10.0 * knots_conversion

#use from 1 January 1968
    reported_speed_low_bounds  = [0.0, 1.0, 6.0, 11.0, 16.0, 21.0, 26.0, 31.0, 36.0, 40.1,   0.0]
    reported_speed_high_bounds = [0.0, 5.0, 10., 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 100., 100.0]

#use before 1 January 1968
    early_reported_speed_low_bounds  = [0.0, 1.0, 4.0, 7.0, 10.0, 13.0, 16.0, 19.0, 22.0, 24.1,   0.0]
    early_reported_speed_high_bounds = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 100., 100.0]

#angle clockwise from north
    ship_course_lookup = [None, np.pi/4., 2.*np.pi/4., 3.*np.pi/4., 4.*np.pi/4.,
                             5.*np.pi/4., 6.*np.pi/4., 7.*np.pi/4., 0.0*np.pi/4., None] 


    assert len(times) == len(reported_course)
    assert len(times) == len(reported_speed)
    assert len(times) == len(latitudes)
    assert len(times) == len(longitudes)

    n = len(times)

    speeds = np.zeros((n,4))
    flags = np.zeros((n,10))

#calculate speeds relative to points within +- 2 obs
    for i in range(1, n):
        distances = 1000.*sphere_distance(latitudes[i],longitudes[i],latitudes[i-1],longitudes[i-1])
        speeds[i,1] = distances/(times[i]-times[i-1])
    for i in range(2, n):
        distances = 1000.*sphere_distance(latitudes[i],longitudes[i],latitudes[i-2],longitudes[i-2])
        speeds[i,0] = distances/(times[i]-times[i-2])

    for i in range(0, n-1):
        distances = 1000.*sphere_distance(latitudes[i+1],longitudes[i+1],latitudes[i],longitudes[i])
        speeds[i,2] = distances/(times[i+1]-times[i])
    for i in range(0, n-2):
        distances = 1000.*sphere_distance(latitudes[i+2],longitudes[i+2],latitudes[i],longitudes[i])
        speeds[i,3] = distances/(times[i+2]-times[i])

    speed_limit = np.median(speeds[:,1]) * median_to_max_speed
    if speed_limit < lowest_max_speed:
        speed_limit = default_max_speed

    failure = 0

#flag if speed calculated from preceding two obs, two neighbouring obs, or next two obs exceeds the limit
    for i in range(0,n):
        if speeds[i,0] > speed_limit and speeds[i,1] > speed_limit:
            flags[i,0] = 1
            failure = 1
        if speeds[i,1] > speed_limit and speeds[i,2] > speed_limit:
            flags[i,0] = 1
            failure = 1
        if speeds[i,2] > speed_limit and speeds[i,3] > speed_limit:
            flags[i,0] = 1
            failure = 1

#flag if speed exceeds absolute max speed            
        if speeds[i,1] > absolute_max_speed:
            flags[i,1] = 1
            failure = 1

#flag if speed difference between calculated speed from previous ob to this one
#and reported speed at previous ob is too large
    for i in range(1,n):

        if reported_speed[i-1] != None and not(math.isnan(reported_speed[i-1])):
            low  =  reported_speed_low_bounds[int(reported_speed[i-1])]*knots_conversion
            high = reported_speed_high_bounds[int(reported_speed[i-1])]*knots_conversion
        else:
            low = 0.0*knots_conversion
            high = 100.0*knots_conversion
        
        if (speeds[i,1] < low and abs(speeds[i,1]-low) > max_speed_change) :
            flags[i,2] = 1
            failure = 1
        if (speeds[i,1] > high and abs(speeds[i,1]-high) > max_speed_change) :
            flags[i,2] = 1
            failure = 1

#flag if distance from interpolated position is > 150 miles
    interpolated_positions = np.zeros(n)
    for i in range(1,n-1):
        fraction = (times[i]-times[i-1])/(times[i+1]-times[i-1])
        interpolated_latitude = fraction*(latitudes[i+1]-latitudes[i-1]) + latitudes[i-1]
        interpolated_longitude = fraction*(longitudes[i+1]-longitudes[i-1]) + longitudes[i-1]
        distance_from_interpolated_position = \
                                sphere_distance(latitudes[i],longitudes[i],\
                                                interpolated_latitude,interpolated_longitude)
        if (distance_from_interpolated_position > max_dist_from_interp_pos):
            flags[i,3] = 1
            failure = 1

#flag if distance between reported and predicted position
            
#flag if direction of travel differs by more than 60 degrees from the direction reported at previous ob
    for i in range(1,n):
        #calculate direction
        lat_change = latitudes[i]-latitudes[i-1]
        lon_change = longitudes[i]-longitudes[i-1]

        angle = angle_from_latlon(lat_change,lon_change)

        if angle != None and reported_course[i-1] != None and not(math.isnan(reported_course[i-1])):

            if ship_course_lookup[int(reported_course[i-1])] != None:

                diff = angle_diff(angle,ship_course_lookup[int(reported_course[i-1])])

                if diff > 60.0 * np.pi / 180.:
                    flags[i,4] = 1
                    failure = 1

    failure = np.zeros(n)
    for i in range(1,n-1):
#failure is exceed soft speed limit AND too far from interpolated position AND two or more others
        if flags[i,0] == 1 and flags[i,3] == 1 and flags[i,1]+flags[i,2]+flags[i,4] >=2 :
            failure[i] = 1
            
    return failure

def angle_diff(angle1,angle2):
#calculate angle between two angles
    diff = abs(angle1 - angle2)
    if diff > np.pi:
        diff = 2.0 * np.pi - diff
    return diff

def angle_from_latlon(lat_change,lon_change):
#work out the bearing from north given a particular latitude and longitude change
#return None if there's no movement
    if lat_change > 0 and lon_change >= 0:
        angle = np.arctan(abs(lon_change)/abs(lat_change))
    elif lat_change <= 0 and lon_change > 0:
        angle = np.arctan(abs(lat_change)/abs(lon_change)) + np.pi/2.
    elif lat_change < 0 and lon_change <= 0:
        angle = np.arctan(abs(lon_change)/abs(lat_change)) + np.pi
    elif lat_change >= 0 and lon_change < 0:
        angle = np.arctan(abs(lat_change)/abs(lon_change)) + 3*np.pi/2.
    else:
        angle = None

    return angle

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

for years in range(1976,1977):
    for months in range(1,3):
        for rows in cursor.execute('SELECT * FROM marinereports WHERE year=? AND month=?',[years,months]):

            #first do positional checks
            if position_check(rows[6],rows[7]) == 1:
#                print "place failure",rows[6],rows[7]
                cursor2.execute('UPDATE qc SET bad_place=1 WHERE uid=?',str(rows[0]))

            #do date checks
            if date_check(rows[2],rows[3],rows[4],rows[5]) == 1:
#                print "date failure",rows[2],rows[3],rows[4],rows[5]
                cursor2.execute('UPDATE qc SET bad_date=1 WHERE uid=?',str(rows[0]))

            #Do simple SST checks
            if sst_freeze_check(rows[8],0.0) == 1:
#                print "freeze!",rows[8]
                cursor2.execute('UPDATE qc SET sst_freeze_check=1 WHERE uid=:uid', {"uid": str(rows[0]) } )
                

connection.commit()

#get all unique ids for this month
cursor.execute('SELECT DISTINCT id FROM marinereports')
allids = cursor.fetchall()

for rows in allids:

   if (rows[0] != None):

        thisid = rows[0]
        print "ID,",thisid

        cursor.execute("SELECT COUNT(*) FROM marinereports WHERE id=:id",{"id": thisid})
        n_elements = cursor.fetchone()[0]

        if (n_elements > 5):

            times        = np.zeros(n_elements)
            longitudes   = np.zeros(n_elements)
            latitudes    = np.zeros(n_elements)
            ssts         = np.zeros(n_elements)
            ship_courses = np.zeros(n_elements)
            ship_speeds  = np.zeros(n_elements)
            uids = []

            cursor.execute('SELECT year, month, day, hour, latitude, longitude, sst, ship_course, ship_speed, uid FROM marinereports WHERE id=:id',{"id": thisid})

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

            result = track_check(times,latitudes,longitudes,ship_courses,ship_speeds)

            for i in range(n_elements):
                cursor2.execute('UPDATE qc SET track_check=:tchk WHERE uid=:uid', {"uid": uids[i], "tchk": result[i] } )
 
#            assert False
#            if sum(result) > 0:
 #               m = Basemap(projection='hammer',lon_0=-160)
  #              m.fillcontinents(color='#cc9966',lake_color='#99ffff')
   #             x, y = m(longitudes, latitudes)
    #            m.drawcoastlines()
     #           im1 = m.scatter(x,y, s=100, c=result)
      #          cb = m.colorbar(im1,"bottom", size="5%", pad="0%")
       #         im2 = m.plot(x,y)
        #        plt.title(thisid, fontsize=14, fontweight='bold')
         #       plt.show()
#

            #assert False

cursor.execute("SELECT COUNT(*) FROM qc WHERE track_check = 1")
print cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE sst_freeze_check = 1")
print cursor.fetchone()[0]

connection.commit()
connection.close()
