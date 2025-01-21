import configparser
import requests
import os

from Util.AIUtil import AIUtil
from Util.config_util import ConfigUtil

MAX_TOKEN = 1000

class SoundToTextClient:
    def get_base_url(self):
        return ConfigUtil().get_config("sound_to_text_url", "").strip("/")

    def extract_text(self, file):
        url = f"{self.get_base_url()}/extract-text"

        files = {'file': ('audio_file', file)}
        response = requests.post(url, files=files)

        return response


class LlmGatewayPayloadCreation:
    @staticmethod
    def build_chat_completion_payload(prompt, max_token):
        payload = {
            "prompt": prompt,
            "max_token": max_token
        }
        return payload

