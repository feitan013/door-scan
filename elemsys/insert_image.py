import cv2
import mysql.connector

# Load pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open a connection to the camera (0 represents the default camera)
cap = cv2.VideoCapture(0)

# Connect to the MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="elemsys"
)

# Create a cursor object to interact with the database
cursor = db_connection.cursor()

# Create a table to store face information (if it doesn't exist)
create_table_query = """
CREATE TABLE IF NOT EXISTS faces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image BLOB NOT NULL
)
"""
cursor.execute(create_table_query)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Draw rectangles around the detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Extract and save the face to the database
        face_image = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        _, face_image_encoded = cv2.imencode('.jpg', face_image)
        face_image_blob = face_image_encoded.tobytes()

        name = input("Enter the name of the person: ")

        # Insert face information into the database
        insert_query = "INSERT INTO faces (name, image) VALUES (%s, %s)"
        cursor.execute(insert_query, (name, face_image_blob))
        db_connection.commit()

        print("Face registered and saved to the database.")

    # Display the resulting frame
    cv2.imshow('Face Registration', frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera, close the database connection, and close the window
cap.release()
cv2.destroyAllWindows()
cursor.close()
db_connection.close()
