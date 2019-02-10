import rospy
import actionlib
import random
import numpy as np
from alice_msgs.msg import ObjRecAction, ObjRecResult, ObjectROIAction, ObjectROIGoal
from network import Network
import exampleMobilenetCall 
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import tensorflow as tf

class ActionServer(object):

    def __init__(self):
        self.CHECKPOINT_DIR = "./ckpt/network.ckpt"
        self.network = Network()
        self.network.load_checkpoint(self.CHECKPOINT_DIR)
        self.image_crop = ''
        self.state = ''
        self.out_label = []
        self.action_server = actionlib.SimpleActionServer("net_server",ObjRecAction,execute_cb=self.callback,auto_start = False)
        self.action_server.start()
        self.client = actionlib.SimpleActionClient("get_objects", ObjectROIAction)
        self.client.wait_for_server()
        goal = ObjectROIGoal()
        self.cv_bridge = CvBridge()
        goal.action = "roi"
        image_msg = rospy.wait_for_message("front_xtion/rgb/image_raw", Image)
        self.image = self.cv_bridge.imgmsg_to_cv2(image_msg, desired_encoding="bgr8")
        self.image_height, self.image_width, _ = self.image.shape
        self.client.send_goal(goal) 



    def callback(self, goal):
       
        if self.client.get_state() == actionlib.GoalStatus.PENDING or self.client.get_state() == actionlib.GoalStatus.LOST:
            image_msg = rospy.wait_for_message("front_xtion/rgb/image_raw", Image)
            self.image = self.cv_bridge.imgmsg_to_cv2(image_msg, desired_encoding="bgr8")
            self.image_height, self.image_width, _ = self.image.shape
            goal = ObjectROIGoal()
            goal.action = "roi"
            self.client.send_goal(goal)

        elif self.client.get_state() == actionlib.GoalStatus.SUCCEEDED or self.client.get_state() == actionlib.GoalStatus.ABORTED:
            
            roi_result = self.client.get_result()
            rois = roi_result.roi
            for roi in rois:
                # print roi.left, roi.right, roi.top, roi.bottom
                # print roi.x, roi.y, roi.z
                padding = 10
                left = roi.left - padding if roi.left - padding > 0 else 0
                right= roi.right + padding if roi.right + padding < self.image_width else self.image_width
                top = roi.top - padding if roi.top - padding > 0 else 0
                bottom = roi.bottom + padding if roi.bottom + padding < self.image_height else self.image_height
                # top_dec = (top-bottom) % 32
                # left_dec = (left-right) % 32
                # top = top - top_dec
                # left = left - left_dec
                self.image_crop = self.image[top:bottom,left:right]

                self.image_crop = cv2.resize(self.image_crop,(32, 32))

                # print self.image_crop
                print exampleMobilenetCall.main(self.image_crop)

                self.out_label.append(self.network.feed_batch([self.image_crop]))           

            result = ObjRecResult()
            print self.out_label
            result.value = self.out_label;
            self.action_server.set_succeeded(result)

if __name__ == "__main__":
    rospy.init_node("net_server_node")
    server = ActionServer()
    rospy.spin()
