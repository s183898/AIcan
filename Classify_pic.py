import time
import numpy as np
import os
import cv2
from PIL import Image
from keras.preprocessing.image import load_img
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.models import model_from_json
import serial 
import datetime

# reduce number of messages from tensorflow 
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'

# Open model from json-file
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()

# define model and load weights
model = model_from_json(loaded_model_json)
model.load_weights("model.h5")


def capture(img_name):
    # Function to capture images using webcam
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")
    
    # The following loop takes 8 pictures, which allows the camera to adjust brightness
    ramp_frames = 8
    for i in range(ramp_frames):
        # The last frame is saved
        ret, frame = cam.read()

    # If no picture is taken, capture returns False    
    if not ret:
        print("failed to grab frame")
        return False

    # Show image:
    #cv2.imshow("test", frame)
   
    # Følgende kan bruges til at gøre billeder kvadratiske hvis nødvendigt:
    # højde, bredde, farve = frame.shape
    # forskel = bredde - højde
    # frame = frame[:, int(forskel/2):-int(forskel/2)]

    # frame = cv2.resize(frame, (512,384))
    
    # save picture and close camera
    cv2.imwrite(img_name+".png", frame)
    cam.release()
    cv2.destroyAllWindows()

    return frame
 

def deep_save(load_name, save_name):
    # This function saves a trained model (Needs load_model from keras)
    model = load_model("4classes_7833_acc")
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("model.h5")


def classify(name):
    # Load image by name
    image = load_img(name, target_size=(224, 224))
    # process image
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)

    # predict the probability for the 4 classes
    yhat = model.predict(image)[0]
    # return class with max probability
    pred = np.argmax(yhat)
    prob = max(yhat)

    return pred, prob

def CaptureClassify(name):
    capture(name)
    pred, prob = classify(name+".png")
    return pred,prob

# open serial port 
serialPort = serial.Serial(port = "COM3", baudrate=57600) 

trash_list = ["glass","metal","paper","plastic"]

# run loop until key is pressed 
try:
    while True:
        # check for message from arduino
        if(serialPort.in_waiting > 0):
            # Read data into a string and then integer
            serialString = serialPort.readline(1)
            trash_inf = serialString.decode('Ascii').strip(",")
            trash = int(trash_inf)
            # If trash has been detected
            if trash == 8:
                waiting = True
                cap = False
                trash = 0
                recent = datetime.datetime.now()
                # wait for 3 seconds
                while waiting: 
                    # Check for labels from arduino
                    if(serialPort.in_waiting > 0):
                        # read message
                        serialString = serialPort.readline(1)
                        trash_inf = serialString.decode('Ascii').strip(",")
                        label_n = int(trash_inf)
                        # if message is a label
                        if label_n in [1,2,3,4]:
                            # Capture image without classification and save with label, date and time
                            capture(trash_list[label_n-1]+"/"+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+trash_list[label_n-1])
                            waiting = False
                            cap = True

                    # check if 3 seconds has passed
                    diff = datetime.datetime.now()-recent
                    if (diff.total_seconds() >= 3):
                        waiting = False
                # if no image has been captured, capture and classify a new image
                if cap == False:
                    pred,prob = CaptureClassify("unlabeled/"+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
                    # send classification of image to arduino
                    prediction = str(pred+1)
                    serialPort.write(prediction.encode())
                    print("prediction:" ,trash_list[pred])
                    print("probability:", prob)   

        # used for debugging
        # else:
        #     print("Skipping")


except KeyboardInterrupt:
    # close serial port
    serialPort.close()

