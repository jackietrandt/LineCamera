'''
Created on 15/03/2013

@author: Alice

'''
import cv2.cv as cv
import time
import sys
from math import sin, cos, sqrt, pi, fabs
import wx 
import os



#function to find shortest distance between 2 line
#provide 2 point of each line
#find out what is the 2 closest point 
#which each belong to a separated line
def ShortestDistance(x1,y1,x2,y2,x3,y3,x4,y4):
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

class SliderFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Slider Example', size=(300, 350))
        panel = wx.Panel(self, -1)
        self.count = 0
        slider = wx.Slider(panel, 100, 25, 1, 100, pos=(10, 10),
                size=(250, -1),
                style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        slider.SetTickFreq(5, 1)
        slider2 = wx.Slider(panel, 100, 25, 1, 100, pos=(10, 50),
                size=(250, -1),
                style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        slider2.SetTickFreq(20, 1)
        
        
app = wx.PySimpleApp()
frame = SliderFrame()
frame.Show()


cv.NamedWindow("canny", 1)
cv.NamedWindow("threshold", 1)
cv.NamedWindow("camera2", 1)

#capture = cv.CaptureFromCAM(0)
capture2 = cv.CaptureFromCAM(0)

ModeTest = True

if ModeTest:
    cv.SetCaptureProperty(capture2, cv.CV_CAP_PROP_FRAME_HEIGHT, 640)
    cv.SetCaptureProperty(capture2, cv.CV_CAP_PROP_FRAME_WIDTH, 320)
else:
    cv.SetCaptureProperty(capture2, cv.CV_CAP_PROP_FRAME_HEIGHT, 1080)
    cv.SetCaptureProperty(capture2, cv.CV_CAP_PROP_FRAME_WIDTH, 1920)
    
while True:
    #img = cv.QueryFrame(capture)
    img2 = cv.QueryFrame(capture2)
    #cv.ShowImage("camera", img)

    # convert to grayscale
    gray = cv.CreateImage((img2.width, img2.height), 8, 1)
    graySmooth = cv.CreateImage((img2.width, img2.height), 8, 1)
    #get x,y_center for line check below
    x_center = img2.width / 2
    y_center = img2.height / 2
    
    edge = cv.CreateImage((img2.width, img2.height), 8, 1)
    storage = cv.CreateMemStorage(0)
    
    cv.CvtColor(img2, gray, cv.CV_BGR2GRAY)

    
    #edges = cv.Canny(gray, 80, 120)
    cv.Smooth(gray, graySmooth)
    #3 - cvThreshold  - What values?
    cv.Threshold(graySmooth,graySmooth, 80, 255, cv.CV_THRESH_BINARY)
    cv.Canny(graySmooth, edge, 100, 150, 3)
    cv.Smooth(edge, edge)
    cv.ShowImage("threshold",graySmooth )
    if ModeTest:
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
            #print ("x1 =" , x1)
            #print ("x2 =" , x2)
            #print ("y1 =" , y1)
            #print ("y2 =" , y2)
            if (x1 - x2) != 0:
                a = ((y1 - y2)/(x1 - x2))
                b = ((y1*x2) - (x1*y2))/(x2 - x1)
            #print ("a =" , a)
            #print ("b =" , b)
            
            #check if line go pass screen center point by passing x of center point
            #into line equation and check toleration of y
            
            #get center screen y, x_center come from image size above
            y_center_calculated = a*x_center + b
            y_difference  = fabs(y_center_calculated - y_center)
            
            print ("y_diff   = ", y_difference)
            
            #print ("x_center = ", x_center)
            #print ("y_center = ", y_center)
            
            #if line is closed to center point then draw
            if (y_difference < 60) and (i < 8):
                cv.Line(img2, line[0], line[1], cv.CV_RGB(255, 0, 0), 3, 8)
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
            ListMe = ShortestDistance (goodpointArray[0][0],goodpointArray[0][1],goodpointArray[1][0],goodpointArray[1][1],goodpointArray[2][0],goodpointArray[2][1],goodpointArray[3][0],goodpointArray[3][1])
            if ListMe:
                print ("short_x1 = ",ListMe)
                cv.Line(img2, (ListMe[0],ListMe[1]), (ListMe[2],ListMe[3]), cv.CV_RGB(0, 255, 0), 3, 8)
            
        #short_x1,short_y1,short_x2,short_y2
    cv.ShowImage("camera2", img2)
    if cv.WaitKey(2) == 27:
        break
