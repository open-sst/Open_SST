import sqlite3
import numpy as np
import numpy.ma as ma
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


class grid:

    def __init__(self, xres, yres):


        lons = np.arange(-180.0+xres/2.,180.0+xres/2.,xres)
        lats = np.arange(-90.0+yres/2.,90.0+yres/2.,yres)

        lats, lons = np.meshgrid(lats, lons)

        self.longitudes = lons
        self.latitudes = lats

        self.xres = xres
        self.yres = yres

        self.nx = int(360/xres)
        self.ny = int(180/yres)

        self.data, self.nobs = np.meshgrid(np.zeros(self.ny),np.zeros(self.nx))
        self.data[:,:] = None
        self.sd, self.nships = np.meshgrid(np.zeros(self.ny),np.zeros(self.nx))
        self.sd[:,:] = None

    def plot(self):

        masked = ma.masked_values(self.data, -999)

        fig = plt.figure()
        ax = fig.add_axes([0.05,0.05,0.9,0.9])
        m = Basemap(projection='kav7',lon_0=0,resolution=None)
        #m.drawcoastlines()
        m.drawmapboundary(fill_color='1')
        im1 = m.pcolormesh(self.longitudes,self.latitudes,masked,shading='flat',cmap=plt.cm.RdBu,latlon=True)
        m.drawparallels(np.arange(-90.,99.,30.))
        m.drawmeridians(np.arange(-180.,180.,60.))
        cb = m.colorbar(im1,"bottom", size="5%", pad="2%")
        ax.set_title('SST analysis for ')
        plt.show()

    def plot_sd(self):

        masked = ma.masked_values(self.sd, -999)

        fig = plt.figure()
        ax = fig.add_axes([0.05,0.05,0.9,0.9])
        m = Basemap(projection='kav7',lon_0=0,resolution=None)
        #m.drawcoastlines()
        m.drawmapboundary(fill_color='1')
        im1 = m.pcolormesh(self.longitudes,self.latitudes,masked,shading='flat',cmap=plt.cm.RdBu,latlon=True)
        m.drawparallels(np.arange(-90.,99.,30.))
        m.drawmeridians(np.arange(-180.,180.,60.))
        cb = m.colorbar(im1,"bottom", size="5%", pad="2%")
        ax.set_title('Stdev SST')
        plt.show()

    def plot_nobs(self):

        masked = ma.masked_values(self.nobs, 0.0)

        fig = plt.figure()
        ax = fig.add_axes([0.05,0.05,0.9,0.9])
        m = Basemap(projection='kav7',lon_0=0,resolution=None)
        #m.drawcoastlines()
        m.drawmapboundary(fill_color='1')
        im1 = m.pcolormesh(self.longitudes,self.latitudes,masked,shading='flat',cmap=plt.cm.RdBu,latlon=True)
        m.drawparallels(np.arange(-90.,99.,30.))
        m.drawmeridians(np.arange(-180.,180.,60.))
        cb = m.colorbar(im1,"bottom", size="5%", pad="2%")
        ax.set_title('Nobs')
        plt.show()

    def total_nobs(self):
        return sum(sum(self.nobs))
        
    def area_average(self):

        weights = np.cos(self.latitudes*np.pi/180.)
        
        sum_weighted_data = 0.0
        sum_weights = 0.0

        for xx in range(0,self.nx):
            for yy in range(0,self.ny):

                if self.nobs[xx,yy] != 0.0 :

                    sum_weighted_data += (self.data[xx,yy] * weights[xx,yy])
                    sum_weights += weights[xx,yy]

        if sum_weights != 0:
            area_average = sum_weighted_data/sum_weights
        else:
            area_average = None

        return area_average

    def xbox(self, longitude):
        if longitude > 180.0:
            longitude = -180.0 + (longitude-180.0)
        xx = int((longitude + 180.)/self.xres)
        if xx >= self.nx:
            xx=0
        return xx

    def ybox(self, latitude):
        yy = int((latitude + 90.)/self.yres)
        if yy >= self.ny:
            yy = self.ny-1
        if yy < 0:
            yy = 0
        return yy
    

    def add_obs(self, latitudes, longitudes, ssts, normals):

        n = len(latitudes)

        for i in range(0,n):
            anom = ssts[i] - normals[i]
           # print anom, self.xbox(longitudes[i]), self.ybox(latitudes[i])
            if self.nobs[ self.xbox(longitudes[i]), self.ybox(latitudes[i]) ] == 0.0:
                self.data[ self.xbox(longitudes[i]), self.ybox(latitudes[i]) ] = anom
                self.sd[ self.xbox(longitudes[i]), self.ybox(latitudes[i]) ] = anom*anom
                self.nobs[ self.xbox(longitudes[i]), self.ybox(latitudes[i]) ] =  1.0
            else:
                self.data[ self.xbox(longitudes[i]), self.ybox(latitudes[i]) ] += anom
                self.sd[ self.xbox(longitudes[i]), self.ybox(latitudes[i]) ] += (anom*anom)
                self.nobs[ self.xbox(longitudes[i]), self.ybox(latitudes[i]) ] +=  1.0

        for xx in range(0,self.nx):
            for yy in range(0,self.ny):
                if self.nobs[xx,yy] != 0.0:
                    self.data[xx,yy] = self.data[xx,yy] / self.nobs[xx,yy]
                    self.sd[xx,yy] = np.sqrt( (self.sd[xx,yy] / self.nobs[xx,yy] ) - (self.data[xx,yy]*self.data[xx,yy]) )
                else:
                    self.data[xx,yy] = -999.
                    self.sd[xx,yy] = -999.

data = grid(5.0,5.0)
data.add_obs([0.0,0.0],[0.0,0.0],[20.,20.],[19.,19.])
print data.area_average()

connection = sqlite3.connect('Data\ICOADS.db')
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM qc WHERE track_check = 0")
print "Passed track check ",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE sst_freeze_check = 0")
print "Passed SST freeze check",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE sst_climatology_check = 0")
print "Passed SST climatology check",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE sst_no_normal = 0")
print "Passed No Normal",cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM qc WHERE fewsome_check = 0")
print "Passed Fewsome check",cursor.fetchone()[0]

for years in range(1850,1852):
    for months in range(1,13):
#        years = 1850
#        months = 1

        latitudes = []
        longitudes = []
        ssts = []
        climav = []
        anoms = []

        for rows in cursor.execute('SELECT marinereports.uid, \
                    marinereports.latitude, marinereports.longitude, marinereports.sst, \
                    ob_extras.climatological_average \
                    FROM marinereports \
                    INNER JOIN ob_extras ON marinereports.uid = ob_extras.uid \
                    INNER JOIN qc ON marinereports.uid = qc.uid \
                    WHERE marinereports.year=? AND marinereports.month=? \
                    AND qc.track_check = 0 AND qc.sst_no_normal = 0 \
                    AND qc.sst_climatology_check = 0 AND qc.fewsome_check = 0 \
                    AND qc.sst_freeze_check = 0',[years,months]):
    
            latitudes.append(rows[1])
            longitudes.append(rows[2])
            ssts.append(rows[3])
            climav.append(rows[4])
            anoms.append(rows[3]-rows[4])

        data  = grid(5.0,5.0)
        data.add_obs(latitudes,longitudes,ssts,climav)

        print data.area_average()
        print data.total_nobs()

data.plot_sd()
data.plot_nobs()
data.plot()

connection.close()

