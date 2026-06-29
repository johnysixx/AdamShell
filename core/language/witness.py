from abc import ABC, abstractmethod


class Witness(ABC):

    @abstractmethod
    def hear(self, word):
        pass