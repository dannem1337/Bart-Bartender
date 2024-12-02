import socket
import select
import time
import cv2
import feat
import json
import warnings

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
    detector = feat.Detector(device="cpu")

    while True:
        try: 
            ret, frame = capture.read() 
            message = detectFaces(frame, detector)
            json_message = json.dumps(message)
            print('sending: ' + json_message)
            sendTextViaSocket(json_message, conn)
            time.sleep(1)
        except:
            sock.shutdown(socket.SHUT_RDWR)

def detectFaces(frame, detector):
    detected_faces = detector.detect_faces(frame)
    detected_landmarks = detector.detect_landmarks(frame, detected_faces)
    detected_aus = detector.detect_aus(frame, detected_landmarks)
    # Since we only are looking at one image
    face = detected_faces[0]
    aus = detected_aus[0]
    message = {
        # "faces_pos": face, TODO: why can they be floats?
        # "aus": aus,
        "no_faces": len(face)
    }
    print(message)
    return message
        

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
    # end if
# end function

if __name__ == '__main__':
    main()