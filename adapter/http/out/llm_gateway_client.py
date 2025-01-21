import configparser
import requests
import os

from Util.AIUtil import AIUtil
from Util.config_util import ConfigUtil
from adapter.log.log_config import LoggerSingleton

MAX_TOKEN = 1000

class LlmGatewayClient:
    def get_base_url(self):
        return ConfigUtil().get_config("llm_gateway_url", "").strip("/")

    def chat_completion(self, system_prompt, user_prompt):
        url = f"{self.get_base_url()}/chat-completion"
        response = requests.post(url, json=LlmGatewayPayloadCreation.build_chat_completion_payload(system_prompt, user_prompt, MAX_TOKEN))

        if self.is_error_status_code(response.status_code):
            LoggerSingleton().log_error(f"An error occurred: {str(response.content)}")
            raise Exception(f"Error calling llm-gateway: {response.status_code} - {response.reason}")

        return AIUtil.process_content(response.content)

    def is_error_status_code(self, status_code):
        return 400 <= status_code <= 599


class LlmGatewayPayloadCreation:
    @staticmethod
    def build_chat_completion_payload(system_prompt, user_prompt, max_token):
        payload = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "max_token": max_token
        }
        return payload

