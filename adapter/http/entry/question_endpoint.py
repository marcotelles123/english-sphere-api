from flask import request, jsonify, Blueprint

from adapter.http.entry.request.question_response import QuestionResponse
from business.question_business import QuestionBusiness

question_endpoint = Blueprint('question_endpoint', __name__)


@question_endpoint.route('/question', methods=['GET'])
async def get_question():
    try:
        question_business = QuestionBusiness()
        subject = request.args.get('subject')
        result = await question_business.make_question(subject)

        return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@question_endpoint.route('/question/<string:id>', methods=['POST'])
async def check_question(id):
    try:
        check_result = None
        question_business = QuestionBusiness()
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file:
            check_result = await question_business.check_question(file, id)

        return QuestionResponse.success(check_result.dict())
    except Exception as e:
        return QuestionResponse.error(str(e))

@question_endpoint.route('/health', methods=['GET'])
def health_check():
    try:
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

