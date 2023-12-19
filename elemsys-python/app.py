from flask import Flask, render_template, Response
import cv2
import serial
import time
from io import BytesIO
import base64

app = Flask(__name__)

# Load the pre-trained face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the reference face image
reference_image_path = "C:/xampp/htdocs/elemsys/image/zy.jpg"
reference_image = cv2.imread(reference_image_path)

# Check if the image is loaded successfully
if reference_image is None:
    print(f"Error: Unable to load reference image at path {reference_image_path}")
    exit()

reference_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

# Open a connection to the Arduino
arduino = serial.Serial('COM1', 9600)  # Change 'COM3' to the appropriate port

def generate_frames():
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use face_cascade.detectMultiScale() to detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Extract the face region
            face_roi = gray[y:y+h, x:x+w]

            # Resize the face_roi to match the size of the reference_gray
            face_roi_resized = cv2.resize(face_roi, (reference_gray.shape[1], reference_gray.shape[0]))

            # Compare the face with the reference face using simple pixel-based comparison
            difference = cv2.absdiff(reference_gray, face_roi_resized)
            mean_difference = cv2.mean(difference)[0]

            # Set a threshold for the difference (you may need to adjust this)
            threshold = 50

            # Display "Access Granted" or "Access Denied" based on the result
            if mean_difference < threshold:
                cv2.putText(frame, "Access Granted", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                # Send signal to Arduino for servo to turn to 180 degrees
                arduino.write(b'180\n')
            else:
                cv2.putText(frame, "Access Denied", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                # Send signal to Arduino for servo to turn to 45 degrees
                arduino.write(b'60\n')

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
