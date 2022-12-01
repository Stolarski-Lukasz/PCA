import re
import operator


class RegexSearch():

    def add_word_boundaries(self, user_expression):
        user_expression_list = user_expression.split()
        correct_user_expression_list = []
        for word in user_expression_list:
            correct_word = "\\b" + word + "\\b"
            correct_user_expression_list.append(correct_word)
        user_expression_regex = " ".join(correct_user_expression_list)
        return user_expression_regex


    def get_word_type_counts_list(self, some_list):
        """
        Returns:
            a list of tuples: returns a list of tuples - word_type, count. It is used in the regex search
        """
        types_dict = {}
        for word in some_list:
            if word in types_dict:
                types_dict[word] += 1
            else:
                types_dict[word] = 1
        results = sorted(types_dict.items(), key=operator.itemgetter(1), reverse=True)
        return results


    def regex_search(self, user_expression_regex, words_found_list, element):
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


