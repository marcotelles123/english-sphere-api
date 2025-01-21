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
from domain.elaborate.elaborate import Elaborate


class ElaborateBusiness:
    def __init__(self):
        self.llm_gateway_client = LlmGatewayClient()
        self.sound_to_text_client = SoundToTextClient()
        self.mongo_client = DbClientMongo()

    async def make_elaborate(self, subject: str):
        try:
            LoggerSingleton().log_info(
                f"Starting make_elaborate, creating prompt, subject={subject}"
            )
            system_prompt, user_prompt = self._create_prompt_make_elaborate(subject)
            LoggerSingleton().log_info("Calling IA...")
            result = self.llm_gateway_client.chat_completion(system_prompt, user_prompt)
            id = await self._save_result(
                subject, result, LoggerSingleton().get_logger()
            )

            LoggerSingleton().log_info(f"Returning result: {result}")

            return {"id": id, "elaborate": result}
        except Exception as e:
            LoggerSingleton().log_error(f"Error: {e}\nStacktrace:\n{traceback.format_exc()}")
            raise e

    async def _save_result(
        self, subject: str, elaborate: str, logger: logging.Logger
    ) -> str:
        logger.info(f"Saving elaborate, subject={subject}, elaborate={elaborate}. ")

        try:
            data = {"subject": subject, "result": elaborate, "first": True }
            result = await self.mongo_client.insert_elaborate(data)
            logger.info(f"Elaborate saved successfully for subject: {subject}")

            return str(result)
        except Exception as e:
            LoggerSingleton().log_error(f"Error: {e}\nStacktrace:\n{traceback.format_exc()}")
            raise e

    async def check_elaborate(self, file: FileStorage, elaborate_id: str):
        try:
            LoggerSingleton().log_info(
                f"Starting check_elaborate, finding elaborate {elaborate_id}"
            )

            result_mongo = await self.mongo_client.find_elaborates(
                {"_id": ObjectId(elaborate_id)}
            )

            elaborate = result_mongo[0]["result"]
            subject = result_mongo[0]["subject"]
            if elaborate is None:
                raise NotFoundException("elaborate", elaborate_id)

            LoggerSingleton().log_info(f"Converting to text")
            response = self.sound_to_text_client.extract_text(file)

            answer = json.loads(response.content.decode("utf-8").strip())["message"]

            system_prompt, user_prompt = self._create_prompt_check_elaborate(elaborate, answer)

            LoggerSingleton().log_info(
                f"Calling LLM elaborate {elaborate}, answer {answer}"
            )
            check_result = self.llm_gateway_client.chat_completion(system_prompt, user_prompt)

            answer = json.loads(response.content.decode("utf-8").strip())["message"]
            result_message = json.loads(check_result)["message"]
            elaborate_message = json.loads(elaborate)["message"]

            result, new_elaborate = self._extract_new_elaborate(result_message)

            new_qelaborate_id = None
            if new_elaborate:
                new_elaborate_id = await self._save_result(
                    subject, self._encapsulate_elaborate(new_elaborate), LoggerSingleton().get_logger()
                )

            check_result = CheckResult(parent_id=elaborate_id, question=elaborate, answer=answer, result=result)

            await self.mongo_client.insert_check_result(check_result.model_dump())

            return Elaborate(question=elaborate_message, answer=answer, result=result, new_question=new_elaborate, new_question_id=new_elaborate_id)
        except Exception as e:
            LoggerSingleton().log_error(f"Error: {e}\nStacktrace:\n{traceback.format_exc()}")

            raise e

    def _encapsulate_elaborate(self, elaborate):
        message = {
            "message": f"Elaborate: {elaborate}"
        }
        return json.dumps(message, indent=4)

    def _extract_new_elaborate(self, text):
        if "__novapergunta__" in text:
            parts = text.split("__novapergunta__:")
            if len(parts) > 1:
                remaining_message = parts[0].strip()
                new_elaborate = parts[1].strip()
                return remaining_message, new_elaborate
        return text.strip(), None

    @staticmethod
    def _create_prompt_check_elaborate(elaborate: str, answer: str):
        system_prompt = ("Verifique minha resposta com relação ao inglês, de maneira casual. Ignore pontuações" 
                        "Me envie um feedback em português da seguinte forma. Ex de resposta: Erros cometidos: erro, erro, erro envie também um modelo da minha frase corrigida"
                        "Caso minha resposta esteja entendivel e a resposta dentro do contexto, mesmo com alguns erros, "
                        "mantenha o dialogo me fazendo uma nova pergunta relacionado a minha resposta anterior __novapergunta__: Esse é um exemplo de nova pergunta, "
                         "e também uma avaliação de 1 a 10 considerando a complexidade da minha resposta, por ex par aa pergunta: Question: Who is Batman's main enemy? se minha resposta for apenas Joker a nota deve ser 1, se minha resposta for Btamn's main enemy is Joker, known as crime clown"
                         "caso minha resposta não esteja entendível não mande mais perguntas.")
        user_prompt = "Pergunta: _question_. Resposta: _answer_ ".replace("_question_", elaborate).replace("_answer_", answer)
        return system_prompt, user_prompt

    @staticmethod
    def _create_prompt_make_elaborate(subject: str):
        system_prompt = ("Você é uma professora de inglês, iremos simular um diálogo livre. "
                         "O nivel de dificuldade deverá em relação ao ingles e não em relação ao tema. "
                         "Voce deverá fazer perguntas para eu elaborar e não dar respostas simples"
                         "Ex de resposta: Question: This is a suggested question....?")
        user_prompt = "Me faça uam pergunta pessoal com o tema: _subject_. ".replace("_subject_", subject)

        return system_prompt, user_prompt
