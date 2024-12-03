from furhat_remote_api import FurhatRemoteAPI
import time
import google.generativeai as genai

genai.configure(api_key="AIzaSyDVzqHc8FxpPiyGFXe9jkdiiSqa8U5iuQ0")
model = genai.GenerativeModel("gemini-1.5-flash")

furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name='Matthew')

furhat.attend(user="CLOSEST")


# use something like this for the conversation
furhat.say(text="Whoa there!", async_req=True)
furhat.gesture(name="Surprise")
time.sleep(1)

while True:
    user_input_async = furhat.furhat_listen_get(async_req=True)
    user_input = user_input_async.get()
    ai_Response = model.generate_content(user_input)
    furhat.say(text=ai_Response.text)
    time.sleep(1)
    # Should call this function constantly. It just attends to the closest user in this
    # moment and keeps following that person, even though a different user comes closer later
    furhat.attend(user='CLOSEST')