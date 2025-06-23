import cv2
import numpy as np
import imutils
from imutils.video import VideoStream
from imutils.video import FPS
import time
import streamlit as st
import tempfile


if st.button("you want to you webcam"):
    
    class CameraTranslationDetect(object):
        """
        Class for calculating translational shift betwen two frames
        """
        version = '2019.0.1'
    
        def __init__(self):
            """initializer method"""
            print('Hello, world.')
        
        def detect_phase_shift(self, prev_frame, curr_frame):
            """opencv cv2 - returns detected sub-pixel phase-shift between two frames"""
            prev_frame = np.float32(cv2.cvtColor(prev_frame, 
                                             cv2.COLOR_BGR2GRAY))    # convert to required type
            curr_frame = np.float32(cv2.cvtColor(curr_frame, 
                                             cv2.COLOR_BGR2GRAY))    
            shift = cv2.phaseCorrelate(prev_frame, curr_frame)      #calculate phase-correlation between current and previous frame

            return shift
    
   
      
        
        
# ***    ***    ***     Implementation      ***     ***     ***


    vs = VideoStream(src=0).start()    # initialize the video stream
    time.sleep(2.0)    # allow camera to warm up
    fps = FPS().start()    # initialize the FPS counter

    n=0    # incrementer

    threshold = 2    # detection sensitivity value

    center = 200-50, 200   #define point for logging camera-state to screen

    obj = CameraTranslationDetect()    # instantiate CameraTranslationDetect object and pass in reference frame

#mainloop
    while True:
        frame = vs.read()    # read frame from video stream
        frame = imutils.resize(frame, width=400)    # resize output window

        if n == 0:    # check if first frame
            initial = frame.copy()    # store first frame 
            prev = frame.copy()
            n=n+1
     
        (shift_x, shift_y), sf = obj.detect_phase_shift(prev, frame)    # pass subsequent frame into class method, returns translational shift
    
        if shift_x >= threshold or shift_x <= -threshold or shift_y >= threshold or shift_y <= -threshold:    # check detected shift against threshold
            ts = time.time()    #get current time for logging detected motion
            readable = time.ctime(ts)    # convert timestamp to readable format
        
            print("camera movement detected @ " +    #print timestamp and x, y translation when motion detected
                str(readable) + ' x: ' + 
                str(shift_x) + ' y: ' + 
                str(shift_y))     

            cv2.putText(    #update screen
                frame,    #numpy array on which text is written
                    "Motion Detected", #text
                    center, #position at which writing has to start
                    cv2.FONT_HERSHEY_SIMPLEX, #font family
                    0.8, #font size
                    (0, 0, 255, 0), #font color
                    2) #font stroke
        else:
            cv2.putText(frame, "Position Stable", 
                    center, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0, 0), 2) 

        cv2.imshow("Frame", frame)    #display output
    
        key = cv2.waitKey(75) & 0xFF
        if key == ord("q"):    # if the `q` key was pressed, break from the loop
            break
 
        fps.update()    # update the FPS counter
    
    #reset shift
        shift_x = None  
        shift_y = None
        sf = None
        prev = frame.copy()

# stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()


class CameraTranslationDetect:
    def __init__(self, threshold=2.0):
        self.threshold = threshold

    def detect_phase_shift(self, prev_frame, curr_frame):
        prev_gray = np.float32(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
        curr_gray = np.float32(cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY))
        shift, _ = cv2.phaseCorrelate(prev_gray, curr_gray)
        return shift


def process_video(video_path, detector):
    cap = cv2.VideoCapture(video_path)
    prev_frame = None
    frame_count = 0
    detected_frames = []

    st_frame = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break
        frame = imutils.resize(frame, width=400)
        frame = cv2.resize(frame, (400, int(frame.shape[0] * 400 / frame.shape[1])))

        if prev_frame is None:
            prev_frame = frame.copy()
            continue

        shift_x, shift_y = detector.detect_phase_shift(prev_frame, frame)
        movement_detected = abs(shift_x) >= detector.threshold or abs(shift_y) >= detector.threshold

        if movement_detected:
            cv2.putText(frame, "Motion Detected", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            detected_frames.append(frame_count)
        else:
            cv2.putText(frame, "Position Stable", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        st_frame.image(frame, channels="BGR")
        prev_frame = frame.copy()
        frame_count += 1
    cap.release()
    return detected_frames
       
st.title("📹 Kamera Hareketi Tespit Sistemi")
st.write("Bir video yükleyin ve önemli kamera hareketlerinin hangi karelerde olduğunu görün.")

uploaded_video = st.file_uploader("Video Yükle (.mp4, .avi)", type=["mp4", "avi"])

if uploaded_video is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())

    detector = CameraTranslationDetect(threshold=2.0)
    st.write("Analiz ediliyor...")

    with st.spinner("Video işleniyor, lütfen bekleyin..."):
        result_frames = process_video(tfile.name, detector)

    st.success("İşlem tamamlandı.")
    st.write(f"🚨 Kamera hareketi tespit edilen kareler: {result_frames}") 
           
