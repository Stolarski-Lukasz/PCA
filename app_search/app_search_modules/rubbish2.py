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