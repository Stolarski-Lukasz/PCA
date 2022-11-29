import re
import operator

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
