class imma:
    
    def __init__(self):
        self.read_record(' '*150)

    def check_validity(self):
        self.valid_imma = True
        
        if self.yr != None and (self.yr < 1600 or self.yr > 2024):
            self.valid_imma = False
        if self.mo != None and (self.mo < 1 or self.mo > 12):
            self.valid_imma = False
        if self.dy != None and (self.dy < 1 or self.dy > 31):
            self.valid_imma = False
        if self.hr != None and (self.hr < 0 or self.hr > 23.99):
            self.valid_imma = False
        if self.lat != None and (self.lat < -90.00 or self.lat > 90.00):
            self.valid_imma = False
        if self.lon != None and (self.lon < -179.99 or self.lon > 359.99):
            self.valid_imma = False

#ICOADS 2.5 documentation has a numbered list for country id but there are
#alphabetic characters in C1?
#        if self.c1 != None and (self.c1 < 0 or self.c1 > 99):
#            self.valid_imma = False

        if self.at != None and (self.at < -99.9 or self.at > 99.9):
            self.valid_imma = False

        if self.si != None and (self.si < 0 or self.si > 12):
            self.valid_imma = False
        if self.sst != None and (self.sst < -99.9 or self.sst > 99.9):
            self.valid_imma = False


    def set_yr(self, instr):
        if instr == "    ":
            self.yr = None
        else:
            self.yr = int(instr)
       
    def set_mo(self, instr):
        if instr == "  ":
            self.mo = None
        else:
            self.mo = int(instr)

    def set_dy(self, instr):
        if instr == "  ":
            self.dy = None
        else:
            self.dy = int(instr)

    def set_hr(self, instr):
        if instr == "    ":
            self.hr = None
        else:
            self.hr = float(instr)/100.0

    def set_lat(self, instr):
        if instr == "     ":
            self.lat = None
        else:
            self.lat = float(instr)/100.

    def set_lon(self, instr):
        if instr == "      ":
            self.lon = None
        else:
            self.lon = float(instr)/100.

    def set_at(self, instr):
        if instr == "    ":
            self.at = None
        else:
            self.at = float(instr)/10.

    def set_si(self, instr):
        if instr == "  ":
            self.si = None
        else:
            self.si = int(instr)

    def set_sst(self, instr):
        if instr == "    ":
            self.sst = None
        else:
            self.sst = float(instr)/10.

    def set_c1(self, instr):
        if instr == "  ":
            self.c1 = None
        else:
            self.c1 = (instr)


    
    def read_record(self, line):
        self.valid_imma = True
        
        self.set_yr(line[0:3+1])
        self.set_mo(line[4:5+1])
        self.set_dy(line[6:7+1])
        self.set_hr(line[8:11+1])
        self.set_lat(line[12:16+1])
        self.set_lon(line[17:22+1])
        
        self.im = line[23:24+1]
        self.attc = line[25:25+1]
        self.ti = line[26:26+1]
        self.li = line[27:27+1]
        self.ds = line[28:28+1]
        self.vs = line[29:29+1]
        self.nid = line[30:31+1]
        self.ii = line[32:33+1]
        
        self.id = line[34:42+1]  #id is just a string so nothing special to do

        self.set_c1(line[43:44+1])
        
        self.di = line[45:45+1]
        self.d = line[46:48+1]
        self.wi = line[49:49+1]
        self.w = line[50:52+1]
        self.vi = line[53:53+1]
        self.vv = line[54:55+1]
        self.ww = line[56:57+1]
        self.w1 = line[58:58+1]
        self.slp = line[59:63+1]
        self.a = line[64:64+1]
        self.ppp = line[65:67+1]
        self.it = line[68:68+1]
        
        self.set_at(line[69:72+1])
        
        self.wbti = line[73:73+1]
        self.wbt = line[74:77+1]
        self.dpti = line[78:78+1]
        self.dpt = line[79:82+1]
        
        self.set_si(line[83:84+1])
        self.set_sst(line[85:88+1])

        self.n = line[89:89+1]
        self.nh = line[90:90+1]
        self.cl = line[91:91+1]
        self.hi = line[92:92+1]
        self.h = line[93:93+1]
        self.cm = line[94:94+1]
        self.ch = line[95:95+1]
        self.wd = line[96:97+1]
        self.wp = line[98:99+1]
        self.wh = line[100:101+1]
        self.sd = line[102:103+1]
        self.sp = line[104:105+1]
        self.sh = line[106:107+1]
        self.atti = line[108:109+1]
        self.attl = line[110:111+1]
        self.bsi = line[112:112+1]
        self.b10 = line[113:115+1]
        self.b1 = line[116:117+1]
        self.dck = line[118:120+1]
        self.sid = line[121:123+1]
        self.pt = line[124:125+1]
        self.dups = line[126:127+1]
        self.dupc = line[128:128+1]
        self.tc = line[129:129+1]
        self.pb = line[130:130+1]
        self.wx = line[131:131+1]
        self.sx = line[132:132+1]
        self.c2 = line[133:134+1]

        self.check_validity()
