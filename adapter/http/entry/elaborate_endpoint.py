from flask import request, jsonify, Blueprint

from adapter.http.entry.request.elaborate_response import ElaborateResponse
from business.elaborate_business import ElaborateBusiness

elaborate_endpoint = Blueprint('elaborate_endpoint', __name__)


@elaborate_endpoint.route('/elaborate', methods=['GET'])
async def get_elaborate():
    try:
        elaborate_business = ElaborateBusiness()
        subject = request.args.get('subject')
        result = await elaborate_business.make_elaborate(subject)

        return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@elaborate_endpoint.route('/elaborate/<string:id>', methods=['POST'])
async def check_elaborate(id):
    try:
        check_result = None
        elaborate_business = ElaborateBusiness()
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file:
            check_result = await elaborate_business.check_elaborate(file, id)

        return ElaborateResponse.success(check_result.dict())
    except Exception as e:
        return ElaborateResponse.error(str(e))

@elaborate_endpoint.route('/health', methods=['GET'])
def health_check():
    try:
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

