from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
import rospy


class GraspSub(AbstractBehaviour):
    
    def init(self):
        pass

    def update(self):
        pass
    
    def reset(self):
        self.state = State.idle
        self.init()
