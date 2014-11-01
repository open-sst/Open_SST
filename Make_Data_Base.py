import sqlite3
import imp

foo = imp.load_source('IMMA.py', '..\IMMA\Python\IMMA.py')

connection = sqlite3.connect('Data\ICOADS.db')
cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS marinereports')
cursor.execute('DROP TABLE IF EXISTS qc')
cursor.execute('DROP TABLE IF EXISTS ob_extras')

cursor.execute('CREATE TABLE marinereports (uid text, id text, year int, \
    month int, day int, hour real, latitude real, longitude real, \
    sst real, at real, country text, sst_method int, deck int, \
    source_id int, platform_type int, ship_course int, ship_speed int)')

cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS uid ON marinereports (uid)')

cursor.execute('CREATE TABLE qc (uid text, bad_time int, bad_place int, over_land int, \
    track_check int, sst_buddy_check int, bad_sst int, sst_freeze_check int, \
    sst_no_normal int, sst_climatology_check int)')

cursor.execute('CREATE TABLE ob_extras (uid text, random_unc real, \
    micro_bias real, bias real, bias_unc real, icoads_measurement_method int, \
    wmo47_measurement_method int, )')


for year in range(1976,1977):
    for month in range(1,3):

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
            cursor.execute('INSERT INTO qc VALUES (?,?,?,?,?,?,?,?,?,?)'
                           ,[uid, None, None, None, None, None, None, None, None, None])

#set some default values for the ob extra table.
            if x.data['PT'] <= 5:
                cursor.execute('INSERT INTO ob_extras VALUES (?,?,?,?,?)'
                               ,[uid, 0.8, 0.8, None, None])
            if x.data['PT'] == 7:
                cursor.execute('INSERT INTO ob_extras VALUES (?,?,?,?,?)'
                               ,[uid, 0.5, 0.5, 0.0, 0.0])
            if x.data['PT'] == 6:
                cursor.execute('INSERT INTO ob_extras VALUES (?,?,?,?,?)'
                               ,[uid, 0.5, 0.5, 0.0, 0.0])
                
            test=test+1
           
        file.close()

connection.commit()
connection.close()
