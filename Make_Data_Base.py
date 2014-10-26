import sqlite3
#from imma_classes import imma

connection = sqlite3.connect('Data\ICOADS.db')

cursor = connection.cursor()

cursor.execute('CREATE TABLE marinereports (id text, year real, month real, day real, hour real, latitude real, longitude real, sst real, at real)')

file = open('Data\IMMA_R2.5.1850.01.man',"r")

#for line in file:
#    report = imma()
#    report.read_record(line)
#    assert report.valid_imma
#    cursor.execute('INSERT INTO marinereports VALUES (?,?,?,?,?,?,?,?,?)',[id,yr,mo,dy,hr,lat,lon,sst,at])

for line in file:
    yr = int(line[0:3+1])
    mo = int(line[4:5+1])
    dy = int(line[6:7+1])
    hr = line[8:11+1]
    if hr == "    ":
        hr = None
    else:
        hr = float(hr)/100.
    lat = float(line[12:16+1])/100.
    lon = float(line[17:22+1])/100.
    im = line[23:24+1]
    attc = line[25:25+1]
    ti = line[26:26+1]
    li = line[27:27+1]
    ds = line[28:28+1]
    vs = line[29:29+1]
    nid = line[30:31+1]
    ii = line[32:33+1]
    id = line[34:42+1]
    c1 = line[43:44+1]
    di = line[45:45+1]
    d = line[46:48+1]
    wi = line[49:49+1]
    w = line[50:52+1]
    vi = line[53:53+1]
    vv = line[54:55+1]
    ww = line[56:57+1]
    w1 = line[58:58+1]
    slp = line[59:63+1]
    a = line[64:64+1]
    ppp = line[65:67+1]
    it = line[68:68+1]
    at = line[69:72+1]
    if at == "    ":
        at = None
    else:
        at = float(at)/10.
    wbti = line[73:73+1]
    wbt = line[74:77+1]
    dpti = line[78:78+1]
    dpt = line[79:82+1]
    si = line[83:84+1]
    sst = line[85:88+1]
    if sst == "    ":
        sst = None
    else:
        sst = float(sst)/10.
    n = line[89:89+1]
    nh = line[90:90+1]
    cl = line[91:91+1]
    hi = line[92:92+1]
    h = line[93:93+1]
    cm = line[94:94+1]
    ch = line[95:95+1]
    wd = line[96:97+1]
    wp = line[98:99+1]
    wh = line[100:101+1]
    sd = line[102:103+1]
    sp = line[104:105+1]
    sh = line[106:107+1]
    atti = line[108:109+1]
    attl = line[110:111+1]
    bsi = line[112:112+1]
    b10 = line[113:115+1]
    b1 = line[116:117+1]
    dck = int(line[118:120+1])
    sid = line[121:123+1]
    pt = int(line[124:125+1])
    dups = line[126:127+1]
    dupc = line[128:128+1]
    tc = line[129:129+1]
    pb = line[130:130+1]
    wx = line[131:131+1]
    sx = line[132:132+1]
    c2 = line[133:134+1]
    cursor.execute('INSERT INTO marinereports VALUES (?,?,?,?,?,?,?,?,?)',[id,yr,mo,dy,hr,lat,lon,sst,at])

file.close()

connection.commit()

connection.close()
