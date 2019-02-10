from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
import rospy
import actionlib
from alice_msgs.msg import *

class ObjRecSub(AbstractBehaviour):
    
    def init(self):
    	self.client = actionlib.SimpleActionClient("net_server",ObjRecAction)
    	self.client.wait_for_server()
    	print 'connected to server'
    	self.goal = ObjRecGoal()
    	# self.goal.req="roi"
        pass

    def update(self):
    	if self.state == State.start:
            self.client.send_goal(self.goal)
            self.state = State.obj_grasp
    	elif (self.client.get_state() == actionlib.GoalStatus.SUCCEEDED or self.client.get_state() == actionlib.GoalStatus.ABORTED) and self.state == State.obj_grasp:
    		self.result = self.client.get_result()
    		# print self.result.value
    		self.finish()
        pass
    
    def reset(self):
        self.state = State.idle
        self.init()
