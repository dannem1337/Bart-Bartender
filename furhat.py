from furhat_remote_api import FurhatRemoteAPI
import time

####### TODOs ######
# make furhat follow a face (or multiple)
# Connect furhat to LLM
# Tune the LLM to be a bartender -> include a list of cocktails/ingredients to choose from
####################

furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name='Matthew')

thread = furhat.attend(location="0.0,0.0,1.0", async_req=True)

furhat.say(text="Whoa there!", async_req=True)
furhat.gesture(name="Surprise")
time.sleep(1)
result = furhat.furhat_listen_get(async_req=True)
