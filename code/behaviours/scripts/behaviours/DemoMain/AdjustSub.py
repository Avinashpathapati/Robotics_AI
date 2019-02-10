from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
import rospy
import actionlib
from alice_msgs.msg import *

class AdjustSub(AbstractBehaviour):
    
    def init(self):
        self.client = actionlib.SimpleActionClient('alicecontroller', alicecontrollerfunctionAction)
        self.client.wait_for_server()
        pass

    def update(self):
    	if self.state == State.start:
    		goal = alicecontrollerfunctionGoal()
        	goal.function = "move"
        	goal.meter = -0.4
        	self.client.send_goal(goal)
        	self.state = State.adjust
        	self.client.wait_for_result()

        elif self.state == State.adjust and (self.client.get_state() == actionlib.GoalStatus.SUCCEEDED or self.client.get_state() == actionlib.GoalStatus.ABORTED):
        	self.finish()
        pass
    
    def reset(self):
        self.state = State.idle
        self.init()
