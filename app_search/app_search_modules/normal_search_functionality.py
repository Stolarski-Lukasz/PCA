import string
exotic_punctuation = ["“", "”", "’", "‘", "—"]


class NormalSearch():

    user_expression_in_element = False

    def get_cut_off_points(self, user_expression, element, user_expression_length):
        cut_off_points = []
        if user_expression in element[25]:
            self.user_expression_in_element = True
            element_length = len(element[25])
            element_expression_counter = 0
            for element_letter in element[25]:
                if user_expression[0] == element_letter:
                    if element_expression_counter == 0 or element[25][element_expression_counter - 1] == ' ':
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
        return cut_off_points


    def get_parts(self, element, cut_off_points):
        parts = []
        if self.user_expression_in_element and cut_off_points:
            parts.append(element[14][:cut_off_points[0]])
            cut_off_points_counter = 1
            cut_off_points_length = len(cut_off_points)
            for cut_off_point in cut_off_points:
                if cut_off_points_counter < cut_off_points_length:
                    parts.append(element[14][cut_off_point:cut_off_points[cut_off_points_counter]])
                    cut_off_points_counter += 1

            parts.append(element[14][cut_off_points[cut_off_points_counter - 1]:])
        return parts


    def get_single_results_dict(self, element, parts, cut_off_points):
        single_result_dict = {}
        if self.user_expression_in_element and cut_off_points:
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

