from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/python/health', methods=['GET'])
def health():
    return jsonify({"status": "Python service is running"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)