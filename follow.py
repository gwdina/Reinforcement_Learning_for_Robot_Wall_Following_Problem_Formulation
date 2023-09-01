#!/usr/bin/python3

import rospy
import cmath
import string
import time
from std_srvs.srv import Empty
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


# 1(medium), 0(close), 2 (far)

state = [0,0,0]
scanData = None

def callback(data):
     global scanData
     scanData = data.ranges


def getState():
    global state
    global scanData
    state = ["0","0","0"]

     #front
    Fsum = 0 
    for i in range(80,101):
        Fsum += scanData[i]
        #print(scanData[i])
        

    Favg = Fsum/20

    if (Favg > .5):
        state[0] = '2'
    else:
        state[0] = '0'

    #Angle
    Asum = 0 
    for i in range(40,71):
        Asum += scanData[i]
        #print(scanData[i])

    Aavg = Asum/30

    if (Aavg > .5):
        state[1] = '2'
    elif ((Aavg < 0.5) and (Aavg > .4)):
        state[1] = '1'
    else:
        state[1] = '0' 

    #Right
    Rsum = 0 
    for i in range(0,36):
        Rsum  += scanData[i]
        #print(scanData[i])

    Ravg = Rsum/30

    if (Ravg > .5):
        state[2] = '2'
    elif ((Ravg < 0.5) and (Ravg > .4)):
        state[2] = '1'
    else:
        state[2] = '0' 
    
    state="".join(state)

rospy.init_node('laser_scan_publisher')
scan_subscriber = rospy.Subscriber('/scan', LaserScan, callback)
rate = rospy.Rate(2)

velocity_publisher = rospy.Publisher('/triton_lidar/vel_cmd', Twist, queue_size=10)
vel_msg = Twist()

#rospy.wait_for_service('/gazebo/reset_world')
reset_world = rospy.ServiceProxy('/gazebo/reset_world', Empty)
#reset_world()

 # 0 = close, 2 = far, 1 = medium 
#forward, right foward, left foward 
table = {
    "222": [1,0,0], 
    "221": [1,0,0], 
    "220": [1,0,0], ######
    "212": [1,0,0], 
    "211": [1,0,0], 
    "210": [0,1,0], ######
    "202": [1,0,0], 
    "201": [0,1,0], #
    "200": [0,1,0],####
    "022": [0,0,1],#
    "021": [0,0,1],#
    "020": [0,0,1],###### wall
    "012": [0,0,1],#
    "011": [0,0,1],#
    "010": [0,0,1], ######## wall
    "002": [0,0,1], 
    "001": [0,0,1], 
    "000": [0,0,1]  ######## wall sometimes
}




while scanData is None:    
    pass

reset_world()

while not rospy.is_shutdown():
    vel_msg.linear.z = 0
    vel_msg.linear.y = 0
    vel_msg.angular.z = 0
    velocity_publisher.publish(vel_msg)

    getState()
    
    # one to move foward, one to move foward and left, and one to move foward and right
    # foward
    if (table[state][0]==1):
     print("Foward"+state)
     vel_msg.linear.y = .25
     vel_msg.angular.z = 0
     vel_msg.linear.z = 0
     velocity_publisher.publish(vel_msg)
    
     

    #foward right
    if (table[state][1]==1):
     print("right"+state)
     vel_msg.linear.y = 0.25
     vel_msg.angular.z = -0.25
     vel_msg.linear.z = 0
     velocity_publisher.publish(vel_msg)



    #foward left
    if (table[state][2]==1):
     print("left"+state)
     vel_msg.linear.y = 0.25
     vel_msg.angular.z = 0.25
     vel_msg.linear.z = 0
     velocity_publisher.publish(vel_msg)

    rate.sleep()


    