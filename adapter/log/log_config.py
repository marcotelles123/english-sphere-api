import logging
import os
import asyncio
from flask import g
from Util.config_util import ConfigUtil
from adapter.log.log_mongo import LogMongo


class LoggerSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        log_file_path = ConfigUtil().get_config('log_file_path', 'temp/logs/app.log')
        log_level = ConfigUtil().get_config('log_level', 'INFO').upper()

        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        logging.basicConfig(
            filename=log_file_path,
            level=getattr(logging, log_level, logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger(__name__)

    def get_logger(self) -> logging.Logger:
        return self.logger

    def log_info(self, message):
        formatted_message = self._add_correlation_key(message)
        self.logger.info(formatted_message)
        asyncio.create_task(self._insert_log_to_mongo('INFO', formatted_message))

    def log_debug(self, message):
        formatted_message = self._add_correlation_key(message)
        self.logger.debug(formatted_message)
        asyncio.create_task(self._insert_log_to_mongo('DEBUG', formatted_message))

    def log_error(self, message):
        formatted_message = self._add_correlation_key(message)
        self.logger.error(formatted_message)
        asyncio.create_task(self._insert_log_to_mongo('ERROR', formatted_message))

    def _add_correlation_key(self, message):
        correlation_id = getattr(g, 'correlation_id', 'N/A')
        return f"Correlation key {correlation_id}. {message}"

    async def _insert_log_to_mongo(self, param, formatted_message):
        print("async callexd")
        log_mongo = LogMongo()
        await log_mongo.insert_log(param, formatted_message)

