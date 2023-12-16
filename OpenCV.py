import cv2

def detect_face():
    # Load the pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Open a connection to the webcam (usually 0 or 1, depending on your setup)
    cap = cv2.VideoCapture(0)

    #Adding a flag variable to set the value when face is detected
    isFaceDetected = False

    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()

        # Convert the frame to grayscale (face detection works better in grayscale)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            #Display the message FACE IS DETECTED
            cv2.putText(frame, 'Face Detected!', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2, cv2.LINE_AA)

            #Face detected
            isFaceDetected = True

        # Display the resulting frame
        cv2.imshow('Face Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q') or isFaceDetected:
            break

    # Release the webcam and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

    return isFaceDetected

if __name__ == "__main__":
    result = detect_face()
    print("Face Detected :", result)
