from utils.state import State
from utils.abstractBehaviour import AbstractBehaviour
import rospy
import sys
import numpy as np
from alice_msgs.msg import Order
from std_msgs.msg import String


class DemoMain(AbstractBehaviour):
	
	def init(self):
		#self.order_message = None
		self.navSub = self.get_behaviour('NavSub')
		# self.graspSub = self.get_behaviour('GraspSub')
		self.obj_graspSub = self.get_behaviour('ObjRecSub')
		self.adjustSub = self.get_behaviour('AdjustSub')
		self.obj_inc = 0
		self.final_flag = 0
		self.objects = np.array([])
		self.pub = rospy.Publisher('/speech', String, queue_size = 1)
		pass

	def update(self):

		if self.state == State.start or self.state == State.sub4:

			order_message = None
			self.obj_inc = 0
			self.final_flag = 0
			self.table2_index = 0
			self.table1_loc = []
			self.table1_obj = []
			self.table2_loc = []
			self.table2_obj = []
			self.navSub.table_name = 'initial'
			self.navSub.counter = 0
			self.navSub.start()
			self.state = State.initial

		elif self.objects.size == 0 and self.state == State.initial:
			if self.navSub.finished() :
				self.pub.publish(String('Initial location reached. Ready to receive a new order'))
				try:
					order_message = rospy.wait_for_message("order", Order, 15.0)# wait for 1 second, if nothing received it creates an exception
					print('order received')
					print(order_message)
					if order_message != None:
						self.objects = np.array(order_message.objects)
						self.locations = np.array(order_message.locations)
						for i in range(len(self.locations)):
							print(i)
							if self.locations[i].lower() == 'table1':
								self.table1_loc.append(self.locations[i])
								self.table1_obj.append(self.objects[i])
							if self.locations[i].lower() == 'table2':
								self.table2_loc.append(self.locations[i])
								self.table2_obj.append(self.objects[i])

						# self.locations_indices = np.argsort(self.locations)
						# self.table2_index = np.where(self.locations.lower() == 'table2')

		
					if len(self.table1_obj) == 0:
						print('inside if')
						self.cur_loc = self.table2_loc
						self.cur_obj = self.table2_obj
						self.cur_table = 'table2'

					else:
						print('inside else')
						self.cur_loc = self.table1_loc
						self.cur_obj = self.table1_obj
						self.cur_table = 'table1'

					
				except:
					return 

			elif self.navSub.failed():
				self.adjustSub.start()
				self.state = State.adjust

		if self.objects.size != 0 and (self.state == State.initial or self.state == State.sub3):
			# cur_in = self.locations_indices[self.obj_inc];
			#self.each_obj = self.order_message.objects[cur_in]
			#self.each_loc = self.order_message.locations[cur_in]
			self.pub.publish(String('navigating to ' + str(self.cur_table)))
			self.each_obj = self.cur_obj[self.obj_inc]
			self.each_loc = self.cur_loc[self.obj_inc]
			self.navSub.table_name = self.cur_table
			# if self.final_flag == 1:
			# 	self.navSub.table_name = 'table2.2'
			self.navSub.start()
			self.state = State.sub1
		
		elif self.state == State.sub1:
			if self.navSub.finished():
				print('started object rec and grasp '+str(self.obj_inc)+ ' '+'from table '+str(self.cur_table))
				self.obj_graspSub.goal.req = self.each_obj
				self.obj_graspSub.start()
				self.state = State.sub2
				
			elif self.navSub.failed():
				self.adjustSub.start()
				self.state = State.adjust

		elif self.state == State.adjust:
			if self.adjustSub.finished():
				if self.objects.size != 0:
					self.state = State.sub3
				else:
					self.state = State.sub4
		
		elif self.state == State.sub2:
			if self.obj_graspSub.finished():
				self.pub.publish(String('object recognition and grasping finished at ' + str(self.cur_table)))
				self.state = State.sub3
				self.obj_inc = self.obj_inc + 1

		if self.state == State.sub3:
			if self.obj_inc >= len(self.cur_obj):
				if self.navSub.table_name == 'table1':
					self.obj_inc = 0
					self.cur_obj = self.table2_obj
					self.cur_loc = self.table2_loc
					self.cur_table = 'table2'
					if self.table2_obj.size == 0:
						self.objects = np.array([])
						self.state = State.sub4
					self.navSub.counter = 0

				elif self.navSub.table_name == 'table2':
					self.obj_inc = 0
					self.cur_obj = self.table2_obj
					self.cur_loc = self.table2_loc
					self.cur_table = 'table2.2'
					self.navSub.counter = 0

				else:
					self.objects = np.array([])
					self.state = State.sub4

		pass
