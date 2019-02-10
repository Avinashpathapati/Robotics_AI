from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
from alice_msgs.msg import ObjRecAction, ObjRecResult, ObjRecGoal
import actionlib
import rospy


class RunNetwork(AbstractBehaviour):
    
    def init(self):
    	self.client = actionlib.SimpleActionClient("net_server",ObjRecAction)
    	self.client.wait_for_server()
    	print 'connected to server'
    	self.goal = ObjRecGoal()
    	self.goal.req="roi"
        pass

    def update(self):
    	if self.state == State.start:
            self.client.send_goal(self.goal)
            self.state = State.sub1
    	elif (self.client.get_state() == actionlib.GoalStatus.SUCCEEDED or self.client.get_state() == actionlib.GoalStatus.ABORTED) and self.state == State.sub1:
    		result = self.client.get_result()
    		print result.value
    		self.finish()
        pass
    
    def reset(self):
        self.state = State.idle
        self.init()
