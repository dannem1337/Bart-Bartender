from furhat_remote_api import FurhatRemoteAPI
import time

furhat = FurhatRemoteAPI("localhost")
furhat.set_voice(name='Matthew')

thread = furhat.attend(location="0.0,0.0,1.0", async_req=True)

furhat.say(text="Whoa there!", async_req=True)
furhat.gesture(name="Surprise")
