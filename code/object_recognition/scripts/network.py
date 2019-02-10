import tensorflow as tf
import numpy as np
import cv2

class Network:
  def __init__(self):
    self.inputWidth = 32
    self.inputHeight = 32
    self.inputChannels = 3
    self.nLabels = 5
    self.learningRate = 0.002
    config = tf.ConfigProto(device_count={'GPU': 0})
    config.gpu_options.allow_growth=True
    self.sess = tf.InteractiveSession(config = config)
    self.build()
    self.saver = tf.train.Saver()

    
  def weight_variable(self, shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

  def bias_variable(self, shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

  def conv2d(self, x, W, padding = 'SAME'):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

  def max_pool_2x2(self, x, padding = 'SAME'):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding=padding)

  def store_checkpoint(self, ckpt):
      self.saver.save(self.sess, ckpt)
  def load_checkpoint(self, ckpt):
      self.saver.restore(self.sess, ckpt)

  def build(self):
    
    #with tf.device('/gpu:0'):
    self.x = tf.placeholder(tf.float32, shape=[None, self.inputHeight, self.inputWidth, self.inputChannels])
    self.target_output = tf.placeholder(tf.float32, shape=[None, self.nLabels])

    image = tf.reshape(self.x, [-1, self.inputWidth, self.inputHeight, self.inputChannels])

    with tf.name_scope('conv1'):
      W_conv1 = self.weight_variable([8 , 8 ,3, 32])
      b_conv1 = self.bias_variable([32])
      h_conv1 = tf.nn.relu(self.conv2d(image, W_conv1) + b_conv1)

    with tf.name_scope('pool1'):
      h_pool1 = self.max_pool_2x2(h_conv1)

  # Second convolutional layer -- maps 32 feature maps to 64.
    with tf.name_scope('conv2'):
      W_conv2 = self.weight_variable([5 , 5 , 32, 64])
      b_conv2 = self.bias_variable([64])
      h_conv2 = tf.nn.relu(self.conv2d(h_pool1, W_conv2) + b_conv2)

    # Second pooling layer.
    with tf.name_scope('pool2'):
      h_pool2 = self.max_pool_2x2(h_conv2)

    # Fully connected layer 1 -- after 2 round of dow nsampling, our 28x28 image
    # is down to 7x7x64 feature maps -- maps this to 1024 features.
    with tf.name_scope('fc1'):
      W_fc1 = self.weight_variable([8 * 8 * 64, 1024])
      b_fc1 = self.bias_variable([1024])

      h_pool2_flat = tf.reshape(h_pool2, [-1, 8*8*64])
      h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    
    with tf.name_scope('fc2'):
      W_fc2 = self.weight_variable([1024, 5])
      b_fc2 = self.bias_variable([5])

      y_conv = tf.matmul(h_fc1, W_fc2) + b_fc2
    with tf.name_scope('loss'):
      cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels = self.target_output, logits = y_conv, name="mean_cross_entropy"))

    with tf.name_scope('GradientDescentOptimizer'):
      self.train_step = tf.train.GradientDescentOptimizer(self.learningRate).minimize(cross_entropy)

    with tf.name_scope('accuracy'):
      self.predict = tf.nn.softmax(y_conv)
      correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(self.target_output, 1), name= "correct")
      correct_prediction = tf.cast(correct_prediction, tf.float32)
      self.accuracy = tf.reduce_mean(correct_prediction)
      self.summary = tf.summary.merge_all()

    self.variables = tf.global_variables_initializer()
    self.sess.run(self.variables)
    # with tf.name_scope('fully_connected'):

    #   input_flattened = tf.reshape(self.x, [-1, self.inputWidth * self.inputHeight * self.inputChannels])

    #   weights_1 = self.weight_variable([self.inputWidth * self.inputHeight * self.inputChannels, self.nLabels])
    #   biases_1 = self.bias_variable([self.nLabels])
      
    #   self.linear_out = tf.matmul(input_flattened, weights_1) + biases_1
    #   self.softmax_out = tf.nn.softmax(self.linear_out)
      
    # cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels = self.target_output, logits = self.linear_out), name="mean_cross_entropy")
    # #self.train_step = tf.train.AdamOptimizer(self.learningRate).minimize(cross_entropy)
    # self.train_step = tf.train.GradientDescentOptimizer(self.learningRate).minimize(cross_entropy)

    
    # self.correct_prediction = tf.equal(tf.argmax(self.softmax_out,1), tf.argmax(self.target_output,1), name = "correct")
    # self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32), name = "accuracy")
    
    # self.summary = tf.summary.merge_all()
    # self.variables = tf.global_variables_initializer()
    # print self.sess.run(self.variables)
    
    # self.training_summary = tf.summary.scalar("training accuracy", self.accuracy)
    # self.loss_summary = tf.summary.scalar("loss", cross_entropy)
    # self.merged = tf.summary.merge_all()
    # self.summary_writer = tf.summary.FileWriter("./tensorboard/", self.sess.graph)
  
  def train_batch(self, data, labels):
    self.train_step.run(feed_dict = {self.x: data, self.target_output: labels})
  
  def test_batch(self, data, labels):
    return self.accuracy.eval(feed_dict = {self.x: data, self.target_output: labels})
    
  
  def feed_batch(self, data):
    #image = tf.reshape(data, [-1, self.inputWidth, self.inputHeight, self.inputChannels])
    #image = np.reshape(data,[-1,self.inputWidth, self.inputHeight, self.inputChannels])
    out = self.predict.eval(session= self.sess, feed_dict = {self.x: data})
    return out

  
  def predict_label(self, image_data):
    cv2.imshow("Image crop", image_data)
    # cv2.waitKey(0);
    softmax_tensor = self.sess.graph.get_tensor_by_name('final_result:0') ## resolve layer from .pb file
    predictions = self.sess.run(softmax_tensor, {'input:0' : image_data}) ## Run network on your input
    predictions = np.squeeze(predictions)                            ## make sure output dims are correct
    print predictions
    norm = predictions / np.sqrt(predictions.dot(predictions))       ## normalize output data (make softmax out of it)
    print "out: ", norm, " label = ", np.argmax(norm)                ## print result
    return norm, np.argmax(norm)

 
if __name__ == "__main__":
  network = Network()
