from flask import Flask, render_template, Response
import cv2
import http.server
import socketserver


class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(pageData, "utf8"))
        elif self.path.startswith('/image'):
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()

            ret, frame = cap.read()
            _, jpg = cv2.imencode(".jpg", frame)

            self.wfile.write(jpg)
        else:
            self.send_response(404)

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("Serving at port ", PORT)
    try:
        httpd.serve_forever()
    except:
        pass


app = Flask(__name__)

camera = cv2.VideoCapture("/dev/video0")  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
