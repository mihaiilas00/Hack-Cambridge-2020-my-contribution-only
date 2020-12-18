################################################
# This program receives as input a stream of real-time data in the form of waste collection points
# coordinates and percentage of fullness, as well as the type of reclycling material corresponding to each of these bins
# 
# It then stores this data in a queue and considers clusters of such bins to suggest the most optimal placement of new bins 
# and their material type, in order to avoid overflow. 
#
# The program makes use of techniques such as OOP programming and multi-threading (threads for data collection, periodic statistics 
# computation and on-demand placement suggestions).
#
# Author: Mihai Ilas
#
################################################


from collections import deque
import os.path
from datetime import datetime
import time
from threading import Thread
from threading import Condition
import math

Flag=0
No_of_bins=500
list_of_bins=[]
BINS=deque([],maxlen=240)
buffer=[]
dict_averages={}
dict_existing={}
dict_need={}
dict_coordinates={}
suggested_coordinates=[]


class Bins():
    def __init__(self, ID, full, plastic, glass, paper, number):
        self.ID=ID
        self.full=full
        self.number=number
        if number!=0:
            self.plastic=(100*plastic)/number
            self.glass=(100*glass)/number
            self.paper=(100*paper)/number
        else:
            self.plastic=plastic
            self.glass=glass
            self.paper=paper

class Coordinates():
    def __init__(self, ID, full, x,y):
        self.ID=ID
        self.full=full
        
        self.x=x
        self.y=y
        
        
def stats(bins_list):
    global dict_averages
    
    length=len(bins_list)
   
    Sum=0
    for j in range(len(bins_list[0])):
            Sum=0
            for i in range(length):
                Sum+=bins_list[i][j].full
            Average=Sum/length
            dict_averages[bins_list[0][j].ID].full=Average

    for j in range(len(bins_list[0])):
            Sum=0
            for i in range(length):
                Sum+=bins_list[i][j].plastic
            Average=Sum/length
            dict_averages[bins_list[0][j].ID].plastic=Average

    for j in range(len(bins_list[0])):
            Sum=0
            for i in range(length):
                Sum+=bins_list[i][j].glass
            Average=Sum/length
            dict_averages[bins_list[0][j].ID].glass=Average

    for j in range(len(bins_list[0])):
            Sum=0
            for i in range(length):
                Sum+=bins_list[i][j].paper
            Average=Sum/length
            dict_averages[bins_list[0][j].ID].paper=Average

    for j in range(len(bins_list[0])):
            Sum=0
            for i in range(length):
                Sum+=bins_list[i][j].number
            Average=Sum/length
            dict_averages[bins_list[0][j].ID].number=Average

def read():
    
    global BINS
    global list_of_bins
    buffer=[]
    list_of_bins=[]
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'Input.txt')
    file_read = open(file_path, "r")

    
    Time=(datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    Time/=60
    Time=int(Time)
    if Time % 1==0:
        
        for line in file_read:
            buffer=[]
           
            for i in line.strip().split():
                buffer.append(i)
          
            ID=int(buffer[0])
            
            full=int(buffer[1])
            plastic=int(buffer[2])
            glass=int(buffer[3])
            paper=int(buffer[4])
            number=int(buffer[5])
            #x=float(0)
            #y=float(0)
           
            
            bin_temporary=Bins(ID,full,plastic,glass,paper,number)
            list_of_bins.append(bin_temporary)
          
            
      
        BINS.append(list_of_bins)
       
    return BINS

def read_coordinates():
    global BINS
    global dict_averages
    global dict_coordinates
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'Input2.txt')
    file_read2 = open(file_path, "r")

    for line in file_read2:
        buffer=[]
           
        for i in line.strip().split():
            buffer.append(i)

        name=int(buffer[0])
        x=float(buffer[1])
        y=float(buffer[2])
        for j in range(len(BINS[0])):
            if BINS[0][j].ID==name:
                dict_coordinates[BINS[0][j].ID]=Coordinates(BINS[0][j].ID,dict_averages[BINS[0][j].ID].full,x,y)
                    
        
def need(dict_need):
    global dict_averages
    global BINS
    Answer=[]
    for j in range(len(BINS[0])):
        for i in range(3):
            if dict_need[BINS[0][j].ID][i]==1:
                ID=BINS[0][j].ID
                if i==0:
                    material="plastic"
                    percentage=dict_averages[BINS[0][j].ID].plastic
                    
                if i==1:
                    material="glass"
                    percentage=dict_averages[BINS[0][j].ID].glass
                if i==2:
                    material="paper"
                    percentage=dict_averages[BINS[0][j].ID].paper
                Answer.append([ID, material, percentage])
                
    return(Answer)

def always_running_thread():
    
    global BINS
    while(True):
        
        
        BINS=read()
        
       
        time.sleep(10)
       
       
def start_statistics(threshold=40):
    global Flag
    global BINS
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'Output.txt')
    file_write = open(file_path, "w+")

    for j in range(len(BINS[0])):
        dict_averages[BINS[0][j].ID]=Bins(BINS[0][j].ID,0,0,0,0,0)
        if Flag==0:
            dict_existing[BINS[0][j].ID]=[0,0,0]
            dict_need[BINS[0][j].ID]=[0,0,0]
    Flag=1
        
    stats(BINS)
    
    for j in range(len(BINS[0])):
        
        if dict_averages[BINS[0][j].ID].plastic> threshold and dict_existing[BINS[0][j].ID][0]==0:
            dict_need[BINS[0][j].ID][0]=1
        else:
            dict_need[BINS[0][j].ID][0]=0
        if dict_averages[BINS[0][j].ID].glass> threshold and dict_existing[BINS[0][j].ID][1]==0:
            dict_need[BINS[0][j].ID][1]=1
        else:
            dict_need[BINS[0][j].ID][1]=0
        if dict_averages[BINS[0][j].ID].paper> threshold and dict_existing[BINS[0][j].ID][2]==0:
            dict_need[BINS[0][j].ID][2]=1
        else:
            dict_need[BINS[0][j].ID][2]=0


    Answer=need(dict_need)
    print("Bins to be added")
    for element in Answer:
        print(element)
    
    for item in Answer:
        for i in range(3):
            
            file_write.write(str(item[i]))
            file_write.write(" ")
        file_write.write("\n")
    file_write.close()
    
def trigger_stats():
    
    global BINS
    #always_running_thread.join()
    while(True):
        #c.acquire()
        if len(BINS)>0:
            start_statistics()
        

        #c.notify_all()
        #c.release()
        time.sleep(10)


def finding_clusters(Full_limit=60):
    global dict_coordinates
    global suggested_coordinates
    max1=max2=max3=max4=1000000
    for element1 in dict_coordinates:
        Full_sum=deque([0,0,0,0])
        X_sum=deque([0,0,0,0])
        Y_sum=deque([0,0,0,0])
        Full_total=0
        X_total=0
        Y_total=0
        for element2 in dict_coordinates:
            counter=0
            Distance=math.sqrt((dict_coordinates[element1].x-dict_coordinates[element2].x)**2+(dict_coordinates[element1].y-dict_coordinates[element2].y)**2)
            if Distance<max1:
                max1=Distance
                Full_sum=insert(0,Full_sum,dict_coordinates[element2].full)
                Full_sum.pop()
                X_sum=insert(0,X_sum,dict_coordinates[element2].x)
                X_sum.pop()
                Y_sum=insert(0,Y_sum,dict_coordinates[element2].y)
                Y_sum.pop()
                
            elif Distance<max2:
                max2=Distance
                Full_sum=insert(1,Full_sum,dict_coordinates[element2].full)
                Full_sum.pop()
                X_sum=insert(1,X_sum,dict_coordinates[element2].x)
                X_sum.pop()
                Y_sum=insert(1,Y_sum,dict_coordinates[element2].y)
                Y_sum.pop()
                
            elif Distance<max3:
                max3=Distance
                Full_sum=insert(2,Full_sum,dict_coordinates[element2].full)
                Full_sum.pop()
                X_sum=insert(2,X_sum,dict_coordinates[element2].x)
                X_sum.pop()
                Y_sum=insert(2,Y_sum,dict_coordinates[element2].y)
                Y_sum.pop()
                
            elif Distance<max4:
                max4=Distance
                Full_sum=insert(3,Full_sum,dict_coordinates[element2].full)
                Full_sum.pop()
                X_sum=insert(3,X_sum,dict_coordinates[element2].x)
                X_sum.pop()
                Y_sum=insert(3,Y_sum,dict_coordinates[element2].y)
                Y_sum.pop()
                
            for i in range(4):
                Full_total+=Full_sum[i]
                X_total+=X_sum[i]
                Y_total+=Y_sum[i]

            Full_total+=dict_coordinates[element1].full
            X_total+=dict_coordinates[element1].x
            Y_total+=dict_coordinates[element1].y

            if Full_total>Full_limit*5:
                x_suggested=X_total/5
                y_suggested=Y_total/5
                suggested_coordinates.append((x_suggested,y_suggested))

            else:
                X_total-=X_sum[3]
                Y_total-=Y_sum[3]
                Full_total-=Full_sum[3]
                if Full_total>Full_limit*4:
                    x_suggested=X_total/4
                    y_suggested=Y_total/4
                    suggested_coordinates.append((x_suggested,y_suggested))
                    
                else:
                    X_total-=X_sum[2]
                    Y_total-=Y_sum[2]
                    Full_total-=Full_sum[2]
                    if Full_total>Full_limit*3:
                        x_suggested=X_total/3
                        y_suggested=Y_total/3
                        suggested_coordinates.append((x_suggested,y_suggested))
                        
    suggested_coordinates=list(set(suggested_coordinates))
    return suggested_coordinates

def insert(i,queue,element):
    
    queue.append(0)
    for j in range(len(queue)-2,i-1,-1):
        queue[j+1]=queue[j]
    
    queue[i]=element
    return queue
                
def trigger_coordinates():
    global BINS
    global dict_averages
    script_dir = os.path.dirname(__file__)
    file_path2 = os.path.join(script_dir, 'Output_coordinates.txt')
    
            
    while(True):
        file_write2 = open(file_path2, "w+")
        read_coordinates()
        suggested_coordinates=finding_clusters()
        print("New bins needed at")
        for j in range(len(suggested_coordinates)):
            print(suggested_coordinates[j][0]," ",suggested_coordinates[j][1])
           
        for element in suggested_coordinates:
        
            file_write2.write(str(element[0]))
            file_write2.write(" , ")
            file_write2.write(str(element[1]))
            file_write2.write("\n")

        file_write2.close()
        time.sleep(10)

            
always_running_thread = Thread(target=always_running_thread, args=())       #Reading input data in a thread
always_running_thread.start()

time.sleep(2)

stats_thread = Thread(target=trigger_stats, args=())    #Running the statistic analysis in a second thread

stats_thread.start()

time.sleep(2)

coordinates=Thread(target=trigger_coordinates,args=())
coordinates.start()

always_running_thread.join()
stats.join()
coordinates.join()
  
