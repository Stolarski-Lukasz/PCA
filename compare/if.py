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
