import string
exotic_punctuation = ["“", "”", "’", "‘", "—"]


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



