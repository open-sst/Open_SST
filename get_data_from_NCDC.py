import urllib
from random import randint
from time import sleep


for year in range(1890,1900):
    for month in range(1,13):

        print year,month
        smn = str(month)
        syr = str(year)
        if month < 10:
            smn = '0'+smn
        yrmn = syr + smn

        testfile = urllib.URLopener()
        testfile.retrieve("http://www1.ncdc.noaa.gov/pub/data/icoads2.5/"+syr+"/IMMA_R2.5."+syr+"."+smn+"_ENH" \
                          ,"Data/IMMA_R2.5."+syr+"."+smn+".man")

        sleep(randint(1,5))

        
