# Bart-Bartender

## Setup furhat and run code
To run the python code on the furhat, first boot up Furhat Studio and click the button "Start remote API"

After this you should run `video_server.py` and `client_receiver.py` using the normal python commands. In the terminal, this would be:
```
python camera_server/video_server.py
python furhat_client/client_receive.py 
```

To make the Furhat follow the closest virtual user, open the web interface (https://localhost:8080) and go to the 'wizard' tab. There you can add virtual users by double clicking the picture with the Furhat.