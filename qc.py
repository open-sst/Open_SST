import numpy as np
import math
from datetime import date, time, datetime
import calendar

def sst_climatology_check(insst,inclimav, tolerance = 8.0):

    result = 0

    if insst == None or inclimav == None:
        result = 1
    else:
        if abs(insst-inclimav) > tolerance:
            result = 1

    return result

def sst_freeze_check(insst, sst_unc):
#fail if SST below the freezing point by more than twice the uncertainty
    result = 0
    if (insst != None):
        if (insst < (-1.93-2*sst_unc)):
            result = 1
    return result


def position_check(inlat, inlon):
#return 1 if lat or lon is invalid, 0 otherwise
    assert inlat != None and not(math.isnan(inlat))
    assert inlon != None and not(math.isnan(inlon))
    result = 0
    if (inlat < -90 or inlat > 90):
        result = 1
    if (inlon <-180 or inlon > 360):
        result = 1
    if (inlat == 0 and inlon ==0):
        result = 1

    return result


def date_check(inyear, inmonth, inday, inhour):
#return 1 if date is valid. 0 otherwise
    assert inyear != None
    assert inmonth != None
#    assert inday != None

    result = 0

    if (inyear > 2024 or inyear < 1850):
        result = 1

    if (inmonth < 1 or inmonth > 12):
        result = 1

    if calendar.isleap(inyear):
        month_lengths = [31,29,31,30,31,30,31,31,30,31,30,31]
    else:
        month_lengths = [31,28,31,30,31,30,31,31,30,31,30,31]
        
    if inday == None:
        result = 1
    else:
        if (inday < 1 or inday > month_lengths[inmonth-1]):
            result = 1

    if (inhour != None and (inhour >= 24 or inhour < 0)):
        result = 1

    return result

def sphere_distance(lat1,lon1,lat2,lon2):
    earths_radius = 6400.0
    delta = angular_distance(lat1,lon1,lat2,lon2)*earths_radius
    return delta

def angular_distance(lat1,lon1,lat2,lon2):
#calculate distance between two points on a sphere
#input latitudes and longitudes should be in degrees
    assert lat1 != None and not(math.isnan(lat1))
    assert lon1 != None and not(math.isnan(lon1))
    assert lat2 != None and not(math.isnan(lat2))
    assert lon2 != None and not(math.isnan(lon2))

    radians_per_degree = np.pi / 180.

#convert degrees to radians
    lat1 = lat1 * radians_per_degree
    lon1 = lon1 * radians_per_degree
    lat2 = lat2 * radians_per_degree
    lon2 = lon2 * radians_per_degree
    
    delta_lambda = abs(lon1-lon2)
    bit1 = (np.cos(lat2)*np.sin(delta_lambda))
    bit1 = bit1*bit1
    bit2 = ( np.cos(lat1)*np.sin(lat2) - np.sin(lat1)*np.cos(lat2)*np.cos(delta_lambda) )
    bit2 = bit2 * bit2
    topbit = bit1 + bit2
    topbit = np.sqrt(topbit)
    bottombit = np.sin(lat1)*np.sin(lat2) + np.cos(lat1)*np.cos(lat2)*np.cos(delta_lambda)
    delta = np.arctan2(topbit, bottombit)
    
    return delta

def lat_lon_from_course_and_distance(lat1, lon1, tc, d):
#calculate a latitude and longitude given a starting point, course and angular distance
#http://williams.best.vwh.net/avform.htm#LL
    radians_per_degree = np.pi / 180.
    lat1 = lat1 * radians_per_degree
    lon1 = lon1 * radians_per_degree

    lat =np.arcsin(np.sin(lat1)*np.cos(d)+np.cos(lat1)*np.sin(d)*np.cos(tc))
    dlon=np.arctan2(np.sin(tc)*np.sin(d)*np.cos(lat1),np.cos(d)-np.sin(lat1)*np.sin(lat))
    lon= math.fmod( lon1-dlon+np.pi, 2.*np.pi ) - np.pi

    lat = lat / radians_per_degree
    lon = -1 * lon / radians_per_degree

    return (lat,lon)

def course_between_points(lat1,lon1,lat2,lon2):
#given two points find the initial true course at point1
    d = angular_distance(lat1,lon1,lat2,lon2)
    radians_per_degree = np.pi / 180.

    if d != 0:
    
        lat1 = lat1 * radians_per_degree
        lon1 = lon1 * radians_per_degree
        lat2 = lat2 * radians_per_degree
        lon2 = lon2 * radians_per_degree
    
        if np.cos(lat1) < 0.0000001:
            if lat1 > 0:
                tc1 = np.pi
            else:
                tc1 = 2.*np.pi
        else:
            if np.sin(lon2-lon1) > 0:
                tc1 = np.arccos((np.sin(lat2)-np.sin(lat1)*np.cos(d))/(np.sin(d)*np.cos(lat1)))
            else:
                tc1 = 2.*np.pi-np.arccos((np.sin(lat2)-np.sin(lat1)*np.cos(d))/(np.sin(d)*np.cos(lat1)))

    else:
        
        tc1 = 0.0
        
    return tc1/radians_per_degree

def intermediate_point(lat1,lon1,lat2,lon2,f):
#given two lat,lon point find the latitude and longitude that are a fraction f
#of the great circle distance between them
#http://williams.best.vwh.net/avform.htm#Intermediate

    assert f <= 1.0
    
    d = angular_distance(lat1,lon1,lat2,lon2)

    if d != 0.0:
#convert degrees to radians
        radians_per_degree = np.pi / 180.
        lat1 = lat1 * radians_per_degree
        lon1 = lon1 * radians_per_degree
        lat2 = lat2 * radians_per_degree
        lon2 = lon2 * radians_per_degree

        A = np.sin((1-f)*d)/np.sin(d)
        B = np.sin(f*d)/np.sin(d)
        x = A*np.cos(lat1)*np.cos(lon1) +  B*np.cos(lat2)*np.cos(lon2)
        y = A*np.cos(lat1)*np.sin(lon1) +  B*np.cos(lat2)*np.sin(lon2)
        z = A*np.sin(lat1)              +  B*np.sin(lat2)
        lat=np.arctan2(z,np.sqrt(x*x+y*y)) / radians_per_degree
        lon=np.arctan2(y,x) / radians_per_degree
    else:
        lat = lat1
        lon = lon1

    return (lat,lon)

def split_generic_callsign(times,latitudes,longitudes):

    #knots to metres per second
    knots_conversion     = 0.51444444

    #at least one ship
    result = [1]
    n_ships = 1

    last_time = [times[0]]
    last_lat = [latitudes[0]]
    last_lon = [longitudes[0]]

    n = len(times)

    if n > 1:
        for i in range(1,n):
            #calculate speeds from last position for each ship
            speeds =[]
            distances = []
            for j in range(0,n_ships):
                d = 1000.*sphere_distance(latitudes[i],longitudes[i],last_lat[j],last_lon[j])
                distances.append(d)
                if times[i]-last_time[j] == 0 and d == 0:
                    speeds.append(0.0)
                elif times[i]-last_time[j] == 0 and d != 0:
                    speeds.append(99.99)
                else:
                    speeds.append(d / (times[i]-last_time[j]))

            #if all speeds exceed 40 knots then create new ship
            if min(speeds) > 40.0 * knots_conversion:
                n_ships = n_ships + 1
                last_time.append(times[i])
                last_lat.append(latitudes[i])
                last_lon.append(longitudes[i])
                result.append(n_ships)

            #else check distances from all ships to ob
            else:
                if min(distances) < 1000.*5000.:
                    #if there's a small gap (<5000 km) then append to existing ship
                    winner = distances.index(min(distances))
                    last_time[winner] = times[i]
                    last_lat[winner] = latitudes[i]
                    last_lon[winner] = longitudes[i]
                    result.append(winner+1)
                else:
                    #for big gaps add a new ship
                    n_ships = n_ships + 1
                    last_time.append(times[i])
                    last_lat.append(latitudes[i])
                    last_lon.append(longitudes[i])
                    result.append(n_ships)
                
    return result


def track_check(times,latitudes,longitudes,reported_course,reported_speed):

#this is a set of checks to make sure the tracks look sensiblish

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
        if times[i]-times[i-1] == 0:
            speeds[i,1] = 999999999.0
        else:
            speeds[i,1] = distances/(times[i]-times[i-1])
    for i in range(2, n):
        distances = 1000.*sphere_distance(latitudes[i],longitudes[i],latitudes[i-2],longitudes[i-2])
        if times[i]-times[i-2] == 0:
            speeds[i,0] = 999999999.0
        else:
            speeds[i,0] = distances/(times[i]-times[i-2])
    for i in range(0, n-1):
        distances = 1000.*sphere_distance(latitudes[i+1],longitudes[i+1],latitudes[i],longitudes[i])
        if times[i+1]-times[i] == 0:
            speeds[i,2] = 999999999.0
        else:
            speeds[i,2] = distances/(times[i+1]-times[i])
    for i in range(0, n-2):
        distances = 1000.*sphere_distance(latitudes[i+2],longitudes[i+2],latitudes[i],longitudes[i])
        if times[i+2]-times[i] == 0:
            speeds[i,3] = 999999999.0
        else:
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
        if (times[i+1]-times[i-1]) == 0.0:
            fraction = 1.0
        else:   
            fraction = (times[i]-times[i-1])/(times[i+1]-times[i-1])

        interpolated_latitude, interpolated_longitude = \
                               intermediate_point(latitudes[i-1],longitudes[i-1],latitudes[i+1],longitudes[i+1],fraction)

        distance_from_interpolated_position = \
                                sphere_distance(latitudes[i],longitudes[i],\
                                                interpolated_latitude,interpolated_longitude)
        if (distance_from_interpolated_position > max_dist_from_interp_pos):
            flags[i,3] = 1
            failure = 1

#flag if distance between reported and predicted position
#start loop at two because we need a calculated speed for the previous ob
    for i in range(2,n):
        if reported_course[i-1] != None and not(math.isnan(reported_course[i-1])) and \
           reported_speed[i-1] != None and not(math.isnan(reported_speed[i-1])):
            if ship_course_lookup[int(reported_course[i-1])] != None:

                #this is the reported speed at the previous ob
                low  =  reported_speed_low_bounds[int(reported_speed[i-1])]*knots_conversion
                high =  reported_speed_high_bounds[int(reported_speed[i-1])]*knots_conversion
                avspeed = (high+low)/2.
                #the time between observations is
                timchange = times[i]-times[i-1]

                #distance is speed times time
                distance = avspeed * timchange
                #angular distance is actual distance divided by earth's radius
                distance = distance / 6400.

                #this is the reported course at the previous ob
                course = ship_course_lookup[int(reported_course[i-1])]

                predictedlat, predictedlon = lat_lon_from_course_and_distance(latitudes[i],longitudes[i],course,distance)

                #calculate difference between predicted and reported position
                dist = sphere_distance(latitudes[i],longitudes[i],predictedlat, predictedlon)
                #if this distance is greater than the time between obs multiplied by the calculated speed at the last ob then fail
                if dist > timchange*speeds[i-1,1]:
                    flags[i,5] = 1

#flag if direction of travel differs by more than 60 degrees from the direction reported at previous ob
    for i in range(1,n):
        #calculate direction
        lat_change = latitudes[i]-latitudes[i-1]
        lon_change = longitudes[i]-longitudes[i-1]

        course = course_between_points(latitudes[i-1],longitudes[i-1] \
                                       ,latitudes[i],longitudes[i])
        course = course * np.pi/180.

        if course != None and reported_course[i-1] != None and not(math.isnan(reported_course[i-1])):
            if ship_course_lookup[int(reported_course[i-1])] != None:

                diff = angle_diff(course,ship_course_lookup[int(reported_course[i-1])])

                if diff > 60.0 * np.pi/180.:
                    flags[i,4] = 1
                    failure = 1

    failure = np.zeros(n)
    for i in range(1,n-1):
#failure is exceed soft speed limit AND too far from interpolated position AND two or more others
        if flags[i,0] == 1 and flags[i,3] == 1 and flags[i,1]+flags[i,2]+flags[i,4]+flags[i,5] >=2 :
            failure[i] = 1
            
    return failure

def angle_diff(angle1,angle2):
#calculate angle between two angles
    diff = abs(angle1 - angle2)
    if diff > np.pi:
        diff = 2.0 * np.pi - diff
    return diff

