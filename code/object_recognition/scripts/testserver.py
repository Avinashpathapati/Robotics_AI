import rospy
import actionlib
import random
import numpy as np
from alice_msgs.msg import ObjRecAction, ObjRecResult, ObjectROIAction, ObjectROIGoal
from network import Network

from cv_bridge import CvBridge, CvBridgeError
import cv2
import tensorflow as tf
from keras.models import load_model
from alice_object import AliceObject
from moveit import MoveIt
from math import pi, degrees
from sensor_msgs.msg import Image, PointCloud2
from gazebo_msgs.srv import DeleteModel
from alice_msgs.srv import MoveHead
from alice_msgs.srv._MoveHead import MoveHeadRequest
from std_srvs.srv import Empty
import time
import os


def CallbackRGBImage(data):
    pass

def CallbackPointCloud(data):
    pass

def CallbackDepthImage(data):
    pass

class ActionServer(object):

    

    def __init__(self):
        print('started obj rec action server init')

        self.CHECKPOINT_DIR = "./ckpt/network.ckpt"


        self.network = Network()
        self.network.load_checkpoint(self.CHECKPOINT_DIR)
        
        self.action_server = actionlib.SimpleActionServer("net_server",ObjRecAction,execute_cb=self.callback,auto_start = False)
        #rospy.init_node("grasp_testing")

        # Run subscribers to that the rgb image exposure doesn't cause problems 
        rospy.Subscriber("front_xtion/rgb/image_raw", Image, CallbackRGBImage)
        rospy.Subscriber("front_xtion/depth/image_raw", Image, CallbackDepthImage)
        rospy.Subscriber("front_xtion/depth/points", PointCloud2, CallbackPointCloud)
        time.sleep(2)



    
        print "start loading model"
        self.model = load_model(os.environ["HOME"] + "/DATA/model.h5")
        self.graph = tf.get_default_graph()
        self.model._make_predict_function()   
     
        ## Reseting the Octomap because we moved before
        self.alice_object = AliceObject() # Class for interfacing with alice_object node



        self.action_server.start()

   


    def callback(self, goal):
        self.all_object_data = self.alice_object.GetObjectInformation()
        print('allll object')
        # print(self.all_object_data)
        for objects in self.all_object_data:
            print "object"
            x = 0
            y = 0
            z = 0
            z_min = 0
            z_max = 0

            predictions = []
            classifications = []
            for object in objects:
                print "processing images"
                image_color, image_depth, x, y, z, z_min, z_max = object

                print 'Image:', image_depth
                image_depth = np.asarray(image_depth)   
                image_depth = self.alice_object.CreateBinaryImage(image_depth)        
                image_depth = image_depth.reshape(1, 28, 28, 1)
                
                with self.graph.as_default():
                    prediction = self.model.predict(image_depth)[0][0]
                prediction *= pi

                print "Deg: ", degrees(prediction)

              
                predictions.append(prediction)
                
                
                image_color = cv2.resize(image_color,(32, 32))
                class_index = self.network.feed_batch([image_color])[0]
                
                #uncomment to show images
                #cv2.imshow("color image", image_color[0])
                #cv2.waitKey(0)    
                    
                print "With orientation:", str(degrees(np.mean(predictions)))
                print "Box class:", class_index

        result = ObjRecResult()
        result.value = [10]
        self.action_server.set_succeeded(result)

if __name__ == "__main__":
    rospy.init_node("net_server_test")
    server = ActionServer()
    rospy.spin()
