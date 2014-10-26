import sqlite3
from imma_classes import imma

connection = sqlite3.connect('Data\ICOADS.db')

cursor = connection.cursor()

cursor.execute('CREATE TABLE marinereports (id text, year real, month real, day real, hour real, latitude real, longitude real, sst real, at real)')

file = open('Data\IMMA_R2.5.1850.01.man',"r")

for line in file:
    report = imma()
    report.read_record(line)
    assert report.valid_imma
    cursor.execute('INSERT INTO marinereports VALUES (?,?,?,?,?,?,?,?,?)',[report.id,report.yr,report.mo,report.dy,report.hr,report.lat,report.lon,report.sst,report.at])

file.close()

connection.commit()

connection.close()
