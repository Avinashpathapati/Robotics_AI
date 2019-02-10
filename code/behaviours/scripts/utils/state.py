from enum import Enum, unique

@unique
class State(Enum):
    idle = 0
    start = 1
    
    sub1 = 4
    sub2 = 5
    sub3 = 6
    sub4 = 7
    sub5 = 8
    obj_grasp = 9
    initial = 10
    approach = 11
    adjust = 12
    finished = 2
    failed = 3