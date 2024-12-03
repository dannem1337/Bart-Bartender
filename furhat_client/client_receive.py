import socket
import select
import time
import json
from furhat_remote_api import FurhatRemoteAPI
import google.generativeai as genai

HOST = 'localhost'
PORT = 65439

ACK_TEXT = 'text_received'

genai.configure(api_key="Your API key")
model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  system_instruction="""You are Bart the Bartender. It is your job to find out what 
  cocktail fits the mood of the one that is talking to you. You do this by asking
  considerate but short questions. Questions should be less than 2 sentences. After
  3 questions you should suggest a cocktail that fits the mood of the user. Once
  you suggest a cocktail, you should stop asking questions""")


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

    furhat.say(text="Hello, what can I do for you today?")
    socks = [sock]
    while True:
        readySocks, _, _ = select.select(socks, [], [], 5)
        for sock in readySocks:
            message = receiveTextViaSocket(sock)
            furhat_recieve_text(furhat, message)
            print('received: ' + str(message))


def furhat_recieve_text(furhat, message):
    message = json.loads(message)
    user_input = furhat.listen()
    print("user message is:" + user_input.message)
    ai_response = model.generate_content(user_input.message)
    print(ai_response.text)
    furhat.say(text=ai_response.text, blocking=True)
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
