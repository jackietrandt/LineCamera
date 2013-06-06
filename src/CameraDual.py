'''
Created on 23/04/2013

@author: user
'''
'''
Created on 15/03/2013

@author: Alice

'''
import cv2.cv as cv
import time
import sys
from math import sin, cos, sqrt, pi, fabs
#import wx 
import os
import threading
#queue for threading passing item between thread safely
import Queue


#---------------------------------------------------------------------------# 
# modbus serial com 
#---------------------------------------------------------------------------# 

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import serial.tools.list_ports
import time

class App:
    def __init__(self, param):
        self.init_general_variable()
        self.init_threading_variable()
        self.init_camera()
        self.init_communication()
        pass
    def init_general_variable(self):
        #________Program configuration option______
        self.ModeTest = True # set capture frame resolution 768 x 1024 ___or 1080 x 1920
        self.CameraDebugScreen = False # show raw capture from camera 1 and 2 for alignment and checking ___or disable at run mode
        self.CameraDebugMerge = False # show merged camera screen for positioning and alignment
        self.CameraTHCanny = False # show camera gray threadhold and cannying for parameter tuning
        self.ConsoleDebugLine = False # show line debug information on console screen
        self.ConsoleDebugLineDiff = False # show line trajectory distance from center of the screen , assume product feed through middle of camera screen
        self.ConsoleDebugShortestDistance = False # show debug info for input to shortest distance function 

       
    #---------------------------------------------------------------------------# 
    # D_AddressRef
    #---------------------------------------------------------------------------# 
    #Input address in decimal - then function would convert it to PLC address
    #Address 0x1000 stand for D register in PLC
    #Address 0x0258 stand for 600 in decimal
    #So to write to D600 register in the PLC
    #The reference address is 0x1258
    def init_threading_variable(self):
        #hold list of executing thread
        self.threads = []
        self.event = threading.Event()
        #holding queue for passing object across thread
        self.queueLock_work = threading.Lock()
        self.queueLock_result = threading.Lock()
        self.queueLock_com = threading.Lock()
        self.workQueue = Queue.Queue(20)
        self.resultQueue = Queue.Queue(10)
        self.comQueue = Queue.Queue(10)
        pass
    def init_camera(self):
        #USB camera capture 
        self.capture1 = cv.CaptureFromCAM(0)
        self.capture2 = cv.CaptureFromCAM(1)

        #Configure capture screen resolution
        if self.ModeTest:
            cv.SetCaptureProperty(self.capture1, cv.CV_CAP_PROP_FRAME_HEIGHT, 768)
            cv.SetCaptureProperty(self.capture1, cv.CV_CAP_PROP_FRAME_WIDTH, 1024)
        
            cv.SetCaptureProperty(self.capture2, cv.CV_CAP_PROP_FRAME_HEIGHT, 768)
            cv.SetCaptureProperty(self.capture2, cv.CV_CAP_PROP_FRAME_WIDTH, 1024)
        
        else:
            cv.SetCaptureProperty(self.capture1, cv.CV_CAP_PROP_FRAME_HEIGHT, 1080)
            cv.SetCaptureProperty(self.capture1, cv.CV_CAP_PROP_FRAME_WIDTH, 1920)
        
            cv.SetCaptureProperty(self.capture2, cv.CV_CAP_PROP_FRAME_HEIGHT, 1080)
            cv.SetCaptureProperty(self.capture2, cv.CV_CAP_PROP_FRAME_WIDTH, 1920)    
    def init_communication(self):
        comport_list = list(serial.tools.list_ports.comports())
        if len(comport_list) > 0:
            print '___________________________________________Found the following COM PORT________________________________________________________'
            for port_found in comport_list:
                print port_found[0]
            self.Com_client = ModbusClient(method='ascii', port=comport_list[0][0], baudrate='115200', timeout=1)
            print "Init Modbus :" + comport_list[0][0]
            print "Modbus Client :" , self.Com_client 
        else:
            print 'No COM port found'
    def D_AddressRef(self,d_Address):
        d_Working = 4096
        d_Working = d_Working + d_Address
        return d_Working
    #---------------------------------------------------------------------------# 
    # ShortestDistance
    #---------------------------------------------------------------------------# 
    #function to find shortest distance between 2 line
    #provide 2 point of each line
    #find out what is the 2 closest point 
    #which each belong to a separated line
    def ShortestDistance(self,x1,y1,x2,y2,x3,y3,x4,y4):
        if self.ConsoleDebugShortestDistance:
            print ("x1 = " ,x1)
            print ("y1 = " ,y1)
            print ("x2 = " ,x2)
            print ("y2 = " ,y2)
            print ("x3 = " ,x3)
            print ("y3 = " ,y3)
            print ("x4 = " ,x4)
            print ("y4 = " ,y4)
        #distance 1 3
        x13 = x1 - x3
        y13 = y1 - y3
        distance_1 = (x13*x13 + y13*y13)**0.5
        
        #distance 1 4
        x14 = x1 - x4
        y14 = y1 - y4
        distance_2 = (x14*x14 + y14*y14)**0.5
        
        #distance 2 3
        x23 = x2 - x3
        y23 = y2 - y3
        distance_3 = (x23*x23 + y23*y23)**0.5
    
        #distance 2 4
        x24 = x2 - x4
        y24 = y2 - y4
        distance_4 = (x24*x24 + y24*y24)**0.5
        
        print ("Distance_1 = " ,distance_1)
        print ("Distance_2 = " ,distance_2)
        print ("Distance_3 = " ,distance_3)
        print ("Distance_4 = " ,distance_4)
        
        if (distance_1 < distance_2) and (distance_1 < distance_3) and (distance_1 < distance_4):
            short_x1 = x1
            short_x2 = x3
            short_y1 = y1
            short_y2 = y3
            return short_x1,short_y1,short_x2,short_y2;
        if (distance_2 < distance_1) and (distance_2 < distance_3) and (distance_2 < distance_4):
            short_x1 = x1
            short_x2 = x4
            short_y1 = y1
            short_y2 = y4
            return short_x1,short_y1,short_x2,short_y2;
        if (distance_3 < distance_1) and (distance_3 < distance_2) and (distance_3 < distance_4):
            short_x1 = x2
            short_x2 = x3
            short_y1 = y2
            short_y2 = y3
            return short_x1,short_y1,short_x2,short_y2;
        if (distance_4 < distance_1) and (distance_4 < distance_2) and (distance_4 < distance_3):
            short_x1 = x2
            short_x2 = x4
            short_y1 = y2
            short_y2 = y4
            return short_x1,short_y1,short_x2,short_y2;
    def ReadCamera_1(self):
        while True:
            #img = cv.QueryFrame(capture)
            img1 = cv.QueryFrame(self.capture1)
            img2 = cv.QueryFrame(self.capture2)
            
            self.queueLock_work.acquire()
            if self.workQueue.empty():
                self.workQueue.put(img1)
                self.workQueue.put(img2)
            self.queueLock_work.release()
            cv.WaitKey(2)
        pass
    def EdgeScan(self):
        
        while True:
            

            self.queueLock_work.acquire()
            if not self.workQueue.empty():
                img1 = self.workQueue.get()
                img2 = self.workQueue.get()
            self.queueLock_work.release()

            if self.CameraDebugScreen:
                cv.ShowImage("usbCam_1", img1)
                cv.ShowImage("usbCam_2", img2)
        
            #__Merge__create a holder of the merged image from camera capture 1 and 2
            img_Master = cv.CreateImage((img2.width*2, img2.height), 8, 3)
            #__Merge__set ROI and copy img from camera 1 2 over one by one
            master_x= 0 # co-ordinate of top left vertex.
            master_y= 0 # co-ordinate of top left vertex.
            master_w= img1.width # width or region
            master_h= img1.height # height of region
            cv.SetImageROI(img_Master,(master_x,master_y,master_w,master_h))
            cv.Copy(img1, img_Master)
            #__Merge__now copy the second camera image over
            master_x= img2.width # co-ordinate of top left vertex.
            cv.ResetImageROI(img_Master)
            cv.SetImageROI(img_Master,(master_x,master_y,master_w,master_h))
            cv.Copy(img2, img_Master)
            cv.ResetImageROI(img_Master)
            if self.CameraDebugMerge:
                cv.ShowImage("cameraMerge",img_Master)
            
            # convert to grayscale
            gray = cv.CreateImage((img_Master.width, img_Master.height), 8, 1)
            graySmooth = cv.CreateImage((img_Master.width, img_Master.height), 8, 1)
            #get x,y_center for line check below
            x_center = img_Master.width / 2
            y_center = img_Master.height / 2
            
            edge = cv.CreateImage((img_Master.width, img_Master.height), 8, 1)
            storage = cv.CreateMemStorage(0)
            
            cv.CvtColor(img_Master, gray, cv.CV_BGR2GRAY)
        
            
            #edges = cv.Canny(gray, 80, 120)
            cv.Smooth(gray, graySmooth)
            #3 - cvThreshold  - What values?
            cv.Threshold(graySmooth,graySmooth, 80, 255, cv.CV_THRESH_BINARY)
            cv.Canny(graySmooth, edge, 100, 150, 3)
            cv.Smooth(edge, edge)
            if self.CameraTHCanny:
                cv.ShowImage("threshold",graySmooth )
                cv.ShowImage("canny", edge)
            #lines = cv.HoughLinesP(edges, 1, math.pi/2, 2, None, 30, 1);
            lines = cv.HoughLines2(edge, storage, cv.CV_HOUGH_PROBABILISTIC, 1, pi / 180, 100, 90, 20)
        
            #work out how many line detected in image    
            i = 0
            for line in lines:
                i = i + 1
            
            #define array to hold all the line point that go through center, this case hold 10 point
            #each point have 2 element, x and y
            goodpointArray=[[0 for t in range(2)] for q in range(10)]
            goodpointDistance=[[0 for t in range(2)] for q in range(100)]
            # work out what are these line equation a b are
            # line equation as y = ax + b
            if i > 1:
                i = 0
                for line in lines:
                    x1 = float(line[0][0])
                    x2 = float(line[1][0])
                    y1 = float(line[0][1])
                    y2 = float(line[1][1])
                    if self.ConsoleDebugLine:
                        print ("x1 =" , x1)
                        print ("x2 =" , x2)
                        print ("y1 =" , y1)
                        print ("y2 =" , y2)
                    if (x1 - x2) != 0:
                        a = ((y1 - y2)/(x1 - x2))
                        b = ((y1*x2) - (x1*y2))/(x2 - x1)
                    else:
                        a = 0
                        b = x1
                    if self.ConsoleDebugLine:
                        print ("a =" , a)
                        print ("b =" , b)
                    
                    #check if line go pass screen center point by passing x of center point
                    #into line equation and check toleration of y
                    
                    #get center screen y, x_center come from image size above
                    y_center_calculated = a*x_center + b
                    y_difference  = fabs(y_center_calculated - y_center)
                    
                    if self.ConsoleDebugLineDiff:
                        print ("y_diff   = ", y_difference)
                    
                    #print ("x_center = ", x_center)
                    #print ("y_center = ", y_center)
                    
                    #if line is closed to center point then draw
                    if (y_difference < 60) and (i < 8):
                        cv.Line(img_Master, line[0], line[1], cv.CV_RGB(255, 0, 0), 3, 8)
                        goodpointArray[i][0] = line[0][0]
                        goodpointArray[i][1] = line[0][1]
                        goodpointArray[i+1][0] = line[1][0]
                        goodpointArray[i+1][1] = line[1][1]
                        i = i + 2
                    
                goodpointArray_size = i
                print ("Good line detected =",goodpointArray_size)
                #then we search the array for gap between line
                if goodpointArray_size > 3:
                    print ("Good line =",goodpointArray)
                    ListMe = self.ShortestDistance (goodpointArray[0][0],goodpointArray[0][1],goodpointArray[1][0],goodpointArray[1][1],goodpointArray[2][0],goodpointArray[2][1],goodpointArray[3][0],goodpointArray[3][1])
                    if ListMe:
                        print ("short_x1 = ",ListMe)
                        cv.Line(img_Master, (ListMe[0],ListMe[1]), (ListMe[2],ListMe[3]), cv.CV_RGB(0, 255, 0), 3, 8)
                    
                #short_x1,short_y1,short_x2,short_y2
            cv.ShowImage("camera2", img_Master)
            if cv.WaitKey(2) == 27:
                #send event to shutdown all thread
                self.event.set()
                break


        pass
    def close_program(self):
        for each_thread in self.threads:
            each_thread.stop()

# Main program where everything start
#_____________________________________________________________________________
def main():
    print "Python version = " + sys.version
    print "Opencv version = " + cv.__version__
    #print "Qt version = " + QT_VERSION_STR
    #print "Numpy version = " + np.version.version
    #print "Matplotlib version = " + matplotlib.__version__
    #print "Line profiler = " + matplotlib.__version__
    param = True
    application = App(param)
    
    try:
        #Class for camera 1 image collection:
        class myThread_1 (threading.Thread):
            def __init__(self, threadID, name, counter):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.counter = counter
            def run(self):
                print "Starting " + self.name
                application.ReadCamera_1()
            def stop(self):
                self._Thread__stop()                

        #Class for Edge scanner :
        class myThread_2 (threading.Thread):
            def __init__(self, threadID, name, counter):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.counter = counter
            def run(self):
                print "Starting " + self.name
                application.EdgeScan()
            def stop(self):
                self._Thread__stop()                

        # Create new threads
        thread1 = myThread_1(1, "Camera 1", 1)        
        thread2 = myThread_2(2, "Edge Scanner", 2)
        # Start new Threads
        thread1.start()
        thread2.start()
        # Add threads to thread list
        application.threads.append(thread1)
        application.threads.append(thread2)
        
    except:
        print "Error: unable to start thread"

    application.event.wait()
    application.close_program()

if __name__ == "__main__":
    main()