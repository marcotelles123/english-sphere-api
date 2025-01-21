
import motor.motor_asyncio

from Util.config_util import ConfigUtil
from adapter.db.db_client import DbClient

from adapter.log.log_config import LoggerSingleton

class DbClientMongo(DbClient):
    def __init__(self):
        db_name = ConfigUtil().get_config("db_name", "db-english-sphere")
        user = ConfigUtil().get_config("db_user", "usr-marco")
        password = ConfigUtil().get_config("db_password", "1234")
        host = ConfigUtil().get_config("db_host", "localhost")
        port = int(ConfigUtil().get_config("db_port", 27017))
        uri = f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
        LoggerSingleton().log_info(f"MongoDB uri={uri}")
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def insert_question(self, question_data):
        result = await self.db.questions.insert_one(question_data)
        return result.inserted_id

    async def find_questions(self, query=None):
        if query:
            results = await self.db.questions.find(query).to_list(length=None)
        else:
            results = await self.db.questions.find().to_list(length=None)
        return results

    async def insert_elaborate(self, elaborate_data):
        result = await self.db.elaborates.insert_one(elaborate_data)
        return result.inserted_id

    async def find_elaborates(self, query=None):
        if query:
            results = await self.db.elaborates.find(query).to_list(length=None)
        else:
            results = await self.db.elaborates.find().to_list(length=None)
        return results

    async def insert_check_result(self, result_data):
        result = await self.db.check_result.insert_one(result_data)
        return result.inserted_id
