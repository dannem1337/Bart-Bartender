from furhat_remote_api import FurhatRemoteAPI
import time
import google.generativeai as genai

genai.configure(api_key="AIzaSyDVzqHc8FxpPiyGFXe9jkdiiSqa8U5iuQ0")
model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  system_instruction="""You are Bart the Bartender. It is your job to find out what 
  cocktail fits the mood of the one that is talking to you. You do this by asking
  considerate but short questions. Questions should be less than 2 sentences. After
  3 questions you should suggest a cocktail that fits the mood of the user. Once
  you suggest a cocktail, you should stop asking questions""")

furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name='Matthew')

furhat.attend(user="CLOSEST")


# use something like this for the conversation
furhat.say(text="Hello, what can I do for you today?", async_req=True)
furhat.gesture(name="Surprise")
time.sleep(1)

while True:
    user_input = furhat.listen()
    print(user_input.message)
    ai_response = model.generate_content(user_input.message)
    print(ai_response.text)
    furhat.say(text=ai_response.text, blocking=True)
    # Should call this function constantly. It just attends to the closest user in this
    # moment and keeps following that person, even though a different user comes closer later
    furhat.attend(user='CLOSEST')