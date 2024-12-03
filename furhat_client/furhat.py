from furhat_remote_api import FurhatRemoteAPI
import time

furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name='Matthew')

furhat.attend(user="CLOSEST")


# use something like this for the conversation
furhat.say(text="Whoa there!", async_req=True)
furhat.gesture(name="Surprise")
time.sleep(1)
result = furhat.furhat_listen_get(async_req=True)

while True:
    time.sleep(1)
    # Should call this function constantly. It just attends to the closest user in this
    # moment and keeps following that person, even though a different user comes closer later
    furhat.attend(user='CLOSEST')