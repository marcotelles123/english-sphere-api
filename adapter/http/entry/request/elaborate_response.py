from flask import jsonify

class ElaborateResponse:
    @staticmethod
    def success(data):
        return jsonify({"status": "success", "data": data}), 200

    @staticmethod
    def error(message, status_code=500):
        return jsonify({"status": "error", "message": message}), status_code