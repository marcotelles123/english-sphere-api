import json


class AIUtil:
    @staticmethod
    def process_content(content):
        if isinstance(content, bytes):
            parsed_content = json.loads(content.decode('utf-8'))
            return json.dumps(parsed_content, ensure_ascii=False, indent=4)
        elif isinstance(content, str):
            parsed_content = json.loads(content)
            return json.dumps(parsed_content, ensure_ascii=False, indent=4)
        else:
            raise TypeError(f"Tipo de conteúdo não suportado: {type(content)}")
