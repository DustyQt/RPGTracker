from src.data.connector import Connector
from src.controller.character import Character
import seval
import json
import pydash
import src.controller.utils as utils
from boto3.dynamodb.conditions import Key, Attr
class manager:
    def __init__(self):
        self.connector = Connector()
        self.character_controller = Character()

    def load_character(self, id):
        return self.character_controller.load_character(id)