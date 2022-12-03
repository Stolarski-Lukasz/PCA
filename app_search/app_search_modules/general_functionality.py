import string
import re


def remove_punctuation(user_expression):
    exotic_punctuation = ["“", "”", "’", "‘", "—"]
    # this removes punctuation
    for c in string.punctuation:  
        user_expression = user_expression.replace(c, "")
    # this removes more exotic punctuation
    for c in exotic_punctuation:
        user_expression = user_expression.replace(c, "")
    return user_expression


def get_element_search_criteria(element, database_indexes, filtering_data):
    element_search_criteria = []
    database_indexes_counter = 0
    for filtering_datum in filtering_data:
        element_search_criteria.append(element[database_indexes[database_indexes_counter]])
        database_indexes_counter += 1
    return element_search_criteria


class PcaDataProcessor:

    type_of_search = "normal"


    def process_filtering_data(self, filtering_data):
        if filtering_data == 'all':
            filtering_data = []
        else:
            filtering_data = filtering_data.split('-')
        return filtering_data


    def process_database_indexes(self, database_indexes):
        if database_indexes == 'all':
            database_indexes = []
        else:
            database_indexes = database_indexes.split('-')
            database_indexes = list(map(int, database_indexes))
        return database_indexes


    def user_wildcards_to_regex(self, user_expression, vowel, consonant):
        if "QQ1" in user_expression:
            indices_list = [m.start() for m in re.finditer('QQ1', user_expression)]
            index_counter = 0
            for index in indices_list:
                user_expression = user_expression[:index - index_counter] + '\w' + user_expression[
                                                                                index - index_counter + 3:]
                index_counter += 1
            self.type_of_search = 'regex'

        if "QQ2" in user_expression:
            indices_list = [m.start() for m in re.finditer('QQ2', user_expression)]
            for index in indices_list:
                user_expression = user_expression[:index] + '\w+' + user_expression[index + 3:]
            self.type_of_search = 'regex'

        if "QQ3" in user_expression:
            indices_list = [m.start() for m in re.finditer('QQ3', user_expression)]
            index_counter = 0
            for index in indices_list:
                user_expression = user_expression[:index + index_counter] + vowel + user_expression[
                                                                                    index + index_counter + 3:]
                index_counter += 5
            self.type_of_search = 'regex'

        if "QQ4" in user_expression:
            indices_list = [m.start() for m in re.finditer('QQ4', user_expression)]
            index_counter = 0
            for index in indices_list:
                user_expression = user_expression[:index + index_counter] + consonant + user_expression[
                                                                                        index + index_counter + 3:]
                index_counter += 19
            self.type_of_search = 'regex'
            
        return user_expression

