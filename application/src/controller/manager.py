from src.data.connector import Connector
import seval
import json
import pydash
from boto3.dynamodb.conditions import Key, Attr
class manager:
    def __init__(self):
        self.connector = Connector()

    def load_character(self, id):
        character = self.connector.get_item(table_name='character', key={'id': id})
        character['basic_stats']= self.calculate_stats(self.get_basic_stats(), character)
        character['classes'], character['class_stats'], character['all_pasives_plain'], character['all_pasives_percentage']= self.get_classes(character)
        character['secondary_stats'] = self.calculate_stats(self.get_secondary_stats(), character)
        print(character)
        return character
      
    def get_classes(self, character): 
        character_classes = list()
        for char_class in character['classes']:
            character_classes.append(self.connector.get_item(table_name='class', key={'id': char_class}))
        char_class_pasives_plain= list()
        char_class_pasives_percentage= list()
        for char_class in character_classes:
            for pasive in char_class['pasives_plain']:
                char_class_pasives_plain.append(self.connector.get_item(table_name='pasive', key={'id': pasive}))
            for pasive in char_class['pasives_percentage']:
                char_class_pasives_percentage.append(self.connector.get_item(table_name='pasive', key={'id': pasive}))
        class_stats = dict()
        sum_class_pasives_plain = dict()
        sum_class_pasives_percentage = dict()
        for stat in character_classes[0].get('stats'):
            self.sum_dict(class_stats, stat, char_class.get('stats').get(stat))
        for char_class in character_classes:
            for char_pasive_plain in char_class_pasives_plain:
                stat = char_pasive_plain['stat'] 
                formula = char_pasive_plain['formula']
                dv = char_pasive_plain['default_values']
                self.sum_dict(sum_class_pasives_plain, stat, self.calculate(character, formula, dv))
            for char_pasive_percentage in char_class_pasives_percentage:
                stat = char_pasive_percentage['stat'] 
                formula = char_pasive_percentage['formula']
                dv = char_pasive_percentage['default_values']
                self.sum_dict(sum_class_pasives_percentage, stat, self.calculate(character, formula, dv))
        return character_classes, class_stats, sum_class_pasives_plain, sum_class_pasives_percentage

    def sum_dict(self, dict, key, value):
        if key in dict:
            dict[key]+=value
        else: 
            dict[key] = value  
        return dict

    def get_basic_stats(self):
        fe= Attr('type').contains('basic')
        basic_stats = self.connector.scan_w_filter(table_name='stat', filter_expression=fe)
        return basic_stats
  
    def get_secondary_stats(self): 
        fe= Attr('type').contains('secondary')
        secondary_stats = self.connector.scan_w_filter(table_name='stat', filter_expression=fe)
        return secondary_stats
    
    def calculate_stats(self, all_stats_list, character): 
        all_stats_dict = dict()
        for i in range(len(all_stats_list)):
            all_stats_dict[all_stats_list[i]['id']]= all_stats_list[i]
        final_stats= dict() 
        for stat in all_stats_dict: 
            stat_formula = all_stats_dict[stat]['formula']
            stat_default_values = all_stats_dict[stat]['default_values']
            final_stats[stat]= self.calculate(character, stat_formula, stat_default_values)
        return final_stats 

    def calculate(self, character, formula, dv):
        for route in dv: 
            value = pydash.get(character, route)
            if value is not None:
                if type(value) == list:
                    dv[route] = sum(value)
                else:
                    dv[route] = value
            formula = formula.replace(route, str(dv[route]))
        result = seval.safe_eval(formula)
        return result