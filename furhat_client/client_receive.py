import socket
import select
import time
import json
from furhat_remote_api import FurhatRemoteAPI
import google.generativeai as genai

HOST = 'localhost'
PORT = 65439

ACK_TEXT = 'text_received'

genai.configure(api_key="AIzaSyAN4EcYsU3-1rkAds7xBihH6F1zDjw9Pqo")
model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  system_instruction="""You are Bart the Bartender. It is your job to find out what 
  cocktail fits the mood of the customer. Keep the converstion short and pleasant. 
  Once the customer indicates they want the cocktail, you don't ask anymore what 
  the customer wants. In that case you say: \"Here you go!\" and   nothing more.""")


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
    done = False
    while not done:
        readySocks, _, _ = select.select(socks, [], [], 5)
        for sock in readySocks:
            message = receiveTextViaSocket(sock)
            done = furhat_recieve_text(furhat, message)
            print('received: ' + str(message))


def furhat_recieve_text(furhat, message):
    # TODO add attention to furhat using message
    message = json.loads(message)
    # attending only to the first face
    position_value = message['faces_pos'][0]
    print(position_value)
    x = position_value[0]
    x = -25
    y = position_value[1]
    y = 0
    width = position_value[2]
    height = position_value[3]
    attend_x = (str) (x)
    attend_y = (str) (y)
    # attend_x = (str) (x + (width/2))
    # attend_y = (str) (y + (height/2))
    attend_z = "1.0"
    attend_location = attend_x + "," + attend_y + "," + attend_z
    print(attend_location)
    furhat.attend(location=attend_location)
    user_input = furhat.listen()
    print("user message is: " + user_input.message)
    # TODO: fix crash if message is empty
    ai_response = model.generate_content(user_input.message)
    print("AI response is: " + ai_response.text)
    furhat.say(text=ai_response.text, blocking=True)
    if "Here you go!" in ai_response.text:
        return True
    return False
    # furhat.say(text=f"{message['no_faces']}", blocking=True)


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
