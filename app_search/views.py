from django.views.decorators.csrf import csrf_exempt
import pickle
import os
import itertools
from datetime import datetime
import os
from django.http import JsonResponse

from .app_search_modules.general_functionality import PcaDataProcessor, remove_punctuation, get_element_search_criteria
from .app_search_modules.normal_search_functionality import NormalSearch
from .app_search_modules.regex_search_functionality import RegexSearch


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(f"{BASE_DIR}/data/database/database_list.pickle", "rb") as open_object:
    database_list = pickle.load(open_object)

database_list_length = len(database_list)
vowel = '[aeiouy]'
consonant = '[qwrtpsdfghjklzxcvbnm]'
pagination_bin_size = 25


@csrf_exempt
def search(request):
    # getting data from request
    return_value = request.POST.dict()
    user_expression = return_value['user_search_field_value']
    filtering_data = return_value['checked_string']
    database_indexes = return_value['database_indexes_string']

    # processing data
    user_expression = remove_punctuation(user_expression)
    pca_data_processor = PcaDataProcessor()
    filtering_data = pca_data_processor.process_filtering_data(filtering_data)
    database_indexes = pca_data_processor.process_database_indexes(database_indexes)
    user_expression = pca_data_processor.user_wildcards_to_regex(user_expression, vowel, consonant)
    type_of_search = pca_data_processor.type_of_search

    # 'norma' search
    next_search_start_index = 0
    if type_of_search == 'normal':
        user_expression_length = len(user_expression)
        new_dict = {}
        textunit_counter = 0
        element_counter = 0

        for element in database_list:
            element_counter += 1
            element_search_criteria = get_element_search_criteria(element, database_indexes, filtering_data)
            if element_search_criteria == filtering_data:
                normal_search_object = NormalSearch()
                cut_off_points = normal_search_object.get_cut_off_points(user_expression, element, user_expression_length)
                parts = normal_search_object.get_parts(element, cut_off_points)
                single_result_dict = normal_search_object.get_single_results_dict(element, parts, cut_off_points)
                if len(single_result_dict) > 0:
                    new_dict['result' + str(textunit_counter)] = single_result_dict
                    textunit_counter += 1
                    if textunit_counter == pagination_bin_size:
                        next_search_start_index = element_counter
        
    # 'regex' search
    elif type_of_search == 'regex':
        new_dict = {}
        regex_search_object = RegexSearch()
        user_expression_regex = regex_search_object.add_word_boundaries(user_expression)

        words_found_list = []
        for element in database_list:
            element_search_criteria = get_element_search_criteria(element, database_indexes, filtering_data)
            if element_search_criteria == filtering_data:
                words_found_list = regex_search_object.regex_search(
                                                user_expression_regex=user_expression_regex,
                                                words_found_list=words_found_list,
                                                element=element)

        if len(words_found_list) > 0:
            list_of_tuples = regex_search_object.get_word_type_counts_list(words_found_list)
            new_dict['result'] = {
                'list_of_tuples': list_of_tuples
            }

    # Final processing of new_dict
    textunits_found_number = len(new_dict)
    # this is the way to slice the first "pagination_bin_size" chunk from the whole new_dict
    new_dict = dict(itertools.islice(new_dict.items(), pagination_bin_size))
    new_dict['pagination_bin_size'] = pagination_bin_size
    new_dict['previous_search_start_index'] = 0
    new_dict['next_search_start_index'] = next_search_start_index
    new_dict['textunits_found_number'] = textunits_found_number

    return JsonResponse(new_dict)


@csrf_exempt
def pagination(request):
    # getting data from request
    return_value = request.POST.dict()
    user_expression = return_value['user_expression']
    filtering_data = return_value['filtering_data']
    database_indexes = return_value['database_indexes']
    previous_search_start_index = return_value['previous_search_start_index']
    next_search_start_index = return_value['next_search_start_index']
    textunits_found_number = return_value['textunits_found_number']
    pagination_button_type = return_value['pagination_button_type']
    
    # processing data
    user_expression = remove_punctuation(user_expression)
    pca_data_processor = PcaDataProcessor()
    filtering_data = pca_data_processor.process_filtering_data(filtering_data)
    database_indexes = pca_data_processor.process_database_indexes(database_indexes)
    previous_search_start_index = previous_search_start_index.split(',')
    previous_search_start_index = list(map(int, previous_search_start_index))
    next_search_start_index = int(next_search_start_index)
    textunits_found_number = int(textunits_found_number)

    user_expression_length = len(user_expression)
    new_dict = {}
    textunit_counter = 0
    if pagination_button_type == "pagination_button_next":
        element_counter = next_search_start_index
        search_beginning = next_search_start_index
    else:
        element_counter = previous_search_start_index[-3]
        search_beginning = previous_search_start_index[-3]
    for index in range(search_beginning, database_list_length):
        element_counter += 1
        element_search_criteria = get_element_search_criteria(database_list[index], database_indexes, filtering_data)
        if element_search_criteria == filtering_data:
            normal_search_object = NormalSearch()
            cut_off_points = normal_search_object.get_cut_off_points(user_expression, database_list[index], user_expression_length)
            parts = normal_search_object.get_parts(database_list[index], cut_off_points)
            single_result_dict = normal_search_object.get_single_results_dict(database_list[index], parts, cut_off_points)
            if len(single_result_dict) > 0:
                new_dict['result' + str(textunit_counter)] = single_result_dict
                textunit_counter += 1
                if textunit_counter == pagination_bin_size:
                    next_search_start_index = element_counter
                    break

    # Final processing of new_dict
    # this is the way to slice the first "pagination_bin_size" chunk from the whole new_dict
    new_dict = dict(itertools.islice(new_dict.items(), pagination_bin_size))
    new_dict['pagination_bin_size'] = pagination_bin_size
    if pagination_button_type == "pagination_button_next":
        new_dict['previous_search_start_index'] = previous_search_start_index
        new_dict['next_search_start_index'] = next_search_start_index
    else:
        new_dict['previous_search_start_index'] = previous_search_start_index[:-2]
        new_dict['next_search_start_index'] = previous_search_start_index[-2]
    new_dict['textunits_found_number'] = textunits_found_number

    return JsonResponse(new_dict)