import math
import random
import copy
refreshRate = 0.1 #time of refreshing rate in second
vdesire = 30 #desired speed with infinite gap
w = 2 #minimum stationary distance
T = 2   #refresh timing = (T-1)*refreshRate
time = 3 #time interval between cars
carspermin = 60/time #How many cars per minute
universalplannum = 3
signLength = 1600
mergeTime = 1
timeLine = 0.0
stats = []




def probabilityCalculation(x,desiredx):   #x is defined as how many cars per minute
    if x==0:
        return math.e**(-desiredx)
    prob = float(probabilityCalculation(x-1,desiredx))*float(desiredx)/float(x)
    return prob

def getinstantinputrate():
    p = []
    for i in range(0,int(2*carspermin+1)):
        p.append(probabilityCalculation(i,carspermin))
        if (i>=1):
            p[i] = p[i]+p[i-1]
    a = random.random()
    while a>=p[-1]:
        a = random.random()
    for i in range(2,int(2*carspermin+1)):
        if a<p[i]:
            return i-1;

def instantinputrate_insec():
    a = getinstantinputrate()
    return int(60/a)

class CAR:
    carlength = 5.5
    decceleration = 5
    acceleration = 5

    def findleftbackcarindex(self):
        i = 0
        found = False
        while i < len(self.road.carsleft):
            if self.road.carsleft[i].position[-1] < self.position[-1]:
                found = True
                break
            i += 1
        if found:
            return i
        else:
            return -1


    def __init__(self,v,x,road,plannumber,start):
        self.velocity = [v]
        self.safespeed = []
        self.position = [x]
        self.road = road
        self.plannumber = plannumber
        self.starttime = start
        self.endtime = start
        if plannumber==0:
            self.z = -1
        else:
            self.z = 0
        self.readytodeletion = False
        self.deletionCount = 0
        #self.decceleration = [0]

    def findfrontcar(self):  #return the car object in front of self
        if self in self.road.carsleft:
            for i in range(1,len(self.road.carsleft)):
                if self == self.road.carsleft[i]:
                    return self.road.carsleft[i-1]
        else:
            if self == self.road.carsright[0]:
                virp = self.road.rightlength+self.carlength
                virtualCar = CAR(0,virp,self.road,0,timeLine)
                virtualCar.velocity=[0,0,0,0,0,0,0,0,0,0,0]
                virtualCar.position=[virp,virp,virp,virp,virp,virp]
                return virtualCar
            for i in range(1,len(self.road.carsright)):
                if self == self.road.carsright[i]:
                    return self.road.carsright[i-1]



    def update(self):
        if self.readytodeletion:
            if self.deletionCount>=(mergeTime/refreshRate):
                if self in self.road.carsright:
                    self.road.carsright.remove(self)
                    return 1
            self.deletionCount+=1
        if self in self.road.carsright:
            self.updateZ()
        frontv = self.findfrontcar().velocity[-1-T]
        frontp = self.findfrontcar().position[-1-T]
        xnew = self.position[-1]+self.velocity[-1]*refreshRate
        vpre = self.velocity[-1]
        ppre = self.position[-1]
        va = vpre + 2.5*self.acceleration*refreshRate*(1-vpre/vdesire)*math.sqrt(0.025+vpre/vdesire)
        d = self.decceleration
        #d = 5
        t = refreshRate
        Sn = 2*vpre+self.carlength+w
        #vb = d*t+math.sqrt(d*t*d*t-d*(2*(frontp-Sn-ppre)-vpre*refreshRate-frontv*frontv/d))   #FREAKING AWESOME MODEL FAILED
        #vb = vpre - d*refreshRate           #SIMPLE MODEL(Bullshit)
        #print Sn,frontp,ppre,frontv
        if (t*t-2*(Sn)/d+2*(frontp-ppre-self.carlength)/d+frontv*frontv/d/d)>=0:
            vb = d*(math.sqrt(t*t-2*(Sn)/d+2*(frontp-ppre-self.carlength)/d+frontv*frontv/d/d)-t)
        else:
            vb = vpre - d*refreshRate
        if min(va,vb)==vb:
            if vb<vpre-d*refreshRate:
                vb = vpre-d*refreshRate
        self.position.append(xnew)
        self.safespeed.append(vb)
        if min(va,vb)<0:
            self.velocity.append(0)
        else:
            self.velocity.append(min(va,vb))


    def updateFirstguy(self):
        xnew = self.position[-1]+self.velocity[-1]*refreshRate
        self.position.append(xnew)
        vmax = vdesire
        v = self.velocity[-1]+self.acceleration*refreshRate
        self.velocity.append(min(v,vmax))
        #self.decceleration.append(-(self.velocity[-1]-self.velocity[-2])/refreshRate)

    def updateZ(self):
        if self.readytodeletion:
            self.z = 0
            return
        if self.position[-1]>=self.road.signPos:
            if self.plannumber == 1:
                self.z = 1
            elif self.plannumber == 2:
                if self == self.road.carsright[0]:
                    self.z = 1
                else:
                    self.z = 0
            elif self.plannumber == 3:
                if self.findleftbackcarindex()==-1:
                    self.z = 1
                    return
                leftbackv = self.road.carsleft[self.findleftbackcarindex()].velocity[-1]
                selfv = self.velocity[-1]
                if leftbackv<=selfv:
                    self.z = 0
                else:
                    self.z = 1
        else:
            self.z = 0

    def whetherMerge(self):
        previousIndex = self.findleftbackcarindex()
        if previousIndex == -1:
            if len(self.road.carsleft) == 0:
                return True
            else:
                frontLeftCar = self.road.carsleft[-1]    #WTF ---- frontLeftCar = self.road.carsleft[0!!!!]
                t = 0.1
                allowed = True
                while t < mergeTime:
                    if min(2*(frontLeftCar.position[-1]-self.position[-1]+frontLeftCar.velocity[-1]*t-self.velocity[-1]*t-(self.velocity[-1]**2/2/self.decceleration+self.carlength+w))/t**2,self.acceleration) < -self.decceleration:
                        allowed = False
                        break
                    t += 0.2
                return allowed
        else:
            if len(self.road.carsleft) == 1:
                backLeftCar = self.road.carsleft[previousIndex]
                t = 0.1
                allowed = True
                while t < mergeTime:
                    if max(2*(backLeftCar.position[-1]-self.position[-1]-self.velocity[-1]*t+backLeftCar.velocity[-1]*t+backLeftCar.velocity[-1]**2/2/self.decceleration +self.carlength+w)/t**2,-self.decceleration) > self.acceleration:
                        allowed = False
                    t += 0.2
                return allowed
            else:
                backLeftCar = self.road.carsleft[previousIndex]
                frontLeftCar = self.road.carsleft[previousIndex-1]
                t = 0.1
                allowed = True
                while t < mergeTime:
                    k = max(2*(backLeftCar.position[-1]-self.position[-1]-self.velocity[-1]*t+backLeftCar.velocity[-1]*t+backLeftCar.velocity[-1]**2/2/self.decceleration +self.carlength+w)/t**2,-self.decceleration)
                    j = min(2*(frontLeftCar.position[-1]-self.position[-1]+frontLeftCar.velocity[-1]*t-self.velocity[-1]*t-(self.velocity[-1]**2/2/self.decceleration+self.carlength+w))/t**2,self.acceleration)
                    if k>j:
                        allowed = False
                    t += 0.2
                return allowed





class ROAD:
    carsleft = []
    carsright = []
    def __init__(self,l,r,lmd):
        self.leftlength = l
        self.rightlength = r
        self.carspermin = lmd
        self.signPos = self.rightlength-signLength

    def updateleftcars(self):
        if len(self.carsleft)==0:
            return
        self.carsleft[0].updateFirstguy()
        if self.carsleft[0].position[-1]>self.leftlength:
            self.carsleft[0].endtime = timeLine
            stats.append(copy.deepcopy(self.carsleft[0]))
            self.carsleft.remove(self.carsleft[0])
            if len(self.carsleft)==0:
                return
            self.carsleft[0].updateFirstguy()
        for i in range(1,len(self.carsleft)):
            self.carsleft[i].update()
    def updaterightcars(self):
        i = 0
        while i<len(self.carsright):
            if self.carsright[i].whetherMerge() and self.carsright[i].z==1:
                leftbackindex = self.carsright[i].findleftbackcarindex()
                copycar = copy.deepcopy(self.carsright[i])
                copycar.plannumber = 0
                copycar.z = -1
                if leftbackindex != -1:
                    self.carsleft.insert(leftbackindex,copycar)
                else:
                    self.carsleft.append(copycar)
                self.carsright[i].readytodeletion = True
            if self.carsright[i].update()==1:
                continue
            i+=1


    def rollover(self):  #in second
        loopCount = int(instantinputrate_insec()/refreshRate)
        global timeLine
        for i in range(0,loopCount):
            self.updaterightcars()
            self.updateleftcars()
            timeLine += refreshRate
            for j in range(1,len(self.carsleft)):
                if self.carsleft[j-1].position[-1]-self.carsleft[j].position[-1]<=self.carsleft[j].carlength:
                    print "crash"
                    #err = 1/0
            for j in range(1,len(self.carsright)):
                if self.carsright[j-1].position[-1]-self.carsright[j].position[-1]<=self.carsright[j].carlength:
                    print "crash"
                    #err = 1/0

    def insertAcarleft(self):
        self.carsleft.append(CAR(vdesire,0,self,0,timeLine))

    def insertAcarright(self):
        self.carsright.append(CAR(vdesire,0,self,universalplannum,timeLine))

    """
    def setEndtime(self,endt):
        for car in self.carsleft:
            car.endtime = endt
        for car in self.carsright:
            car.endtime = endt
    """
print "15"
i = 18
all = []
iInt = 0
while i < 28:
    carspermin = i
    for j in range(3,4):
        universalplannum = random.randint(1,3)
        sumcount = 0
        pq = 0
        pr = 0
        for k in range(0,10):
            myRoad = ROAD(2500,2000,0)
            stats = []
            while len(stats)<35:
                myRoad.insertAcarleft()
                myRoad.rollover()
                myRoad.insertAcarright()
                myRoad.rollover()

            while len(myRoad.carsleft)!=0 or len(myRoad.carsright)!=0:
                myRoad.rollover()

            waittime = []
            js = 0

            for car in stats:
                cstart = car.starttime
                cend = car.endtime
                cwait = cend-cstart
                #print cstart,cend,cwait
                js += cwait
                waittime.append(cwait)

            avgwait = js/len(stats)
            js = 0
            for cw in waittime:
                js += (cw-avgwait)**2
            variancewait = js/len(stats)
            pq += variancewait
            pr += avgwait
            print variancewait,avgwait
        print ""
        avgavgwait = pr/10
        avgvariance = pq/10
        print avgvariance,avgavgwait
        print ""
        all.append([avgvariance,avgavgwait])
    print all
    i+=1
    iInt+=1