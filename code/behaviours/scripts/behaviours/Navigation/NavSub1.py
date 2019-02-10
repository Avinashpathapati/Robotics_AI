from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import yaml

class NavSub1(AbstractBehaviour):
    
    def init(self):
        self.counter = 0
        self.client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        self.client.wait_for_server()
        self.goal = MoveBaseGoal()
        self.goal.target_pose.header.frame_id = "map"
        with open('/home/student/sudo/ros/catkin_ws/src/behaviours/config/waypoints.yaml', 'r') as file:
            self.doc = yaml.load(file)
            self.waypoints = self.doc.keys()
            self.waypoints.sort()
        
    def update(self):
        print self.counter
        print self.doc[self.waypoints[self.counter]]
        if self.state == State.start:
            self.goal.target_pose.header.stamp = rospy.Time.now()
            #self.goal.target_pose.pose.position.x = self.doc["waypoint1"]["x"]
            self.goal.target_pose.pose.position.x = self.doc[self.waypoints[self.counter]]["x"]
            self.goal.target_pose.pose.position.y = self.doc[self.waypoints[self.counter]]["y"]
            self.goal.target_pose.pose.orientation.w = self.doc[self.waypoints[self.counter]]["angle"]
            #self.goal.target_pose.pose.position.x = 1.0
            #self.goal.target_pose.pose.orientation.w = 1.0
            self.client.send_goal(self.goal)
            self.state = State.sub1


        elif (self.client.get_state() == actionlib.GoalStatus.SUCCEEDED or self.client.get_state() == actionlib.GoalStatus.ABORTED) and self.state == State.sub1:
            if self.counter == len(self.waypoints) - 1:
                self.finish()
            else:
                self.counter += 1
                self.state = State.start


            
    def reset(self):
        self.state = State.idle
        self.init()
