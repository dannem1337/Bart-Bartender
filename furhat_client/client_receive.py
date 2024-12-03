import socket
import select
import time
import json
from furhat_remote_api import FurhatRemoteAPI

HOST = 'localhost'
PORT = 65439

ACK_TEXT = 'text_received'


def main():
    # instantiate a socket object
    furhat = FurhatRemoteAPI("localhost")
    # Get the voices on the robot
    voices = furhat.get_voices()

    # Set the voice of the robot
    furhat.set_voice(name='Matthew')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('socket instantiated')

    # connect the socket
    connectionSuccessful = False
    while not connectionSuccessful:
        try:
            sock.connect((HOST, PORT))    # Note: if execution gets here before the server starts up, this line will cause an error, hence the try-except
            print('socket connected')
            connectionSuccessful = True
        except:
            pass

    socks = [sock]
    while True:
        readySocks, _, _ = select.select(socks, [], [], 5)
        for sock in readySocks:
            message = receiveTextViaSocket(sock)
            furhat.say(text=f"{message['no_faces']}", blockd=True)
            print('received: ' + str(message))


def furhat_recieve_text(furhat, message):
    message = json.loads(message)
    result = furhat.listen()


def receiveTextViaSocket(sock):
    # get the text via the scoket
    encodedMessage = sock.recv(1024)

    # if we didn't get anything, log an error and bail
    if not encodedMessage:
        print('error: encodedMessage was received as None')
        return None
    # end if

    # decode the received text message
    message = encodedMessage.decode('utf-8')

    # now time to send the acknowledgement
    # encode the acknowledgement text
    encodedAckText = bytes(ACK_TEXT, 'utf-8')
    # send the encoded acknowledgement text
    sock.sendall(encodedAckText)

    return message
# end function

if __name__ == '__main__':
    main()
