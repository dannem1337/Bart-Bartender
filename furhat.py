from furhat_remote_api import FurhatRemoteAPI
import time

####### TODOs ######
# make furhat follow a face (or multiple)
# Connect furhat to LLM
# Tune the LLM to be a bartender -> include a list of cocktails/ingredients to choose from
####################

furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name='Matthew')



# Should call this function constantly. It just attends to the closest user in this
# moment and keeps following that person, even though a different user comes closer later
furhat.attend(user="CLOSEST")


# use something like this for the conversation
furhat.say(text="Whoa there!", async_req=True)
furhat.gesture(name="Surprise")
time.sleep(1)
result = furhat.furhat_listen_get(async_req=True)

while True:
    time.sleep(1)
    furhat.attend(user='CLOSEST')