from src.data.connector import Connector
import seval
import json
import pydash
from boto3.dynamodb.conditions import Key, Attr
import src.controller.utils as utils

class Inventory:
    def __init__(self):
        self.connector = Connector()
    
    def get_character_inventory(self, inventory_id):
        inventory = self.connector.get_item(table_name='equipment', key={'id': inventory_id})
        inventory.pop('id')
        return inventory