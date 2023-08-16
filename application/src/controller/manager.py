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
        character['equipment'] = self.get_character_equipment(character)
        character['basic_stats']= self.calculate_stats(self.get_basic_stats(), character)
        character['classes'] = self.get_classes(character)
        character['class_stats'] = self.get_class_stats(character)
        character['all_pasives_plain'], character['all_pasives_percentage'] = self.get_class_pasives(character)
        character['info_fits'], character['effect_fits'] = self.get_fits(character)
        character['all_pasives_plain'], character['all_pasives_percentage'] = self.get_fits_pasives(character, character['all_pasives_plain'], character['all_pasives_percentage'])
        character['basic_stats']= self.calculate_stats(self.get_basic_stats(), character)
        character['secondary_stats'] = self.calculate_stats(self.get_secondary_stats(), character)
        character['race'] = self.get_race(character)
        character['race_stats'] = self.calculate_stats(self.get_race_stats(character), character)
        for index, value in enumerate(character['classes']):
            character['classes'][index]['precalculated_effect_skills'] = self.pre_calculate_skills(character, value)
        return character
 
    def get_classes(self, character):
        character_classes = list()
        for char_class in character['classes']:
            character_classes.append(self.connector.get_item(table_name='class', key={'id': char_class}))
        return character_classes
     
    def get_class_stats(self, character):
        character_classes = character['classes']
        class_stats = dict()
        main_class= character_classes[0]
        for stat in main_class.get('stats'):
            self.sum_dict(class_stats, stat, main_class.get('stats').get(stat))
        return class_stats
    
    def get_class_pasives(self, character):
        character_classes = character['classes']
        char_class_pasives_plain= list()
        char_class_pasives_percentage= list()
        for char_class in character_classes:
            char_class_pasives_plain.extend(char_class['pasives_plain'])
            char_class_pasives_percentage.extend(char_class['pasives_percentage'])
        sum_class_pasives_plain = dict()
        sum_class_pasives_percentage = dict()
        for char_pasive_plain in char_class_pasives_plain:
            for effect in char_pasive_plain['effects']:
                if effect.get('effect') == 'PASSIVE':
                    stat = effect['stat']
                    formula = effect['formula']
                    dv = effect['default_values']
                    self.sum_dict(sum_class_pasives_plain, stat, self.calculate(character, formula, dv))
        for char_pasive_percentage in char_class_pasives_percentage:
            for effect in char_pasive_percentage['effects']:
                if effect.get('effect') == 'PASSIVE':
                    stat = effect['stat'] 
                    formula = effect['formula']
                    dv = effect['default_values']
                    self.sum_dict(sum_class_pasives_percentage, stat, self.calculate(character, formula, dv))
        return sum_class_pasives_plain, sum_class_pasives_percentage
    
    def get_fits_pasives(self, character, sum_fits_passives_plain, sum_fits_pasives_percentage):
        fit_passives_plain= list()
        fit_passives_percentage= list()
        passive_fits = list()
        for fit in character['passive_fits']:
            passive_fits.append(self.connector.get_item(table_name='fit', key={'id': fit}))
        for fit in passive_fits:
            if fit['type'] == 'passive_plain':
                fit_passives_plain.append(fit)
            if fit['type'] == 'passive_percentage':
                fit_passives_percentage.append(fit)
        for fit in fit_passives_plain: 
            for effect in fit['effects']:
                if effect.get('effect') == 'PASSIVE':
                    stat = effect['stat']
                    formula = effect['formula']
                    dv = effect['default_values']
                    self.sum_dict(sum_fits_passives_plain, stat, self.calculate(character, formula, dv))
        for fit in fit_passives_percentage: 
            for effect in fit['effects']:
                if effect.get('effect') == 'PASSIVE':
                    stat = effect['stat']  
                    formula = effect['formula']
                    dv = effect['default_values']
                    self.sum_dict(sum_fits_pasives_percentage, stat, self.calculate(character, formula, dv))
        return sum_fits_passives_plain, sum_fits_pasives_percentage

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
    
    def get_race_stats(self, character): 
        race_stats = list()
        race = character['race']
        for stat in race['stats']:
            race_stats.append(self.connector.get_item(table_name='stat', key={'id': stat}))
        return race_stats
    
    def get_race(self, character): 
        res = self.connector.get_item(table_name='race', key={'id': character['race']})
        return res
    
    def get_fits(self, character): 
        character_info_fits = list()
        character_effect_fits = list()
        for fit in character['info_fits']:
            character_info_fits.append(self.connector.get_item(table_name='fit', key={'id': fit}))
        for fit in character['effect_fits']:
            character_effect_fits.append(self.connector.get_item(table_name='fit', key={'id': fit}))     
        return character_info_fits, character_effect_fits

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
    
    def precalculate(self, character, formula, dv):
        for route in dv: 
            value = pydash.get(character, route)
            if value is not None:
                if type(value) == list:
                    dv[route] = sum(value)
                else:
                    dv[route] = value
            formula = formula.replace(route, str(dv[route]))
        return formula 
     
    def pre_calculate_skills(self, character, e): 
        element_skills_dict = list() 
        for skill in e['effect_skills']:
            precalc_skill = skill.copy()
            precalc_skill['effects']= list()
            for effect in skill['effects']:
                effect_precalculated ={'formula':  self.precalculate(character, effect['formula'], effect['default_values']),
                                    'stat': effect['stat'],
                                    'effect': effect['effect']}
                precalc_skill['effects'].append(effect_precalculated)
            element_skills_dict.append(precalc_skill)
        return element_skills_dict

