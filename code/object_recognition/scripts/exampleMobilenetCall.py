import cv2
import tensorflow as tf
import numpy as np

### If you place this file in the provided 'inception' folder, it should work after you ran 'run.sh' on your data.
### ~happy hacking~
 

## This function will load a trained network file (probably called output_graph.pb in ./tmp/)
## It will return a tf session, which should be stored as a member variable (in your class). I use it globally here as an example.
def loadNetwork(pb_file_location): 
    f = tf.gfile.FastGFile(pb_file_location, 'rb')
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')
    #Qprint graph_def
    return tf.Session()
    
## This will read the label file, and return a list of labels, in the same index order the output layer reasons in.
def read_labels(label_file):
    with open(label_file) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content  
    


## This function will process one image such that it is usable by Mobilenet.
def preprocess(img): #input is a numpy image
    ## First we'll resize the image such that the network can process it. Possible imagesizes are: 
    ## '224', '192', '160', or '128' (See retrain.py line 84 comments)
    ## By default, 'run.sh' uses the 224 network. You may choose anotherone, by changing the 224 part in 'run.sh' to another valid size.
    img = cv2.resize(img,(224, 224))
    img = img.astype(float) / 255   ##goto [0.0,1.0] instead of [0,255]
    img = np.reshape(img, (1, 224, 224, 3))
    return img
    
## This function will run 
def run_inference_on_image(image_data):
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0') ## resolve layer from .pb file
    predictions = sess.run(softmax_tensor, {'input:0' : image_data}) ## Run network on your input
    predictions = np.squeeze(predictions)                            ## make sure output dims are correct
#    print predictions
    norm = predictions / np.sqrt(predictions.dot(predictions))       ## normalize output data (make softmax out of it)
    print "out: ", norm, " label = ", np.argmax(norm)                ## print result
    return norm, np.argmax(norm)

def main(image_data):
    img = preprocess(image_data)
    out, labIdx = run_inference_on_image(img)
    return labels[labIdx]


labels = read_labels("./inception/tmp/output_labels.txt")
sess = loadNetwork("./inception/tmp/output_graph.pb")

# if __name__ == "__main__":
    
#     img = cv2.imread("1.jpg")
#     labels = read_labels("./tmp/output_labels.txt")
#     sess = loadNetwork("./tmp/output_graph.pb")
#     img = preprocess(img)
#     out, labIdx = run_inference_on_image(img)
#     print "It's ", labels[labIdx], "!"

