import sqlite3
import imp

foo = imp.load_source('IMMA.py', '..\IMMA\Python\IMMA.py')

connection = sqlite3.connect('Data\ICOADS.db')
cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS marinereports')
cursor.execute('CREATE TABLE marinereports (uid text, id text, year real, month real, day real, \
    hour real, latitude real, longitude real, sst real, at real, country text, \
    sst_method int, deck int, source_id int, platform_type int)')
cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS uid ON marinereports (uid)')


for year in range(1850,1851):
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
            cursor.execute('INSERT INTO marinereports VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
                   ,[uid, x.data['ID'],x.data['YR'],x.data['MO'],x.data['DY'],x.data['HR'], \
                     x.data['LAT'],x.data['LON'],x.data['SST'],x.data['AT'],x.data['C1'], \
                     x.data['SI'],x.data['DCK'],x.data['SID'],x.data['PT']])
            test=test+1
            
        file.close()

connection.commit()
connection.close()
