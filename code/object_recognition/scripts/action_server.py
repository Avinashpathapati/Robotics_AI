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
from std_msgs.msg import String
import datetime

def CallbackRGBImage(data):
	pass

def CallbackPointCloud(data):
	pass

def CallbackDepthImage(data):
	pass

class ActionServer(object):

	

	def __init__(self):
		print('started obj rec action server init')
		self.box_size_dict =  { 4:[ 0.215, 0.05,0.095],3:[0.13,0.07,0.075],2:[ 0.155,0.05, 0.055],1:[ 0.1,0.03, 0.13],0:[ 0.16,0.045, 0.17]}
		self.box_labels = {0:"BaseTech" , 1:"TomatoSoup", 2:"EraserBox", 3:"USBHub", 4:"Evergreen"}
		self.CHECKPOINT_DIR = "./ckpt/network.ckpt"

		self.image_save_path = './Recog_Objects/'
		self.image_crop = ''
		self.state = ''
		self.out_label = []
		#rospy.init_node("grasp_testing")
		# Run subscribers to that the rgb image exposure doesn't cause problems 
		rospy.Subscriber("front_xtion/rgb/image_raw", Image, CallbackRGBImage)
		rospy.Subscriber("front_xtion/depth/image_raw", Image, CallbackDepthImage)
		rospy.Subscriber("front_xtion/depth/points", PointCloud2, CallbackPointCloud)
		time.sleep(2)

		move_head = rospy.ServiceProxy("move_head", MoveHead)
		clear_octomap = rospy.ServiceProxy("clear_octomap", Empty)

		# Set the head into 
		move_head_req = MoveHeadRequest()
		move_head_req.pitch = 0.7
		move_head_req.yaw = 0.0
		move_head(move_head_req)
		self.network = Network()
		self.network.load_checkpoint(self.CHECKPOINT_DIR)
		print "start loading model"
		self.graph = tf.Graph()
		with self.graph.as_default():
			self.sess = tf.Session()
			with self.sess.as_default():
				self.model = load_model("/home/student/sudo/ros/catkin_ws/src/DATA/model.h5")

		rospy.sleep(2)
		clear_octomap() 
		## Reseting the Octomap because we moved before
		self.alice_object = AliceObject() # Class for interfacing with alice_object node
		self.moveit = MoveIt() # Class for interfacing with MoveIt (Needs to be implemented!)

		# For deleting the model from Gazebo (Pretending we dropped in a bin on Alice)
		delete_model = rospy.ServiceProxy("gazebo/delete_model", DeleteModel)
		# you can change the cropping in GetObjectInformation function
		#self.all_object_data = alice_object.GetObjectInformation() # Gather RGB and Depth cropping data and x,y,z information

		
		self.zero_image = np.zeros((28,28))
		self.one_image = np.ones((28,28))
		#rospy.sleep(10)
		self.pub = rospy.Publisher('/speech', String, queue_size = 1)
		print('finished obj rec action server init')
		self.temp = []

		self.action_server = actionlib.SimpleActionServer("net_server",ObjRecAction,execute_cb=self.callback,auto_start = False)

		self.action_server.start()

	# Function for delete the model from Gazebo, e.g. "box1"
	def DeleteModelName(name):
		delete_model(name)


	def callback(self, goal):
		self.all_object_data = self.alice_object.GetObjectInformation()
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
				
				#with tf.Graph().as_default():
				with self.graph.as_default():
					with self.sess.as_default():
						prediction = self.model.predict(image_depth)[0][0]
				prediction *= pi

				print "Deg: ", degrees(prediction)

				if np.array_equal(self.zero_image, image_depth) or np.array_equal(self.one_image,image_depth):
					print 'zero image'
					# uncomment to show binary depth image
					#cv2.imshow("binary depth image" , image_depth[0])
				else:            
					#uncomment to show binary depth image
					#cv2.imshow("binary depth image", image_depth[0])
					pass
					
				image_depth = image_depth.reshape(1, 28, 28, 1)
				predictions.append(prediction)
								
				image_color = np.resize(image_color,(32, 32, 3))
				class_prob = self.network.feed_batch([image_color])
				class_index = np.argmax(class_prob)
				print(class_prob)
				print(class_index)
				print(self.box_labels[class_index])
				name = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ' ' + str(self.box_labels[class_index]) + ' ' + str(round(class_prob[0][class_index], 2))
				
				#uncomment to show images
				#cv2.imshow("color image", image_color[0])
				#cv2.waitKey(0)    
				cv2.imwrite(self.image_save_path+name+".jpg", image_color)
				print "With orientation:", str(degrees(np.mean(predictions)))
				print "Box class:", self.box_labels[class_index]
				self.pub.publish(String('I found ' + str(self.box_labels[class_index])))
				print self.box_size_dict[class_index]
				if goal.req.lower() == self.box_labels[class_index].lower():
					self.moveit.grasp(x,y,z,degrees(np.mean(predictions)), self.box_size_dict[class_index])
					self.pub.publish(String('Grasping the ' + str(self.box_labels[class_index])))
					self.temp.append(str(self.box_labels[class_index]))
		
		for i in range(len(self.temp)):
			self.pub.publish(String('I collected ' + self.temp[i]))
		
		result = ObjRecResult()
		result.value = [10]		
		self.action_server.set_succeeded(result)

if __name__ == "__main__":
	rospy.init_node("net_server")
	server = ActionServer()
	rospy.spin()
