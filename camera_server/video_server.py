import socket
import select
import time
import cv2
import pandas as pd
import feat
import json
import warnings
import joblib


HOST = 'localhost'
PORT = 65439

ACK_TEXT = 'text_received'
warnings.filterwarnings("ignore", module="feat")


def main():
    # instantiate a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('socket instantiated')

    # bind the socket
    sock.bind((HOST, PORT))
    print('socket binded')

    # start the socket listening
    sock.listen()
    print('socket now listening')

    # accept the socket response from the client, and get the connection object
    conn, addr = sock.accept()      # Note: execution waits here until the client calls sock.connect()
    print('socket accepted, got connection object')
    capture = cv2.VideoCapture(0)

    with open("rf_model.pkl", "rb") as f:
        model = joblib.load(f)

    detector = feat.Detector(device="cpu")


    while True:
        try: 
            ret, frame = capture.read() 
            message = detectFaces(frame, detector, model)
            json_message = json.dumps(message)
            print('sending: ' + json_message)
            sendTextViaSocket(json_message, conn)
        except:
            sock.shutdown(socket.SHUT_RDWR)

def detectFaces(frame, detector, model):
    detected_faces = detector.detect_faces(frame)
    detected_landmarks = detector.detect_landmarks(frame, detected_faces)
    detected_aus = detector.detect_aus(frame, detected_landmarks)

    emotions = predictEmotion(detected_aus[0], model)
    print(emotions)
    int_face = []
    face = detected_faces[0]
    for f in face:
        # v = x,y,width,height
        int_face.append([int(round(v)) for v in f])
    message = {
        "faces_pos": int_face, 
        "emotions": emotions,
        "no_faces": len(face) 
    }
    return message

def predictEmotion(au_values, model):
    emotion = []
    columns = ['AU01', 'AU02', 'AU04', 'AU05', 'AU06', 'AU07', 'AU09', 'AU10', 
           'AU11', 'AU12', 'AU14', 'AU15', 'AU17', 'AU20', 'AU23', 'AU24', 'AU25', 
           'AU26', 'AU28', 'AU43']
    for au in au_values:
        print(au)
        df = pd.DataFrame([au], columns=columns)
        emotion.append(model.predict(df)[0]) 
    return emotion 
        

def sendTextViaSocket(message, sock):
    # encode the text message
    encodedMessage = bytes(message, 'utf-8')

    # send the data via the socket to the server
    sock.sendall(encodedMessage)

    # receive acknowledgment from the server
    encodedAckText = sock.recv(1024)
    ackText = encodedAckText.decode('utf-8')

    # log if acknowledgment was successful
    if ackText == ACK_TEXT:
        print('server acknowledged reception of text')
    else:
        print('error: server has sent back ' + ackText)

if __name__ == '__main__':
    main()
