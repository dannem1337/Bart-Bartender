import cv2
import opencv_jupyter_ui as jcv2
from feat import Detector
from IPython.display import Image
from furhat_remote_api import FurhatRemoteAPI

# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("localhost")
# Get the voices on the robot
voices = furhat.get_voices()
# Set the voice of the robot
furhat.set_voice(name='Matthew')
# Say "Hi there!"
furhat.say(text="Hi there!")
# Listen to user speech and return ASR result



from feat.utils import FEAT_EMOTION_COLUMNS



detector = Detector(device="cpu")

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while True:
    ret, frame = cam.read()
    if not ret:
        print("OpenCV found an error reading the next frame.")
        break

    faces = detector.detect_faces(frame)
    landmarks = detector.detect_landmarks(frame, faces)
    emotions = detector.detect_emotions(frame, faces, landmarks)

    # The functions seem to assume a collection of images or frames. We acces "frame 0".
    faces = faces[0]
    landmarks = landmarks[0]
    emotions = emotions[0]

    strongest_emotion = emotions.argmax(axis=1)

    for (face, top_emo) in zip(faces, strongest_emotion):
        (x0, y0, x1, y1, p) = face
        cv2.rectangle(frame, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 3)
        cv2.putText(frame, FEAT_EMOTION_COLUMNS[top_emo], (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0), 2)

    jcv2.imshow("Emotion Detection", frame)

    key = jcv2.waitKey(1) & 0xFF
    if key == 27: # ESC pressed
        break

cam.release()
jcv2.destroyAllWindows()

print(FEAT_EMOTION_COLUMNS[top_emo])
