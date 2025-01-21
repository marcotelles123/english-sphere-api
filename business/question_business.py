import logging
import json
from bson import ObjectId
import traceback
from werkzeug.datastructures import FileStorage

from adapter.db.db_client_mongo import DbClientMongo
from adapter.http.out.llm_gateway_client import LlmGatewayClient
from adapter.http.out.sound_to_text_client import SoundToTextClient
from adapter.log.log_config import LoggerSingleton
from domain.exceptions.NotFoundException import NotFoundException
from domain.common.check_result import CheckResult
from domain.question.question import Question


class QuestionBusiness:
    def __init__(self):
        self.llm_gateway_client = LlmGatewayClient()
        self.sound_to_text_client = SoundToTextClient()
        self.mongo_client = DbClientMongo()

    async def make_question(self, subject: str):
        try:
            LoggerSingleton().log_info(
                f"Starting make_question, creating prompt, subject={subject}"
            )
            system_prompt, user_prompt = self._create_prompt_make_question(subject)
            LoggerSingleton().log_info("Calling IA...")
            result = self.llm_gateway_client.chat_completion(system_prompt, user_prompt)
            id = await self._save_result(
                subject, result, LoggerSingleton().get_logger()
            )

            LoggerSingleton().log_info(f"Returning result: {result}")

            return {"id": id, "question": result}
        except Exception as e:
            LoggerSingleton().log_error(f"Error: {e}\nStacktrace:\n{traceback.format_exc()}")
            raise e

    async def _save_result(
        self, subject: str, question: str, logger: logging.Logger
    ) -> str:
        logger.info(f"Saving question, subject={subject}, question={question}. ")

        try:
            data = {"subject": subject, "result": question, "first": True }
            result = await self.mongo_client.insert_question(data)
            logger.info(f"Question saved successfully for subject: {subject}")

            return str(result)
        except Exception as e:
            LoggerSingleton().log_error(f"Error: {e}\nStacktrace:\n{traceback.format_exc()}")
            raise e

    async def check_question(self, file: FileStorage, question_id: str):
        try:
            LoggerSingleton().log_info(
                f"Starting check_question, finding question {question_id}"
            )

            result_mongo = await self.mongo_client.find_questions(
                {"_id": ObjectId(question_id)}
            )

            question = result_mongo[0]["result"]
            subject = result_mongo[0]["subject"]
            if question is None:
                raise NotFoundException("question", question_id)

            LoggerSingleton().log_info(f"Converting to text")
            response = self.sound_to_text_client.extract_text(file)

            answer = json.loads(response.content.decode("utf-8").strip())["message"]

            system_prompt, user_prompt = self._create_prompt_check_question(question, answer)

            LoggerSingleton().log_info(
                f"Calling LLM question {question}, answer {answer}"
            )
            check_result = self.llm_gateway_client.chat_completion(system_prompt, user_prompt)

            answer = json.loads(response.content.decode("utf-8").strip())["message"]
            result_message = json.loads(check_result)["message"]
            question_message = json.loads(question)["message"]

            result, new_question = self._extract_new_question(result_message)

            new_question_id = None
            if new_question:
                new_question_id = await self._save_result(
                    subject, self._encapsulate_question(new_question), LoggerSingleton().get_logger()
                )

            check_result = CheckResult(parent_id=question_id, question=question, answer=answer, result=result)

            await self.mongo_client.insert_check_result(check_result.model_dump())

            return Question(question=question_message, answer=answer, result=result, new_question=new_question, new_question_id=new_question_id)
        except Exception as e:
            LoggerSingleton().log_error(f"Error: {e}\nStacktrace:\n{traceback.format_exc()}")

            raise e

    def _encapsulate_question(self, question):
        message = {
            "message": f"Question: {question}"
        }
        return json.dumps(message, indent=4)

    def _extract_new_question(self, text):
        if "__novapergunta__" in text:
            parts = text.split("__novapergunta__:")
            if len(parts) > 1:
                remaining_message = parts[0].strip()
                new_question = parts[1].strip()
                return remaining_message, new_question
        return text.strip(), None

    @staticmethod
    def _create_prompt_check_question(question: str, answer: str):
        system_prompt = ("Verifique minha resposta com relação ao inglês, de maneira casual. Ignore pontuações" 
                        "Me envie um feedback em português da seguinte forma. Ex de resposta: Erros cometidos: erro, erro, erro envie também um modelo da minha frase corrigida"
                        "Caso minha resposta esteja entendivel e a resposta dentro do contexto, mesmo com alguns erros, me envie uma "
                        "outra pergunta relacionada a minha resposta nesse formato __novapergunta__: Esse é um exemplo de nova pergunta, "
                         "e também uma avaliação de 1 a 10 considerando a complexidade da minha resposta, por ex par aa pergunta: Question: Who is Batman's main enemy? se minha resposta for apenas Joker a nota deve ser 1, se minha resposta for Btamn's main enemy is Joker, known as crime clown"
                         "caso minha resposta não esteja entendível não mande mais perguntas.")
        user_prompt = "Pergunta: _question_. Resposta: _answer_ ".replace("_question_", question).replace("_answer_", answer)
        return system_prompt, user_prompt

    @staticmethod
    def _create_prompt_make_question(subject: str):
        system_prompt = "Você é uma professora de inglês, iremos simular um diálogo livre. O nivel de dificuldade deverá em relação ao ingles e não em relação ao tema. Ex de resposta: Question: This is a suggested question....?"
        user_prompt = "Me envie uma pergunta em inglês de dificuldade médio, com o tema: _subject_. ".replace("_subject_", subject)

        return system_prompt, user_prompt
