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
        self.unc, self.unc2 = np.meshgrid(np.zeros(self.ny),np.zeros(self.nx))
        self.unc[:,:] = None
        self.unc2[:,:] = None

    def plot_masked(self, masked, title):

        fig = plt.figure()
        ax = fig.add_axes([0.05,0.05,0.9,0.9])
        m = Basemap(projection='kav7',lon_0=0,resolution=None)
        #m.drawcoastlines()
        m.drawmapboundary(fill_color='1')
        im1 = m.pcolormesh(self.longitudes,self.latitudes,masked,shading='flat',cmap=plt.cm.RdBu,latlon=True)
        m.drawparallels(np.arange(-90.,99.,30.))
        m.drawmeridians(np.arange(-180.,180.,60.))
        cb = m.colorbar(im1,"bottom", size="5%", pad="2%")
        ax.set_title('SST analysis for '+title)
        plt.show()


    def plot(self):
        masked = ma.masked_values(self.data, -999)
        self.plot_masked(masked, '')

    def plot_sd(self):
        masked = ma.masked_values(self.sd, -999)
        self.plot_masked(masked, 'StDev')
 
    def plot_nobs(self):
        masked = ma.masked_values(self.nobs, 0.0)
        self.plot_masked(masked, 'Nobs')

    def plot_nships(self):
        masked = ma.masked_values(self.nships, 0.0)
        self.plot_masked(masked, 'Nships')

    def plot_uncertainty(self):
        masked = ma.masked_values(self.unc, -999)
        self.plot_masked(masked, 'Uncertainty')

    def total_nobs(self):
        return sum(sum(self.nobs))


    def area_average_uncertainty(self):

#assumes grid box uncertainties are uncorrelated
        weights = np.cos(self.latitudes*np.pi/180.)
        
        sum_weighted_data = 0.0
        sum_weights = 0.0

        for xx in range(0,self.nx):
            for yy in range(0,self.ny):

                if self.nobs[xx,yy] != 0.0 :

                    sum_weighted_data += (self.unc[xx,yy] * self.unc[xx,yy] * weights[xx,yy] * weights[xx,yy])
                    sum_weights += weights[xx,yy]

        if sum_weights != 0:
            area_average = np.sqrt( sum_weighted_data / (sum_weights*sum_weights) )
        else:
            area_average = None

        return area_average

        
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

    def add_obs_by_ship(self, latitudes, longitudes, ssts, normals, ids):

        n = len(latitudes)

        random_unc = 0.8
        micro_bias_unc = 0.8

        unique_ids = set(ids)

        sig_ni_mi, sig_nisq_bi = np.meshgrid(np.zeros(self.ny),np.zeros(self.nx))

#loop over all ships and extract indices for that ship
        for ship in unique_ids:
            indices = [i for i, x in enumerate(ids) if x == ship]

            ni_mi, ship_mask = np.meshgrid(np.zeros(self.ny),np.zeros(self.nx))

            for i in indices:
                anom = ssts[i] - normals[i]
           # print anom, self.xbox(longitudes[i]), self.ybox(latitudes[i])
                xx = self.xbox(longitudes[i])
                yy = self.ybox(latitudes[i])

                if ship_mask[xx,yy] == 0:
                    ship_mask[xx,yy] = 1.0
                
                if self.nobs[xx, yy] == 0.0:
                    self.data[xx, yy] = anom
                    self.sd[xx, yy] = anom*anom
                    self.nobs[xx, yy] =  1.0
                    ni_mi[xx,yy] = 1.0
                else:
                    self.data[xx, yy] += anom
                    self.sd[xx, yy] += (anom*anom)
                    self.nobs[xx, yy] +=  1.0
                    ni_mi[xx,yy] += 1.0 

#at the end of each unique id add up the uncertainty components
            sig_ni_mi = sig_ni_mi + (ni_mi * random_unc * random_unc)
            sig_ni_bi = sig_ni_mi + (ni_mi * ni_mi * micro_bias_unc * micro_bias_unc)
            self.nships = self.nships + ship_mask


        #once all ships have been added, do the final calculations
        for xx in range(0,self.nx):
            for yy in range(0,self.ny):
                if self.nobs[xx,yy] != 0.0:
                    self.data[xx,yy] = self.data[xx,yy] / self.nobs[xx,yy]
                    self.unc[xx,yy] = np.sqrt( (sig_ni_mi[xx,yy] + sig_ni_bi[xx,yy]) / (self.nobs[xx,yy]*self.nobs[xx,yy]) )
                    self.sd[xx,yy] = np.sqrt( (self.sd[xx,yy] / self.nobs[xx,yy] ) - (self.data[xx,yy]*self.data[xx,yy]) )
                else:
                    self.data[xx,yy] = -999.
                    self.unc[xx,yy] = -999.
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


ts = []
tsunc = []

for years in range(1850,1855):
    for months in range(1,13):
#        years = 1850
#        months = 1

        latitudes = []
        longitudes = []
        ssts = []
        climav = []
        anoms = []
        ids = []

        for rows in cursor.execute('SELECT marinereports.uid, \
                    marinereports.latitude, marinereports.longitude, marinereports.sst, \
                    ob_extras.climatological_average, \
                    marinereports.id \
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
            ids.append(str(rows[5]))
            anoms.append(rows[3]-rows[4])

        print "ob by ob", years, months
        data1  = grid(5.0,5.0)
        data1.add_obs(latitudes,longitudes,ssts,climav)
        print "{0:.3f}".format(data1.area_average())
        print data1.total_nobs()

        print "ship by ship", years, months
        data2  = grid(5.0,5.0)
        data2.add_obs_by_ship(latitudes,longitudes,ssts,climav,ids)
        print "{0:.3f}".format(data2.area_average())
        print "{0:.3f}".format(data2.area_average_uncertainty())
        print data2.total_nobs()
#        data2.plot_uncertainty()

        ts.append(data2.area_average())
        tsunc.append(2*data2.area_average_uncertainty())
       
data2.plot_sd()
data2.plot_nobs()
data2.plot_nships()
data2.plot()

ax = range(0,len(ts))

plt.figure()
plt.errorbar(ax,ts,yerr=tsunc)
plt.ylabel('Anomaly')
plt.show()

connection.close()

