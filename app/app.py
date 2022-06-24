from bottle import run, response, static_file, hook, route, jinja2_view, get, error
import pickle
import string
import re
import os
import operator
import itertools
from datetime import datetime

import glob
import schedule
import time


@hook('after_request')
def enable_cors():
    """
    Opening the application to other web pages
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@route('/')
@jinja2_view('home.html', template_lookup=['views'])
def index():
    return {}

@route('/home')
@jinja2_view('home.html', template_lookup=['views'])
def home():
    return {}

@route('/documentation')
@jinja2_view('documentation.html', template_lookup=['views'])
def help():
    return {}

@route('/tutorial')
@jinja2_view('tutorial.html', template_lookup=['views'])
def tutorial():
    return {}

@route('/contact')
@jinja2_view('contact.html', template_lookup=['views'])
def contact():
    return {}


@route('/sitemap.xml')
def website_map():
    return static_file('sitemap.xml', root='./public/')


@route('/robots.txt')
def robots():
    return static_file('robots.txt', root='./public/')


@route('/google6f3b8a18c27a6939.html')
def google_verification():
    return static_file('google6f3b8a18c27a6939.html', root='./public/')


@route('/static/<filepath:path>')
def static_app_files(filepath):
    return static_file(filepath, root='./public/')


@route('/results/<filepath:path>')
def static_results(filepath):
    return static_file(filepath, root='/results/')



# opening database
open_object = open("/data/database/database_list.pickle", "rb")
database_list = pickle.load(open_object)
open_object.close()

# setting up general variables for the search function
exotic_punctuation = ["“", "”", "’", "‘", "—"]
cut_off_points = []


########################
# helper functions START
########################

# FUNCTION 1
# the function below returns a list of tuples - word_type, count. It is used in the regex search
def word_type_counts_list(some_list):
    types_dict = {}
    for word in some_list:
        if word in types_dict:
            types_dict[word] += 1
        else:
            types_dict[word] = 1
    results = sorted(types_dict.items(), key=operator.itemgetter(1), reverse=True)

    # # the code below for cutting the results displayed to a managable number...
    # types_found_number = len(results)
    # types_displayed = types_found_number
    # if types_found_number > 100:
    #     results = results[0:100]
    #     types_displayed = 100

    return results


# FUNCTION 2
# the function performs "normal search" in the main find_phrase function
def normal_search(user_expression, element, user_expression_length):
    single_result_dict = {}
    if user_expression in element[25]:
        cut_off_points = []
        element_length = len(element[25])
        element_expression_counter = 0
        for element_letter in element[25]:
            if user_expression[0] == element_letter:
                # this additional condition necessary to exclude cases of longer words containing the user
                # expression later, e.g. woman contains man - there were problems with this
                # if the word was not the first, but second or third...
                if element_expression_counter == 0:
                    if element_expression_counter + user_expression_length == element_length:
                        cut_off_points.append(element_expression_counter)
                        cut_off_points.append(element_expression_counter + user_expression_length)
                    elif user_expression == element[25][
                                            element_expression_counter:element_expression_counter + user_expression_length] and (
                            element[25][
                                element_expression_counter + user_expression_length] == " " or
                            element[25][
                                element_expression_counter + user_expression_length] in string.punctuation or
                            element[25][
                                element_expression_counter + user_expression_length] in exotic_punctuation):
                        cut_off_points.append(element_expression_counter)
                        cut_off_points.append(element_expression_counter + user_expression_length)
                # this additional condition necessary to exclude cases of longer words containing the user
                # expression later, e.g. woman contains man - there were problems with this if the word
                # was not the first, but second or third...
                elif element[25][element_expression_counter - 1] == ' ':
                    if element_expression_counter + user_expression_length == element_length:
                        cut_off_points.append(element_expression_counter)
                        cut_off_points.append(element_expression_counter + user_expression_length)
                    elif user_expression == element[25][
                                            element_expression_counter:element_expression_counter + user_expression_length] and (
                            element[25][
                                element_expression_counter + user_expression_length] == " " or
                            element[25][
                                element_expression_counter + user_expression_length] in string.punctuation or
                            element[25][
                                element_expression_counter + user_expression_length] in exotic_punctuation):
                        cut_off_points.append(element_expression_counter)
                        cut_off_points.append(element_expression_counter + user_expression_length)
            element_expression_counter += 1

        parts = []
        if len(cut_off_points) > 0:
            parts.append(element[14][:cut_off_points[0]])
            cut_off_points_counter = 1
            cut_off_points_length = len(cut_off_points)
            for cut_off_point in cut_off_points:
                if cut_off_points_counter < cut_off_points_length:
                    parts.append(element[14][cut_off_point:cut_off_points[cut_off_points_counter]])
                    cut_off_points_counter += 1

            parts.append(element[14][cut_off_points[cut_off_points_counter - 1]:])

            # this creates the json file - in the future I may add or remove some parts from this
            single_result_dict = {'section': str(element[2]),
                                  'author': str(element[3]),
                                  'novel': element[4],
                                  'chapter': element[5],
                                  'reader': str(element[6]),
                                  'readers_gender': element[7],
                                  'readers_dialect': element[8],
                                  'genre': element[9],
                                  'authors_gender': element[10],
                                  'audio_file_name': element[11],
                                  'textunit': element[14],
                                  'parts': parts,
                                  'alignment': element[16],
                                  'sentence_type': element[20],
                                  'context': element[21],
                                  'textunit_start': str(element[23]),
                                  'textunit_end': str(element[24]),
                                  'order_in_chapter': str(element[1])
                                  }
    return single_result_dict


def regex_search(database_list, user_expression, user_expression_regex, words_found_list, element):
    user_expression_compiled = re.compile(user_expression_regex)
    # the condition below checks if a regular expression appears in a string (which is without
    # without capital letters; earlier I used 13, which is without caps and punctuation)
    if re.search(user_expression_compiled, element[25]):
        word_found = re.findall(user_expression_compiled, element[25])
        # the line below changes word_found to be used to count textunits rather than tokens...
        word_found = list(set(word_found))
        if len(word_found) > 1:
            for word in word_found:
                words_found_list.append(word)
        else:
            words_found_list.append(word_found[0])

    return words_found_list


########################
# helper functions ENDED
########################
vowel = '[aeiouy]'
consonant = '[qwrtpsdfghjklzxcvbnm]'
pagination_bin_size = 25


@get('/search/<user_expression>/<filtering_data>/<database_indexes>')
def search_button(user_expression, filtering_data, database_indexes):
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
            index_counter += 5
        type_of_search = 'regex'

    if "QQ4" in user_expression:
        indices_list = [m.start() for m in re.finditer('QQ4', user_expression)]
        index_counter = 0
        for index in indices_list:
            user_expression = user_expression[:index + index_counter] + consonant + user_expression[
                                                                                    index + index_counter + 3:]
            index_counter += 19
        type_of_search = 'regex'

    # bottle stuff and other stuff...
    response.set_header('Origin', 'Poland')
    new_dict = {}
    next_search_start_index = 0

    # the search loop for 'mormal' cases which do not involve regex
    # 25 stands here for text units without caps - first search is done here to ged indices,
    # than the final parts are taken from 14, which is data_readable
    if type_of_search == 'normal':
        user_expression_length = len(user_expression)
        new_dict = {}
        textunit_counter = 0
        element_counter = 0

        if filtering_data_length == 5:
            for element in database_list:
                element_counter += 1
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1] \
                        and element[database_indexes[2]] == filtering_data[2] \
                        and element[database_indexes[3]] == filtering_data[3] \
                        and element[database_indexes[4]] == filtering_data[4]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=element,
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter

        elif filtering_data_length == 4:
            for element in database_list:
                element_counter += 1
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1] \
                        and element[database_indexes[2]] == filtering_data[2] \
                        and element[database_indexes[3]] == filtering_data[3]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=element,
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter

        elif filtering_data_length == 3:
            for element in database_list:
                element_counter += 1
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1] \
                        and element[database_indexes[2]] == filtering_data[2]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=element,
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter

        elif filtering_data_length == 2:
            for element in database_list:
                element_counter += 1
                if element[database_indexes[0]] == filtering_data[0] \
                        and element[database_indexes[1]] == filtering_data[1]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=element,
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter

        elif filtering_data_length == 1:
            for element in database_list:
                element_counter += 1
                if element[database_indexes[0]] == filtering_data[0]:
                    single_result_dict = normal_search(user_expression=user_expression,
                                                       element=element,
                                                       user_expression_length=user_expression_length)
                    if len(single_result_dict) > 0:
                        new_dict['result' + str(textunit_counter)] = single_result_dict
                        textunit_counter += 1
                        if textunit_counter == pagination_bin_size:
                            next_search_start_index = element_counter

        # for now only this case - later correct the above...
        elif filtering_data_length == 0:
            for element in database_list:
                element_counter += 1
                single_result_dict = normal_search(user_expression=user_expression,
                                                   element=element,
                                                   user_expression_length=user_expression_length)
                if len(single_result_dict) > 0:
                    new_dict['result' + str(textunit_counter)] = single_result_dict
                    textunit_counter += 1
                    # here is the problem - by adding a new "strange" key to the dictionary
                    if textunit_counter == pagination_bin_size:
                        next_search_start_index = element_counter

    # this is for regex searches
    elif type_of_search == 'regex':
        new_dict = {}
        # adding word boudary wildmarks to all words
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

    textunits_found_number = len(new_dict)
    # this is the way to slice the first "pagination_bin_size" chunk from the whole new_dict
    new_dict = dict(itertools.islice(new_dict.items(), pagination_bin_size))

    new_dict['pagination_bin_size'] = pagination_bin_size
    new_dict['previous_search_start_index'] = 0
    new_dict['next_search_start_index'] = next_search_start_index
    new_dict['textunits_found_number'] = textunits_found_number

    return new_dict


database_list_length = len(database_list)


# 'pagination_next_search_button'
@route('/next_button/<user_expression>/<filtering_data>/<database_indexes>/<previous_search_start_index>/'
       '<next_search_start_index>/<textunits_found_number>')
def next_button(user_expression, filtering_data, database_indexes, previous_search_start_index,
                next_search_start_index, textunits_found_number):
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
    print('after list previous_search_start_index: ', previous_search_start_index)

    # processing next_search_start_index string
    next_search_start_index = int(next_search_start_index)
    print(next_search_start_index)

    # processing next_search_start_index string
    textunits_found_number = int(textunits_found_number)
    print(textunits_found_number)

    print(type_of_search)
    # bottle stuff and other stuff...
    response.set_header('Origin', 'Poland')
    new_dict = {}

    # the search loop for 'mormal' cases which do not involve regex
    # 25 stands here for text units without caps - first search is done here to ged indices,
    # than the final parts are taken from 14, which is data_readable
    if type_of_search == 'normal':
        user_expression_length = len(user_expression)
        new_dict = {}
        textunit_counter = 0
        element_counter = next_search_start_index

        if filtering_data_length == 5:
            for index in range(next_search_start_index, database_list_length):
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
            for index in range(next_search_start_index, database_list_length):
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
            for index in range(next_search_start_index, database_list_length):
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
            for index in range(next_search_start_index, database_list_length):
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
            for index in range(next_search_start_index, database_list_length):
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
            for index in range(next_search_start_index, database_list_length):
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
        # adding word boudary wildmarks to all words
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
    new_dict['previous_search_start_index'] = previous_search_start_index
    new_dict['next_search_start_index'] = next_search_start_index
    new_dict['textunits_found_number'] = textunits_found_number

    return new_dict


# now 'pagination_previous_search_button'
@route('/previous_button/<user_expression>/<filtering_data>/<database_indexes>/<previous_search_start_index>/'
       '<next_search_start_index>/<textunits_found_number>')
def previous_button(user_expression, filtering_data, database_indexes, previous_search_start_index,
                    next_search_start_index, textunits_found_number):
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
    print('after list previous_search_start_index: ', previous_search_start_index)

    # processing next_search_start_index string
    next_search_start_index = int(next_search_start_index)
    print(next_search_start_index)

    # processing next_search_start_index string
    textunits_found_number = int(textunits_found_number)
    print(textunits_found_number)

    print(type_of_search)
    # bottle stuff and other stuff...
    response.set_header('Origin', 'Poland')
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
    print("next_search_start_index sent: ", next_search_start_index)
    new_dict['next_search_start_index'] = previous_search_start_index[-2]
    new_dict['textunits_found_number'] = textunits_found_number

    return new_dict


@route('/create_audio/<audio_file_name>/<textunit_start>/<textunit_duration>/<start_buffer>/<end_buffer>')
def crate_audio(audio_file_name, textunit_start, textunit_duration, start_buffer, end_buffer):
    resulting_audio_name = ''

    for filename in os.listdir("/data/audio"):
        if filename == audio_file_name + '.mp3':
            resulting_audio_name = datetime.now().strftime('%Y_%m_%d %H_%M_%S_%f') + '.mp3'
            ffmpeg_command = 'ffmpeg -ss ' + str(float(textunit_start) - float(start_buffer)) + ' -t ' + str(
                float(textunit_duration) + float(start_buffer) +
                float(end_buffer)) + ' -i ' + '/"data/audio/' + \
                filename + '" -c copy ' + '"' + '/results/' + resulting_audio_name + '"'

            os.system(ffmpeg_command.format(filename))
            break

    return {'resulting_audio_file': resulting_audio_name}
    # return static_file(resulting_audio_name, root='/results', download=filename)


@error(404)
def error404(error):
    return 'Nothing here, sorry'


run(host='0.0.0.0', reloader=True, port=8080, debug=True)


def delete_audio_files():
    list_of_audio_files = glob.glob('/results/*.mp3')
    for file in list_of_audio_files:
        # only these mp3 files will be removed which were created more than 5h ago (or 18000 seconds)
        # this may be changed to some other value in seconds, but the value in every() below should also be changed
        if time.time() - os.stat(file).st_mtime > 18000:
            os.remove(file)


schedule.every(5).hours.do(delete_audio_files)

while True:
    schedule.run_pending()
    time.sleep(1)
