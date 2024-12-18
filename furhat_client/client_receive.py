import socket
import select
import time
import json
from furhat_remote_api import FurhatRemoteAPI
import google.generativeai as genai
import asyncio
from dotenv import load_dotenv
import os
load_dotenv(".env")


HOST = 'localhost'
PORT = 65439

ACK_TEXT = 'text_received'

genai.configure(api_key=os.getenv("API_KEY"))
model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  system_instruction="""You are Bart the Bartender. It is your job to find out what 
  cocktail fits the mood of the customer. Keep the converstion short and pleasant. 
  Once the customer indicates they want the cocktail, you don't ask anymore what 
  the customer wants. In that case you say: \"Here you go!\" and   nothing more.""")

async def listen_and_process(furhat, chat, message_queue):
    message_data = None
    collected_messages = {
        "angry": 0,
        "neutral": 0,
        "happy": 0,
        "surprise": 0,
        "fear": 0,
        "disgust": 0,
        "sad": 0
    }
    while True:
        # Spin on while if there is no costumer there
        result = None
        while result is None or result.message == '' or message_data is None:
            print("in while")
            while not message_queue.empty():
                message_data = await message_queue.get()
                collected_messages[message_data['emotions'][0]] += 1
                print(f"Processed message data: {message_data}")

            if result is None or result.message == '':
                result = await asyncio.to_thread(furhat.listen)
                print(f"Listening result: {result}")


        while True:
            print(collected_messages)
            prompt = "Now answer keeping in mind that i am"
            # Only considering 1 person
            if message_data['no_faces'] == 0: continue
            current_emotion = max(collected_messages, key= lambda x: collected_messages[x])
            match current_emotion:
                case "angry":
                    prompt += "angry\n"
                case "neutral":
                    prompt += "neutral\n"
                case "happy":
                    prompt += "happy\n"
                case "suprised":
                    prompt += "suprised\n"
                case "fear":
                    prompt += "concerned\n"
                case "disgust":
                    prompt += "disgusted\n"
                case "sad":
                    prompt += "sad\n"
            print("user message is: " + result.message)
            ai_response = chat.send_message(prompt + result.message)
            print("AI response is: " + ai_response.text)
            furhat.say(text=ai_response.text, blocking = True)
            if "Here you go!" in ai_response.text:
                # Reset, new person incoming
                collected_messages = {
                    "angry": 0,
                    "neutral": 0,
                    "happy": 0,
                    "surprise": 0,
                    "fear": 0,
                    "disgust": 0,
                    "sad": 0
                }
                while not message_queue.empty():
                    message_data = await message_queue.get()
                print("we are done")
                break;
            result = await asyncio.to_thread(furhat.listen)


async def handle_socket(sock, message_queue):
    """Asynchronously handle socket messages."""
    reader, writer = await asyncio.open_connection(sock=sock)
    while True:
        message = await reader.read(1024)
        if not message:
            print('Socket connection closed')
            break

        # Decode and process message
        decoded_message = message.decode('utf-8')
        # print(f"Received from socket: {decoded_message}")

        # load to dictionary
        # message_data = json.loads(decoded_message)
        try:
            message_data = json.loads(decoded_message)
            # Send message to the queue for processing
            if message_data['no_faces'] != 0: 
                await message_queue.put(message_data)
        except json.JSONDecodeError:
            print("Failed to decode JSON message")




        # Send acknowledgment
        writer.write(ACK_TEXT.encode('utf-8'))
        await writer.drain()

async def main():
    furhat = FurhatRemoteAPI("localhost")
    furhat.set_voice(name='Matthew')
    print('Furhat API initialized')
    chat = model.start_chat()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket instantiated')

    # Connect the socket, retry if we didnot succeed
    while True:
        try:
            sock.connect((HOST, PORT))
            print('Socket connected')
            break
        except ConnectionRefusedError:
            await asyncio.sleep(1)  

    message_queue = asyncio.Queue()
    # Run tasks concurrently
    await asyncio.gather(
        handle_socket(sock, message_queue),
        listen_and_process(furhat, chat, message_queue)
    )

if __name__ == '__main__':
    asyncio.run(main())
