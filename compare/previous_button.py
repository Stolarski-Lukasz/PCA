@csrf_exempt
def previous_button(request):
    return_value = request.POST.dict()
    user_expression = return_value['user_expression']
    filtering_data = return_value['filtering_data']
    database_indexes = return_value['database_indexes']
    
    user_expression = remove_punctuation(user_expression)
    pca_data_processor = PcaDataProcessor()
    filtering_data = pca_data_processor.process_filtering_data(filtering_data)
    database_indexes = pca_data_processor.process_database_indexes(database_indexes)

    previous_search_start_index = return_value['previous_search_start_index']
    next_search_start_index = return_value['next_search_start_index']
    textunits_found_number = return_value['textunits_found_number']

    previous_search_start_index = previous_search_start_index.split(',')
    previous_search_start_index = list(map(int, previous_search_start_index))
    next_search_start_index = int(next_search_start_index)
    textunits_found_number = int(textunits_found_number)
    
    user_expression_length = len(user_expression)
    new_dict = {}
    textunit_counter = 0
    element_counter = previous_search_start_index[-3]
    for index in range(previous_search_start_index[-3], database_list_length):
        element_counter += 1
        element_search_criteria = get_element_search_criteria(database_list[index], database_indexes, filtering_data)
        if element_search_criteria == filtering_data:
            normal_search_object = NormalSearch()
            cut_off_points = normal_search_object.get_cut_off_points(user_expression, database_list[index], user_expression_length)
            parts = normal_search_object.get_parts(database_list[index], cut_off_points)
            single_result_dict = normal_search_object.get_single_results_dict(database_list[index], parts, cut_off_points)
            # single_result_dict = normal_search(user_expression=user_expression,
            #                                    element=database_list[index],
            #                                    user_expression_length=user_expression_length)
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
    new_dict['previous_search_start_index'] = previous_search_start_index[:-2]
    new_dict['next_search_start_index'] = previous_search_start_index[-2]
    new_dict['textunits_found_number'] = textunits_found_number

    return JsonResponse(new_dict)
