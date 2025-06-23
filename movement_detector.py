import cv2
import numpy as np
import streamlit as st
import tempfile


# ------------------ Hareket Algılama Sınıfı ------------------ #
class CameraTranslationDetect:
    def __init__(self, threshold=2.0):
        self.threshold = threshold

    def detect_phase_shift(self, prev_frame, curr_frame):
        prev_gray = np.float32(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
        curr_gray = np.float32(cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY))
        shift, _ = cv2.phaseCorrelate(prev_gray, curr_gray)
        return shift


# ------------------ Video İşleme Fonksiyonu ------------------ #
def process_video(video_path, detector):
    cap = cv2.VideoCapture(video_path)
    prev_frame = None
    frame_count = 0
    detected_frames = []
    st_frame = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

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


# ------------------ Streamlit Arayüzü ------------------ #
st.title("📹 Kamera Hareketi Tespit Sistemi")
st.write("📁 Video yükleyerek ya da 📷 webcam ile kamera hareketlerini tespit edebilirsin.")

option = st.radio("Kullanım Türü Seç:", ["📁 Video Yükle", "📷 Webcam (tek kare)"])

# --- Video Yükleme Seçeneği --- #
if option == "📁 Video Yükle":
    uploaded_video = st.file_uploader("Video Yükle (.mp4, .avi)", type=["mp4", "avi"])
    if uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())

        detector = CameraTranslationDetect(threshold=2.0)
        st.write("🔍 Analiz ediliyor...")

        with st.spinner("Video işleniyor, lütfen bekleyin..."):
            result_frames = process_video(tfile.name, detector)

        st.success("✅ İşlem tamamlandı.")
        st.write(f"🚨 Kamera hareketi tespit edilen kareler: {result_frames}")

# --- Webcam Kullanımı (tek kare) --- #
elif option == "📷 Webcam (tek kare)":
    st.info("Webcam ile iki fotoğraf çekin, sistem aradaki hareketi analiz etsin.")

    img1 = st.camera_input("1. Görüntü (Başlangıç)")
    img2 = st.camera_input("2. Görüntü (Sonraki)")

    if img1 and img2:
        file_bytes1 = np.asarray(bytearray(img1.read()), dtype=np.uint8)
        file_bytes2 = np.asarray(bytearray(img2.read()), dtype=np.uint8)
        frame1 = cv2.imdecode(file_bytes1, 1)
        frame2 = cv2.imdecode(file_bytes2, 1)

        detector = CameraTranslationDetect(threshold=2.0)
        shift_x, shift_y = detector.detect_phase_shift(frame1, frame2)

        movement_detected = abs(shift_x) >= detector.threshold or abs(shift_y) >= detector.threshold

        st.image(frame1, caption="Başlangıç Görüntüsü", channels="BGR")
        st.image(frame2, caption="Sonraki Görüntü", channels="BGR")

        if movement_detected:
            st.error(f"🚨 Kamera hareketi algılandı! Δx={shift_x:.2f}, Δy={shift_y:.2f}")
        else:
            st.success(f"✅ Kamera sabit. Δx={shift_x:.2f}, Δy={shift_y:.2f}")
