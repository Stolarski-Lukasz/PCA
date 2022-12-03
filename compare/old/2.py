if "QQ1" in user_expression:
            indices_list = [m.start() for m in re.finditer('QQ1', user_expression)]
            index_counter = 0
            for index in indices_list:
                user_expression = user_expression[:index - index_counter] + '\w' + user_expression[
                                                                                index - index_counter + 3:]
                index_counter += 1
            self.type_of_search = 'regex'
