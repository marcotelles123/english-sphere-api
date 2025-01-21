from abc import ABC, abstractmethod


class DbClient(ABC):

    @abstractmethod
    async def insert_question(self, data: str) -> str:
        pass
