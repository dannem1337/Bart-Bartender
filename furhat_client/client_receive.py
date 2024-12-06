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

async def listen_and_process(furhat):
    while True:
        # Start listening asynchronously
        result = await asyncio.to_thread(furhat.listen)
        if result.message != '':
            print("user message is: " + result.message)
            ai_response = model.generate_content(result.message)
            print("AI response is: " + ai_response.text)
            furhat.say(text=ai_response.text)

            ## Maybe here we just wait for the next customer?
            # if "Here you go!" in ai_response.text:
            #     return True
            # return False

        print(f"Furhat listened and got: {result}")

async def handle_socket(sock, furhat):
    """Asynchronously handle socket messages."""
    reader, writer = await asyncio.open_connection(sock=sock)
    while True:
        message = await reader.read(1024)
        if not message:
            print('Socket connection closed')
            break

        # Decode and process message
        decoded_message = message.decode('utf-8')
        print(f"Received from socket: {decoded_message}")

        # load to dictionary
        # message_data = json.loads(decoded_message)


        # Send acknowledgment
        writer.write(ACK_TEXT.encode('utf-8'))
        await writer.drain()

async def main():
    furhat = FurhatRemoteAPI("localhost")
    furhat.set_voice(name='Matthew')
    print('Furhat API initialized')

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

    # Run tasks concurrently
    await asyncio.gather(
        handle_socket(sock, furhat),
        listen_and_process(furhat)
    )

if __name__ == '__main__':
    asyncio.run(main())
