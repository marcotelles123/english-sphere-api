from flask import Flask, request, g
from adapter.http.entry.question_endpoint import question_endpoint
from adapter.http.entry.elaborate_endpoint import elaborate_endpoint
from flask_cors import CORS
import uuid

app = Flask(__name__)

def generate_correlation_id():
    return str(uuid.uuid4())

def get_correlation_id():
    return request.headers.get('X-Correlation-ID')

@app.before_request
def add_correlation_id():
    correlation_id = request.headers.get('X-Correlation-ID')
    if not correlation_id:
        correlation_id = generate_correlation_id()
    g.correlation_id = correlation_id


CORS(app)
app.register_blueprint(question_endpoint)
app.register_blueprint(elaborate_endpoint)

if __name__ == '__main__':
    app.run(debug=True, port=5003)