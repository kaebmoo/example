import time
from flask import Flask, render_template, Response
from flask_sse import sse
from flask_cors import CORS 

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://127.0.0.1"
app.register_blueprint(sse, url_prefix='/stream')
CORS(app) 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress')
def progress():
    def generate():
        with app.app_context():
            for i in range(101):
                data = {"progress": i}
                sse.publish(data, type='progress')  # ตรวจสอบว่า type='progress'
                # print(f"Published event: {data}")  # เพิ่ม print statement เพื่อดูข้อมูลที่ถูกส่ง
                time.sleep(0.05)
                if i == 100:
                    sse.publish({"progress": "complete"}, type='progress')


    response = Response(generate(), mimetype='text/event-stream')
    return response


@app.route('/dummy')
def simple_stream():
    pass

if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False, port=9000)