from flask import Flask, render_template, Response, request
import cv2
import face_recognition
import pickle
import os
import eventlet
import eventlet.wsgi

app = Flask(__name__)

if os.path.exists("registered_faces.pkl"):
    with open("registered_faces.pkl", "rb") as f:
        registered_faces = pickle.load(f)
else:
    registered_faces = {}

temp_face_encoding = None
video_source = 1
capture = cv2.VideoCapture(video_source)

def generate_frames():
    global temp_face_encoding
    while True:
        ret, frame = capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            match = None
            for name, info in registered_faces.items():
                matches = face_recognition.compare_faces([info['encoding']], face_encoding, tolerance=0.5)
                if matches[0]:
                    match = name
                    break

            top, right, bottom, left = face_location
            if match:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, match, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "New Face", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                temp_face_encoding = face_encoding

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/register', methods=['POST'])
def register():
    global temp_face_encoding
    name = request.form.get('name')
    if name and temp_face_encoding is not None:
        registered_faces[name] = {
            "encoding": temp_face_encoding
        }
        with open("registered_faces.pkl", "wb") as f:
            pickle.dump(registered_faces, f)
        temp_face_encoding = None
        return "Face registered"
    return "No face to register", 400

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
