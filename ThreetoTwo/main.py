import math
import random
import copy
refreshRate = 0.1 #time of refreshing rate in second
vdesire = 30 #desired speed with infinite gap
w = 2 #minimum stationary distance
T = 3   #refresh timing = (T-1)*refreshRate
time = 1.8 #time interval between cars
carspermin = 60/time #How many cars per minute
universalplannum = 3
signLength = 300
mergeTime = 1
timeLine = 0.0
stats = []




def probabilityCalculation(x,desiredx):   #x is defined as how many cars per minute
    #print x
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
        if self in self.road.carsmiddle:
            while i < len(self.road.carsleft):
                if self.road.carsleft[i].position[-1] < self.position[-1]:
                    found = True
                    break
                i += 1
        elif self in self.road.carsright:
            while i < len(self.road.carsmiddle):
                if self.road.carsmiddle[i].position[-1] < self.position[-1]:
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
        elif self in self.road.carsmiddle:
            if self == self.road.carsmiddle[0]:
                virp = self.road.middlelength+self.carlength
                virtualCar = CAR(0,virp,self.road,0,0)
                virtualCar.velocity=[0,0,0,0,0,0,0,0,0,0,0]
                virtualCar.position=[virp,virp,virp,virp,virp,virp]
                return virtualCar
            for i in range(1,len(self.road.carsmiddle)):
                if self == self.road.carsmiddle[i]:
                    return self.road.carsmiddle[i-1]
        elif self in self.road.carsright:
            if self == self.road.carsright[0]:
                virp = self.road.rightlength+self.carlength
                virtualCar = CAR(0,virp,self.road,0,0)
                virtualCar.velocity=[0,0,0,0,0,0,0,0,0,0,0]
                virtualCar.position=[virp,virp,virp,virp,virp,virp]
                return virtualCar
            for i in range(1,len(self.road.carsright)):
                if self == self.road.carsright[i]:
                    return self.road.carsright[i-1]



    def update(self):
        if self.readytodeletion:
            if self.deletionCount>=(mergeTime/refreshRate):
                if self in self.road.carsmiddle:
                    self.road.carsmiddle.remove(self)
                    return 1
                elif self in self.road.carsright:
                    self.road.carsright.remove(self)
                    return 2
            self.deletionCount+=1
        if (self in self.road.carsright) or (self in self.road.carsmiddle):
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
                if self in self.road.carsright:
                    self.z = 1
                else:
                    self.z = 0
            elif self.plannumber == 2:
                if self in self.road.carsright:
                    if self == self.road.carsright[0]:
                        self.z = 1
                    else:
                        self.z = 0
                else:
                    self.z = 0
            elif self.plannumber == 3:
                if self.findleftbackcarindex()==-1:
                    self.z = 1
                    return
                if self in self.road.carsmiddle:
                    leftbackv = self.road.carsleft[self.findleftbackcarindex()].velocity[-1]
                    selfv = self.velocity[-1]
                    if leftbackv<=selfv:
                        self.z = 0
                    else:
                        self.z = 1
                elif self in self.road.carsright:
                    leftbackv = self.road.carsmiddle[self.findleftbackcarindex()].velocity[-1]
                    selfv = self.velocity[-1]
                    if leftbackv<=selfv:
                        self.z = 0
                    else:
                        self.z = 1
        else:
            self.z = 0


    def whetherMerge(self):
        previousIndex = self.findleftbackcarindex()
        if self in self.road.carsmiddle:
            if previousIndex == -1:
                if len(self.road.carsleft) == 0:
                    return True
                else:
                    frontLeftCar = self.road.carsleft[-1]
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
        elif self in self.road.carsright:
            if previousIndex == -1:
                if len(self.road.carsmiddle) == 0:
                    return True
                else:
                    frontLeftCar = self.road.carsmiddle[-1]
                    t = 0.1
                    allowed = True
                    while t < mergeTime:
                        if min(2*(frontLeftCar.position[-1]-self.position[-1]+frontLeftCar.velocity[-1]*t-self.velocity[-1]*t-(self.velocity[-1]**2/2/self.decceleration+self.carlength+w))/t**2,self.acceleration) < -self.decceleration:
                            allowed = False
                            break
                        t += 0.2
                    return allowed
            else:
                if len(self.road.carsmiddle) == 1:
                    backLeftCar = self.road.carsmiddle[previousIndex]
                    t = 0.1
                    allowed = True
                    while t < mergeTime:
                        if max(2*(backLeftCar.position[-1]-self.position[-1]-self.velocity[-1]*t+backLeftCar.velocity[-1]*t+backLeftCar.velocity[-1]**2/2/self.decceleration +self.carlength+w)/t**2,-self.decceleration) > self.acceleration:
                            allowed = False
                        t += 0.2
                    return allowed
                else:
                    backLeftCar = self.road.carsmiddle[previousIndex]
                    frontLeftCar = self.road.carsmiddle[previousIndex-1]
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
    carsmiddle = []
    def __init__(self,l,m,r,lmd):
        self.leftlength = l
        self.middlelength = m
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
                copycar.z = 0
                """
                for car in self.carsleft:
                    print car.position[-1],car.velocity[-1]
                print ""
                for car in self.carsmiddle:
                    print car.position[-1],car.velocity[-1],car.z,car.whetherMerge()
                print ""
                for car in self.carsright:
                    print car.position[-1],car.velocity[-1],car.z,car.whetherMerge()
                print "\n\n\n"
                """
                self.carsmiddle.insert(leftbackindex,copycar)
                self.carsright[i].readytodeletion = True
            if self.carsright[i].update()==2:
                continue
            i+=1

    def updatemiddlecars(self):
        if len(self.carsmiddle)==0:
            return
        self.carsmiddle[0].updateFirstguy()
        if self.carsmiddle[0].position[-1]>self.middlelength:
            if self.carsmiddle[0].readytodeletion==False:
                self.carsmiddle[0].endtime = timeLine
                stats.append(copy.deepcopy(self.carsmiddle[0]))
                self.carsmiddle.remove(self.carsmiddle[0])
            if len(self.carsmiddle)==0:
                return
            self.carsmiddle[0].updateFirstguy()
        i = 1
        while i<len(self.carsmiddle):
            if self.carsmiddle[i].whetherMerge() and self.carsmiddle[i].z==1:
                leftbackindex = self.carsmiddle[i].findleftbackcarindex()
                copycar = copy.deepcopy(self.carsmiddle[i])
                copycar.plannumber = 0
                copycar.z = -1
                """
                for car in self.carsleft:
                    print car.position[-1],car.velocity[-1]
                print ""
                for car in self.carsmiddle:
                    print car.position[-1],car.velocity[-1],car.z,car.whetherMerge()
                print ""
                for car in self.carsright:
                    print car.position[-1],car.velocity[-1],car.z,car.whetherMerge()
                print "\n\n\n"
                """
                self.carsleft.insert(leftbackindex,copycar)
                self.carsmiddle[i].readytodeletion = True
            if self.carsmiddle[i].update()==1:
                continue
            i+=1

    def rollover(self):  #in second
        loopCount = int(instantinputrate_insec()/refreshRate)
        global timeLine
        for i in range(0,loopCount):
            self.updaterightcars()
            self.updateleftcars()
            self.updatemiddlecars()
            timeLine += refreshRate

    def insertAcarleft(self):
        self.carsleft.append(CAR(vdesire,0,self,0,timeLine))

    def insertAcarright(self):
        self.carsright.append(CAR(vdesire,0,self,universalplannum,timeLine))

    def insertAcarmiddle(self):
        self.carsmiddle.append(CAR(vdesire,0,self,universalplannum,timeLine))



icount = 22
all = []
iInt = 0
while icount < 29:
    carspermin = icount
    all.append([])
    for j in range(1,4):
        universalplannum = j
        sumcount = 0
        pq = 0
        pr = 0
        for k in range(0,10):
            myRoad = ROAD(2500,2500,2000,0)
            stats = []
            while len(stats)<40:
                myRoad.insertAcarleft()
                myRoad.rollover()
                myRoad.insertAcarmiddle()
                myRoad.rollover()
                myRoad.insertAcarright()
                myRoad.rollover()

            while len(myRoad.carsleft)!=0 or len(myRoad.carsright)!=0 or len(myRoad.carsmiddle)!=0:
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
        all[iInt].append([avgvariance,avgavgwait])
    print all
    icount+=1
    iInt+=1