from src.data.connector import Connector
import seval
import json
import pydash
from boto3.dynamodb.conditions import Key, Attr
import src.controller.utils as utils

class Equipment:
    def __init__(self):
        self.connector = Connector()
    
    def get_character_equipment(self, equipment_id):
        equipment = self.connector.get_item(table_name='equipment', key={'id': equipment_id})
        equipment.pop('id')
        return {'stats': self.get_equipment_stats(equipment)}
    
    def get_equipment_stats(self, equipment):
        total_stats= dict()
        for item in equipment:
            stats = equipment[item].get('stats') if equipment[item].get('stats') is not None else []
            for stat in stats:
                utils.sum_dict(total_stats, stat, stats[stat])
        return total_stats