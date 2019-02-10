from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
import rospy


class Navigation(AbstractBehaviour):
    
    def init(self):
    	self.sub1 = self.get_behaviour('NavSub1')
        pass

    def update(self):
    	if self.state == State.start:
    		self.sub1.start()
    		self.state = State.sub1
    	elif self.state == State.sub1:
    		if self.sub1.finished():
    			self.finish()

        pass
