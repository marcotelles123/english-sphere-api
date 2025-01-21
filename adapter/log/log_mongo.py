import asyncio
import os
from datetime import datetime

import motor.motor_asyncio

from Util.config_util import ConfigUtil


class LogMongo:
    def __init__(self):
        db_name = ConfigUtil().get_config("db_log_name", "db-english-sphere-log")
        user = ConfigUtil().get_config("db_log_user", "usr-marco")
        password = ConfigUtil().get_config("db_log_password", "1234")
        host = ConfigUtil().get_config("db_log_host", "mongo-english-sphere")
        port = int(ConfigUtil().get_config("db_log_port", 27017))
        uri = f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def insert_log(self, level, message):
        log_entry = {
            "level": level,
            "message": message,
            "hostname": os.getenv('HOSTNAME', 'mongo-english-sphere'),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "version": "1.0"
        }
        try:
            await self.db.log.insert_one(log_entry)
        except Exception as e:
            print(f"Failed to insert log into MongoDB: {e}")