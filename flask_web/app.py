from flask import Flask, request

app = Flask(__name__)

@app.route('/api/setBeacons', methods=['POST'])
def set_beacons():
    data = request.json
    print(data)
    return "Data received", 200

if __name__ == '__main__':
    app.run(debug=True, port=80)
