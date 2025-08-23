import cv2
from deepface import DeepFace

# Load OpenCV Haarcascade face detector
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Start webcam
web_cam = cv2.VideoCapture(0)

while True:
    ret, frame = web_cam.read()
    if not ret:
        continue  # skip if frame not captured

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # this is for quick face detection (originally trained in grayscale)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        face_roi = frame[y:y + h, x:x + w]

    try:
        # Analyze the frame with DeepFace (emotion)
        result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
        emotion = result[0]['dominant_emotion']

        # Display text on frame
        text = f"Emotion: {emotion}"
        cv2.putText(frame, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    except Exception as e:
        print("Error:", e)

    # Show the frame
    cv2.imshow("Real-time Face Analysis", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

web_cam.release()
cv2.destroyAllWindows()
