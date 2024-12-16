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
    while True:
        message_data = None
        while not message_queue.empty():
            message_data = await message_queue.get()
        
        print(f"Message received for processing: {message_data}")

        # Start listening asynchronously
        result = await asyncio.to_thread(furhat.listen)
        if (result.message != '') and (message_data != None):
            prompt = ""
            print("\n\nTAKING EMOTIONS\n\n")
            match message_data['emotions'][0]:
                case "angry":
                    prompt = "TODO\n"
                case "neutral":
                    prompt = "TODO\n"
                case "happy":
                    prompt = "TODO\n"
                case "suprised":
                    prompt = "TODO\n"
                case "fear":
                    prompt = "TODO\n"
                case "disgust":
                    prompt = "TODO\n"
                case "sad":
                    prompt = "TODO\n"
            print("user message is: " + result.message)
            ai_response = chat.send_message(prompt + result.message)
            print("AI response is: " + ai_response.text)
            furhat.say(text=ai_response.text)

            ## Maybe here we just wait for the next customer?
            # if "Here you go!" in ai_response.text:
            #     return True
            # return False

        print(f"Furhat listened and got: {result}")

async def handle_socket(sock, furhat, message_queue):
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
        handle_socket(sock, furhat, message_queue),
        listen_and_process(furhat, chat, message_queue)
    )

if __name__ == '__main__':
    asyncio.run(main())
