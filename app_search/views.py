from django.views.decorators.csrf import csrf_exempt
import pickle
import string
import re
import os
# import operator
import itertools
from datetime import datetime
import os
from django.http import JsonResponse

from .app_search_modules.general_functionality import remove_punctuation, PcaDataProcessor, get_element_search_criteria
from .app_search_modules.normal_search_functionality import normal_search, NormalSearch
# from .app_search_modules.regex_search_functionality import get_word_type_counts_list, regex_search, add_word_boundaries
from .app_search_modules.regex_search_functionality import RegexSearch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(f"{BASE_DIR}/data/database/database_list.pickle", "rb") as open_object:
    database_list = pickle.load(open_object)

# setting up general variables for the search function
exotic_punctuation = ["“", "”", "’", "‘", "—"]



########################
# helper functions ENDED
########################
vowel = '[aeiouy]'
consonant = '[qwrtpsdfghjklzxcvbnm]'
pagination_bin_size = 25

@csrf_exempt
def search(request):
    return_value = request.POST.dict()
    user_expression = return_value['user_search_field_value']
    filtering_data = return_value['checked_string']
    database_indexes = return_value['database_indexes_string']

    user_expression = remove_punctuation(user_expression)
    pca_data_processor = PcaDataProcessor()
    filtering_data = pca_data_processor.process_filtering_data(filtering_data)
    database_indexes = pca_data_processor.process_database_indexes(database_indexes)
    user_expression = pca_data_processor.user_wildcards_to_regex(user_expression, vowel, consonant)
    type_of_search = pca_data_processor.type_of_search

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
                # single_result_dict = normal_search(user_expression=user_expression,
                #                                    element=element,
                #                                    user_expression_length=user_expression_length)
                
                if len(single_result_dict) > 0:
                    new_dict['result' + str(textunit_counter)] = single_result_dict
                    textunit_counter += 1
                    if textunit_counter == pagination_bin_size:
                        next_search_start_index = element_counter
        

    # this is for regex searches
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


database_list_length = len(database_list)



@csrf_exempt
def next_button(request):
    return_value = request.POST.dict()
    user_expression = return_value['user_expression']
    filtering_data = return_value['filtering_data']
    database_indexes = return_value['database_indexes']
    previous_search_start_index = return_value['previous_search_start_index']
    next_search_start_index = return_value['next_search_start_index']
    textunits_found_number = return_value['textunits_found_number']

    user_expression = remove_punctuation(user_expression)
    pca_data_processor = PcaDataProcessor()
    filtering_data = pca_data_processor.process_filtering_data(filtering_data)
    database_indexes = pca_data_processor.process_database_indexes(database_indexes)

    # processing previous_search_start_index string - I needed to use ',' instead of '&' because there were problems
    # with splitting...
    previous_search_start_index = previous_search_start_index.split(',')
    previous_search_start_index = list(map(int, previous_search_start_index))

    next_search_start_index = int(next_search_start_index)
    textunits_found_number = int(textunits_found_number)

    user_expression_length = len(user_expression)
    new_dict = {}
    textunit_counter = 0
    element_counter = next_search_start_index

    for index in range(next_search_start_index, database_list_length):
        element_counter += 1
        element_search_criteria = get_element_search_criteria(database_list[index], database_indexes, filtering_data)
        if element_search_criteria == filtering_data:
            normal_search_object = NormalSearch()
            cut_off_points = normal_search_object.get_cut_off_points(user_expression, database_list[index], user_expression_length)
            parts = normal_search_object.get_parts(database_list[index], cut_off_points)
            single_result_dict = normal_search_object.get_single_results_dict(database_list[index], parts, cut_off_points)
            # single_result_dict = normal_search(user_expression=user_expression,
            #                                     element=database_list[index],
            #                                     user_expression_length=user_expression_length)
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
    new_dict['previous_search_start_index'] = previous_search_start_index
    new_dict['next_search_start_index'] = next_search_start_index
    new_dict['textunits_found_number'] = textunits_found_number

    return JsonResponse(new_dict)



@csrf_exempt
def previous_button(request):
    return_value = request.POST.dict()
    user_expression = return_value['user_expression']
    filtering_data = return_value['filtering_data']
    database_indexes = return_value['database_indexes']
    previous_search_start_index = return_value['previous_search_start_index']
    next_search_start_index = return_value['next_search_start_index']
    textunits_found_number = return_value['textunits_found_number']
    # removing punctuation
    for c in string.punctuation:  # this removes punctuation
        user_expression = user_expression.replace(c, "")
    for c in exotic_punctuation:
        user_expression = user_expression.replace(c, "")  # this removes more exotic punctuation

    if filtering_data == 'all':
        filtering_data = []
    else:
        filtering_data = filtering_data.split('-')
    filtering_data_length = len(filtering_data)

    if database_indexes == 'all':
        database_indexes = []
    else:
        database_indexes = database_indexes.split('-')
        database_indexes = list(map(int, database_indexes))

    global type_of_search
    type_of_search = 'normal'

    # transforming the user wildcards into python regular expressions
    if "QQ1" in user_expression:
        indices_list = [m.start() for m in re.finditer('QQ1', user_expression)]
        index_counter = 0
        for index in indices_list:
            user_expression = user_expression[:index - index_counter] + '\w' + user_expression[
                                                                               index - index_counter + 3:]
            index_counter += 1
        type_of_search = 'regex'

    if "QQ2" in user_expression:
        indices_list = [m.start() for m in re.finditer('QQ2', user_expression)]
        for index in indices_list:
            user_expression = user_expression[:index] + '\w+' + user_expression[index + 3:]
        type_of_search = 'regex'

    if "QQ3" in user_expression:
        indices_list = [m.start() for m in re.finditer('QQ3', user_expression)]
        index_counter = 0
        for index in indices_list:
            user_expression = user_expression[:index + index_counter] + vowel + user_expression[
                                                                                index + index_counter + 3:]
            index_counter += 4
        type_of_search = 'regex'

    if "QQ4" in user_expression:
        indices_list = [m.start() for m in re.finditer('QQ4', user_expression)]
        index_counter = 0
        for index in indices_list:
            user_expression = user_expression[:index + index_counter] + consonant + user_expression[
                                                                                    index + index_counter + 3:]
            index_counter += 20
        type_of_search = 'regex'

    # processing previous_search_start_index string - I needed to use ',' instead of '&' because there were problems
    # with splitting...
    previous_search_start_index = previous_search_start_index.split(',')
    previous_search_start_index = list(map(int, previous_search_start_index))

    # processing next_search_start_index string
    next_search_start_index = int(next_search_start_index)

    # processing next_search_start_index string
    textunits_found_number = int(textunits_found_number)
    
    new_dict = {}

    # the search loop for 'mormal' cases which do not involve regex
    # 25 stands here for text units without caps - first search is done here to ged indices,
    # than the final parts are taken from 14, which is data_readable
    if type_of_search == 'normal':
        user_expression_length = len(user_expression)
        new_dict = {}
        textunit_counter = 0
        element_counter = previous_search_start_index[-3]

        if filtering_data_length == 5:
            for index in range(previous_search_start_index[-3], database_list_length):
                element_counter += 1
                if database_list[index][database_indexes[0]] == filtering_data[0] \
                        and database_list[index][database_indexes[1]] == filtering_data[1] \
                        and database_list[index][database_indexes[2]] == filtering_data[2] \
                        and database_list[index][database_indexes[3]] == filtering_data[3] \
                        and database_list[index][database_indexes[4]] == filtering_data[4]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=database_list[index],
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter
                            break

        elif filtering_data_length == 4:
            for index in range(previous_search_start_index[-3], database_list_length):
                element_counter += 1
                if database_list[index][database_indexes[0]] == filtering_data[0] \
                        and database_list[index][database_indexes[1]] == filtering_data[1] \
                        and database_list[index][database_indexes[2]] == filtering_data[2] \
                        and database_list[index][database_indexes[3]] == filtering_data[3]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=database_list[index],
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter
                            break

        elif filtering_data_length == 3:
            for index in range(previous_search_start_index[-3], database_list_length):
                element_counter += 1
                if database_list[index][database_indexes[0]] == filtering_data[0] \
                        and database_list[index][database_indexes[1]] == filtering_data[1] \
                        and database_list[index][database_indexes[2]] == filtering_data[2]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=database_list[index],
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter
                            break

        elif filtering_data_length == 2:
            for index in range(previous_search_start_index[-3], database_list_length):
                element_counter += 1
                if database_list[index][database_indexes[0]] == filtering_data[0] \
                        and database_list[index][database_indexes[1]] == filtering_data[1]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=database_list[index],
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter
                            break

        elif filtering_data_length == 1:
            for index in range(previous_search_start_index[-3], database_list_length):
                element_counter += 1
                if database_list[index][database_indexes[0]] == filtering_data[0]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=database_list[index],
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter
                            break

        # for now only this case - later correct the above...
        elif filtering_data_length == 0:
            for index in range(previous_search_start_index[-3], database_list_length):
                element_counter += 1
                single_result_dict = normal_search(user_expression=user_expression,
                                                   element=database_list[index],
                                                   user_expression_length=user_expression_length)
                if len(single_result_dict) > 0:
                    new_dict['result' + str(textunit_counter)] = single_result_dict
                    textunit_counter += 1
                    if textunit_counter == pagination_bin_size:
                        next_search_start_index = element_counter
                        break

    # this is for regex searches
    elif type_of_search == 'regex':
        new_dict = {}
        # adding word boundary wildmarks to all words
        user_expression_list = user_expression.split()
        correct_user_expression_list = []
        for word in user_expression_list:
            correct_word = "\\b" + word + "\\b"
            correct_user_expression_list.append(correct_word)
        user_expression_regex = " ".join(correct_user_expression_list)
        words_found_list = []

        if filtering_data_length == 5:
            for element in database_list:
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1] \
                        and element[database_indexes[2]] == filtering_data[2] \
                        and element[database_indexes[3]] == filtering_data[3] \
                        and element[database_indexes[4]] == filtering_data[4]:
                    words_found_list = regex_search(database_list=database_list,
                                                    user_expression=user_expression,
                                                    user_expression_regex=user_expression_regex,
                                                    words_found_list=words_found_list,
                                                    element=element)

            if len(words_found_list) > 0:
                list_of_tuples = word_type_counts_list(words_found_list)

                new_dict['result'] = {
                    'list_of_tuples': list_of_tuples
                }

        if filtering_data_length == 4:
            for element in database_list:
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1] \
                        and element[database_indexes[2]] == filtering_data[2] \
                        and element[database_indexes[3]] == filtering_data[3]:
                    words_found_list = regex_search(database_list=database_list,
                                                    user_expression=user_expression,
                                                    user_expression_regex=user_expression_regex,
                                                    words_found_list=words_found_list,
                                                    element=element)

            if len(words_found_list) > 0:
                list_of_tuples = word_type_counts_list(words_found_list)

                new_dict['result'] = {
                    'list_of_tuples': list_of_tuples
                }

        if filtering_data_length == 3:
            for element in database_list:
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1] \
                        and element[database_indexes[2]] == filtering_data[2]:
                    words_found_list = regex_search(database_list=database_list,
                                                    user_expression=user_expression,
                                                    user_expression_regex=user_expression_regex,
                                                    words_found_list=words_found_list,
                                                    element=element)

            if len(words_found_list) > 0:
                list_of_tuples = word_type_counts_list(words_found_list)

                new_dict['result'] = {
                    'list_of_tuples': list_of_tuples
                }

        if filtering_data_length == 2:
            for element in database_list:
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1]:
                    words_found_list = regex_search(database_list=database_list,
                                                    user_expression=user_expression,
                                                    user_expression_regex=user_expression_regex,
                                                    words_found_list=words_found_list,
                                                    element=element)

            if len(words_found_list) > 0:
                list_of_tuples = word_type_counts_list(words_found_list)

                new_dict['result'] = {
                    'list_of_tuples': list_of_tuples
                }

        if filtering_data_length == 1:
            for element in database_list:
                if element[database_indexes[0]] == filtering_data[0]:
                    words_found_list = regex_search(database_list=database_list,
                                                    user_expression=user_expression,
                                                    user_expression_regex=user_expression_regex,
                                                    words_found_list=words_found_list,
                                                    element=element)

            if len(words_found_list) > 0:
                list_of_tuples = word_type_counts_list(words_found_list)

                new_dict['result'] = {
                    'list_of_tuples': list_of_tuples
                }

        if filtering_data_length == 0:
            for element in database_list:
                words_found_list = regex_search(database_list=database_list,
                                                user_expression=user_expression,
                                                user_expression_regex=user_expression_regex,
                                                words_found_list=words_found_list,
                                                element=element)

            if len(words_found_list) > 0:
                list_of_tuples = word_type_counts_list(words_found_list)

                new_dict['result'] = {
                    'list_of_tuples': list_of_tuples
                }

    # this is the way to slice the first "pagination_bin_size" chunk from the whole new_dict
    new_dict = dict(itertools.islice(new_dict.items(), pagination_bin_size))

    new_dict['pagination_bin_size'] = pagination_bin_size
    new_dict['previous_search_start_index'] = previous_search_start_index[:-2]
    new_dict['next_search_start_index'] = previous_search_start_index[-2]
    new_dict['textunits_found_number'] = textunits_found_number

    return JsonResponse(new_dict)


@csrf_exempt
def create_audio(request):
    return_value = request.POST.dict()
    audio_file_name = return_value['audio_file_name']
    textunit_start = return_value['textunit_start']
    textunit_duration = return_value['textunit_duration']
    start_buffer = return_value['start_buffer']
    end_buffer = return_value['end_buffer']

    resulting_audio_name = ''
    for filename in os.listdir(BASE_DIR + "/data/audio"):
        if filename == audio_file_name + '.mp3':
            resulting_audio_name = datetime.now().strftime('%Y_%m_%d %H_%M_%S_%f') + '.mp3'
            
            ffmpeg_command = 'ffmpeg -ss ' + str(float(textunit_start) - float(start_buffer)) + ' -t ' + str(
                float(textunit_duration) + float(start_buffer) +
                float(end_buffer)) + ' -i ' + BASE_DIR + '/"data/audio/' + \
                filename + '" -c copy ' + '"' + BASE_DIR + '/media/' + resulting_audio_name + '"'
        
            os.system(ffmpeg_command)
            break

    resulting_audio_name_for_frontend = "/media/" + resulting_audio_name

    return JsonResponse({'resulting_audio_file': resulting_audio_name_for_frontend})