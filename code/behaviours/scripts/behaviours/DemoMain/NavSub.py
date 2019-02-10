from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
import rospy
import math
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from alice_msgs.msg import *
import yaml
from std_msgs.msg import String
from tf.transformations import quaternion_from_euler, euler_from_quaternion


class NavSub(AbstractBehaviour):
    
    def init(self):
    	self.counter = 0
        self.flag = 0
        self.table_name = ''
        self.client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        self.client.wait_for_server()
        self.goal = MoveBaseGoal()
        self.goal.target_pose.header.frame_id = "map"
        #rospy.init_node('test_client')
        self.client2 = actionlib.SimpleActionClient('approach_objects', aliceapproachAction)
        self.client2.wait_for_server()

        print 'found server'
        with open('/home/student/sudo/ros/catkin_ws/src/behaviours/config/waypoints.yaml', 'r') as file:
            self.doc = yaml.load(file)
        self.pub = rospy.Publisher('/speech', String, queue_size = 1)
        print('done nav init')
        pass


    def update(self):
        if self.state == State.start:
            self.waypoints = self.doc[self.table_name].keys()
            self.waypoints.sort()
            print self.counter
            print self.doc[self.table_name][self.waypoints[self.counter]]
            self.goal.target_pose.header.stamp = rospy.Time.now()
            #self.goal.target_pose.pose.position.x = self.doc["waypoint1"]["x"]
	    q = quaternion_from_euler(0.0, 0.0, self.doc[self.table_name][self.waypoints[self.counter]]["angle"])
            self.goal.target_pose.pose.position.x = self.doc[self.table_name][self.waypoints[self.counter]]["x"]
            self.goal.target_pose.pose.position.y = self.doc[self.table_name][self.waypoints[self.counter]]["y"]
            self.goal.target_pose.pose.orientation.x = q[0]
	    self.goal.target_pose.pose.orientation.y = q[1]
	    self.goal.target_pose.pose.orientation.z = q[2]
	    self.goal.target_pose.pose.orientation.w = q[3]

            #self.goal.target_pose.pose.position.x = 1.0
            #self.goal.target_pose.pose.orientation.w = 1.0
            self.client.send_goal(self.goal)
            self.state = State.sub1


        elif (self.client.get_state() == actionlib.GoalStatus.SUCCEEDED  and self.state == State.sub1):
               

            if self.counter == len(self.waypoints) - 1:
                self.flag = 0
                if self.table_name != 'initial':

                    goal = aliceapproachGoal()
                    self.client2.send_goal(goal)
                    self.state = State.approach
                    self.client2.wait_for_result(rospy.Duration.from_sec(60.0)) 
                    if (self.client2.get_state() == actionlib.GoalStatus.ABORTED):  # aborted
                        print 'aborted!' 
                        print(self.table_name)
                        result = self.client2.get_result()

                    elif (self.client2.get_state() == actionlib.GoalStatus.SUCCEEDED):  # movement has succeeded
                        print 'Success final approach'
                        print(self.table_name)
                        result = self.client2.get_result()


                    elif (self.client2.get_state() != actionlib.GoalStatus.SUCCEEDED): # most likely the time-out accord
                        print(self.table_name)
                        print 'Time out' 

                    self.flag = 1

                else:
                    self.flag = 1
                    self.state = State.approach

            else:
                self.counter += 1
                self.state = State.start
        
        elif self.client.get_state() == actionlib.GoalStatus.ABORTED and self.state == State.sub1:
                self.fail('failed')

        elif self.state == State.approach and self.flag == 1:
            self.pub.publish(String('finished navigation'))
            self.finish()

             # use this for time-out checking, if takes to long stop waiting

        pass
    
    def reset(self):
        self.state = State.idle
        self.init()
