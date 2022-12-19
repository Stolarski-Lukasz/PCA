import string

class NormalSearch:
    user_expression_in_element = False

    def get_cut_off_points(self, user_expression, element, user_expression_length):
        cut_off_points = []
        if user_expression in element[25]:
            self.user_expression_in_element = True
            element_length = len(element[25])
            element_expression_counter = 0
            for element_letter in element[25]:
                if user_expression[0] == element_letter:
                    # Check if user expression is at the beginning of the element
                    if element_expression_counter == 0:
                        # Check if user expression is at the end of the element
                        if element_expression_counter + user_expression_length == element_length:
                            cut_off_points.append(element_expression_counter)
                            cut_off_points.append(element_expression_counter + user_expression_length)
                        # Check if user expression is followed by a space or punctuation
                        elif user_expression == element[25][element_expression_counter:element_expression_counter + user_expression_length] and (
                                element[25][element_expression_counter + user_expression_length] == " " or
                                element[25][element_expression_counter + user_expression_length] in string.punctuation or
                                element[25][element_expression_counter + user_expression_length] in exotic_punctuation):
                            cut_off_points.append(element_expression_counter)
                            cut_off_points.append(element_expression_counter + user_expression_length)
                    # Check if user expression is preceded by a space
                    elif element[25][element_expression_counter - 1] == ' ':
                        # Check if user expression is at the end of the element
                        if element_expression_counter + user_expression_length == element_length:
                            cut_off_points.append(element_expression_counter)
                            cut_off_points.append(element_expression_counter + user_expression_length)
                        # Check if user expression is followed by a space or punctuation
                        elif user_expression == element[25][element_expression_counter:element_expression_counter + user_expression_length] and (
                                element[25][element_expression_counter + user_expression_length] == " " or
                                element[25][element_expression_counter + user_expression_length] in string.punctuation or
                                element[25][element_expression_counter + user_expression_length] in exotic_punctuation):
                            cut_off_points.append(element_expression_counter)
                            cut_off_points.append(element_expression_counter + user_expression_length)
                element_expression_counter += 1
        return cut_off_points