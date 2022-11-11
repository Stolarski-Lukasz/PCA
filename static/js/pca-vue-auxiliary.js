/////////////////////////
// helper functions START
/////////////////////////

// HELPER FUNCTION 1
// the function takes an array of true/false values for filtering options - for now, the array is to store 18 values bacause there are 18 active filtering options
// it returns a string containing the options separated by "-"
// it is used for sending processed values which need to be filtered by backend

function return_checked_array(true_false_array) {
    let checked_array = [];

    if (true_false_array[0] == true) {
    }
    if (true_false_array[1] == true) {
        checked_array.push('narrator');
    }
    if (true_false_array[2] == true) {
        checked_array.push('dialogue');
    }
    if (true_false_array[3] == true) {
    }
    if (true_false_array[4] == true) {
        checked_array.push('statement_or_directive');
    }
    if (true_false_array[5] == true) {
        checked_array.push('question');
    }
    if (true_false_array[6] == true) {
        checked_array.push('exclamative_statement');
    }
    if (true_false_array[7] == true) {
    }
    if (true_false_array[8] == true) {
        checked_array.push('reader_f');
    }
    if (true_false_array[9] == true) {
        checked_array.push('reader_m');
    }
    if (true_false_array[10] == true) {
    }
    if (true_false_array[11] == true) {
        checked_array.push('bre');
    }
    if (true_false_array[12] == true) {
        checked_array.push('ame');
    }
    if (true_false_array[13] == true) {
        checked_array.push('aus');
    }
    if (true_false_array[14] == true) {
        checked_array.push('non_native');
    }
    if (true_false_array[15] == true) {
    }
    if (true_false_array[16] == true) {
        checked_array.push('author_f');
    }
    if (true_false_array[17] == true) {
        checked_array.push('author_m');
    }
    return checked_array;
};

// HELPER FUNCTION 2 - !!!MAKE CHANGES HERE IF DATABASE STRUCTURE HAS BEEN ALTERED!!!
// the function takes the array of values returned by HELPER FUNCTION 1
// it returns an array of indexes used in backend search through database
function return_database_indexes_array(checked_array) {
    let database_indexes = [];
    checked_array.forEach(function (filtering_value) {
        if (filtering_value == 'dialogue' || filtering_value == 'narrator') {
            database_indexes.push(21);
        }
        else if (filtering_value == 'statement_or_directive' || filtering_value == 'question' || filtering_value == 'exclamative_statement') {
            database_indexes.push(20);
        }
        else if (filtering_value == 'reader_f' || filtering_value == 'reader_m') {
            database_indexes.push(7);
        }
        else if (filtering_value == 'bre' || filtering_value == 'ame' || filtering_value == 'aus' || filtering_value == 'non_native') {
            database_indexes.push(8);
        }
        else if (filtering_value == 'author_f' || filtering_value == 'author_m') {
            database_indexes.push(10);
        }
    })
    return database_indexes;
};


// HELPER FUNCTION 3
// the function takes the array of values returned by HELPER FUNCTION 1
// transforms the array of checked values into a string with the values separated by "-"
// 'reader_f', 'reader_m', 'author_f' and 'author_m' are changed back to 'f' and 'm'

function return_checked_string(checked_array) {
    let checked_string = '';

    // this if condition necessary to give Python info to create an empty list for filtering_data
    if (checked_array.length == 0) {
        checked_string = 'all';
    }

    else {
        let checked_string_counter = 0;
        checked_array.forEach(function (filtering_value) {
            if (checked_string_counter < checked_array.length - 1) {
                if (filtering_value == 'reader_f' || filtering_value == 'author_f') {
                    checked_string += 'f-';
                    checked_string_counter += 1;
                } else if (filtering_value == 'reader_m' || filtering_value == 'author_m') {
                    checked_string += 'm-';
                    checked_string_counter += 1;
                } else {
                    checked_string += filtering_value + '-';
                    checked_string_counter += 1;
                }
            } else {
                if (filtering_value === 'reader_f' || filtering_value === 'author_f') {
                    checked_string += 'f';
                } else if (filtering_value === 'reader_m' || filtering_value === 'author_m') {
                    checked_string += 'm';
                } else {
                    checked_string += filtering_value;
                }
            }

        })
    }
    return checked_string;
};


// HELPER FUNCTION 4
// the function takes the array of values returned by HELPER FUNCTION 2
// transforms the array of database indexes into a string with the values separated by "-"

function return_database_index_string(database_indexes) {
    let database_indexes_string = '';

    if (database_indexes.length === 0) {
        database_indexes_string = 'all'
    }

    else {
        let database_indexes_string_counter = 0;
        database_indexes.forEach(function (database_index) {
            if (database_indexes_string_counter < database_indexes.length - 1) {
                database_indexes_string += database_index + '-';
                database_indexes_string_counter += 1;
            }
            else {
                database_indexes_string += database_index;
            }
        })
    }
    return database_indexes_string;
};


// HELPER FUNCTION 5
// the function takes the original user imput and outputs the string with properly transformed pca wildcards to Python regex values

function pcawildcards_to_pythonregex(user_search_field_value_original) {
    let user_search_field_value = user_search_field_value_original.toLowerCase();

    // translating PCLA wildcards into python regular expression wildcards
    for (let letter_counter = 0; letter_counter < user_search_field_value.length; letter_counter++) {
        if (user_search_field_value[letter_counter] == "=") {
            user_search_field_value = user_search_field_value.replace(/\=v/g, 'QQ3');
        }
    };

    for (let letter_counter = 0; letter_counter < user_search_field_value.length; letter_counter++) {
        if (user_search_field_value[letter_counter] == "=") {
            user_search_field_value = user_search_field_value.replace(/\=c/g, 'QQ4');
        }
    };

    for (let letter_counter = 0; letter_counter < user_search_field_value.length; letter_counter++) {
        if (user_search_field_value[letter_counter] == "?") {
            user_search_field_value = user_search_field_value.replace(/\?/g, 'QQ1');
        }
    };

    for (let letter_counter = 0; letter_counter < user_search_field_value.length; letter_counter++) {
        if (user_search_field_value[letter_counter] == "*") {
            user_search_field_value = user_search_field_value.replace(/\*/g, 'QQ2');
        }
    };
    return user_search_field_value
};


function generate_results_array(response_object) {
    // two counters, because one counts all examples, another to obtain the name of the key...
    let results_counter = 0;
    let result_name_counter = 0;
    let results_array3 = [];
    let results_array2 = [];
    for (let result in response_object) {
        if (Object.keys(response_object)[results_counter] != 'previous_search_start_index' && Object.keys(response_object)[results_counter] != 'next_search_start_index' && Object.keys(response_object)[results_counter] != 'pagination_bin_size' && Object.keys(response_object)[results_counter] != 'textunits_found_number') {
            let upto3_counter = 1
            results_array2 = []
            let results_array1 = []
            for (let index in response_object['result' + result_name_counter].parts) {
                // this is for even numbers - not keywords
                if (index % 2 == 0) {
                    results_array1.push(response_object['result' + result_name_counter].parts[index])
                    // this is for odd numbers - kyewords
                } else {
                    if (results_array1.length == 0) {
                        results_array1.push("")
                        results_array1.push(response_object['result' + result_name_counter].parts[index])
                        upto3_counter++
                    } else {
                        results_array1.push(response_object['result' + result_name_counter].parts[index])
                    }
                }
                upto3_counter += 1
                if (upto3_counter == 4) {
                    results_array2.push(results_array1)
                    results_array1 = []
                    upto3_counter = 1
                }
            }
            results_counter += 1;
            result_name_counter += 1;
            results_array3.push(results_array2)
        }
        else {
            results_counter += 1;
        }
    }
    return results_array3
}

function add_custom_dropdowns() {
    //creating drop-down selectors START
    ////////////////////////////////////
    var x, i, j, selElmnt, a, b, c;
    /*look for any elements with the class "custom-select":*/
    x = document.getElementsByClassName("custom-select");
    for (i = 0; i < x.length; i++) {
        selElmnt = x[i].getElementsByTagName("select")[0];
        /*for each element, create a new DIV that will act as the selected item:*/
        a = document.createElement("DIV");
        a.setAttribute("class", "select-selected");
        a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
        x[i].appendChild(a);
        /*for each element, create a new DIV that will contain the option list:*/
        b = document.createElement("DIV");
        b.setAttribute("class", "select-items select-hide");
        for (j = 1; j < selElmnt.length; j++) {
            /*for each option in the original select element,
            create a new DIV that will act as an option item:*/
            c = document.createElement("DIV");
            c.innerHTML = selElmnt.options[j].innerHTML;
            c.addEventListener("click", function (e) {
                /*when an item is clicked, update the original select box,
                and the selected item:*/
                var y, i, k, s, h;
                s = this.parentNode.parentNode.getElementsByTagName("select")[0];
                h = this.parentNode.previousSibling;
                for (i = 0; i < s.length; i++) {
                    if (s.options[i].innerHTML == this.innerHTML) {
                        s.selectedIndex = i;
                        h.innerHTML = this.innerHTML;
                        y = this.parentNode.getElementsByClassName("same-as-selected");
                        for (k = 0; k < y.length; k++) {
                            y[k].removeAttribute("class");
                        }
                        this.setAttribute("class", "same-as-selected");
                        break;
                    }
                }
                h.click();
            });
            b.appendChild(c);
        }
        x[i].appendChild(b);
        a.addEventListener("click", function (e) {
            /*when the select box is clicked, close any other select boxes,
            and open/close the current select box:*/
            e.stopPropagation();
            closeAllSelect(this);
            this.nextSibling.classList.toggle("select-hide");
            this.classList.toggle("select-arrow-active");
        });
    }

    function closeAllSelect(elmnt) {
        /*a function that will close all select boxes in the document,
        except the current select box:*/
        var x, y, i, arrNo = [];
        x = document.getElementsByClassName("select-items");
        y = document.getElementsByClassName("select-selected");
        for (i = 0; i < y.length; i++) {
            if (elmnt == y[i]) {
                arrNo.push(i)
            } else {
                y[i].classList.remove("select-arrow-active");
            }
        }
        for (i = 0; i < x.length; i++) {
            if (arrNo.indexOf(i)) {
                x[i].classList.add("select-hide");
            }
        }
    }
    /*if the user clicks anywhere outside the select box,
    then close all select boxes:*/
    document.addEventListener("click", closeAllSelect);
}

function add_data_to_pagination_previous_button_atstart(
    pagination_previous_buttons,
    user_search_field_value,
    response_object) {
    Array.from(pagination_previous_buttons).forEach(function (pagination_previous_button) {
        pagination_previous_button.setAttribute('data-user-search-term', user_search_field_value);
        pagination_previous_button.setAttribute('data-previous-search-start-index', response_object['previous_search_start_index'] + ',' + response_object['next_search_start_index']);
        pagination_previous_button.setAttribute('data-next-search-start-index', response_object['next_search_start_index']);
        pagination_previous_button.setAttribute('data-textunits-found-number', response_object.textunits_found_number);
        pagination_previous_button.setAttribute('data-results-showing-start', 1);
        pagination_previous_button.setAttribute('data-results-showing-end', response_object['pagination_bin_size']);
        pagination_previous_button.setAttribute('data-status', 'inactive');
        pagination_previous_button.setAttribute('data-type', 'previous');
    })
}

function add_data_to_pagination_next_button_atstart(
    pagination_next_buttons,
    user_search_field_value,
    response_object) {
    Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
        pagination_next_button.disabled = false;
        pagination_next_button.setAttribute('data-user-search-term', user_search_field_value);
        pagination_next_button.setAttribute('data-previous-search-start-index', response_object['previous_search_start_index'] + ',' + response_object['next_search_start_index']);
        pagination_next_button.setAttribute('data-next-search-start-index', response_object['next_search_start_index']);
        pagination_next_button.setAttribute('data-textunits-found-number', response_object.textunits_found_number);
        pagination_next_button.setAttribute('data-results-showing-start', 1);
        pagination_next_button.setAttribute('data-results-showing-end', response_object['pagination_bin_size']);
        pagination_next_button.setAttribute('data-type', 'next');
    })
    if (response_object.pagination_bin_size >= response_object.textunits_found_number) {
        Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
            pagination_next_button.disabled = true;
        })
    }
}

function add_data_to_pagination_previous_button(
    pagination_previous_buttons,
    user_search_field_value,
    response_object,
    results_showing_start,
    results_showing_end) {
    Array.from(pagination_previous_buttons).forEach(function (pagination_previous_button) {
        pagination_previous_button.setAttribute(
            'data-user-search-term', user_search_field_value)
        pagination_previous_button.setAttribute(
            'data-previous-search-start-index', response_object['previous_search_start_index'] + ',' + response_object['next_search_start_index'])
        pagination_previous_button.setAttribute(
            'data-next-search-start-index', response_object['next_search_start_index'])
        pagination_previous_button.setAttribute(
            'data-textunits-found-number', response_object.textunits_found_number)
        pagination_previous_button.setAttribute(
            'data-results-showing-start', results_showing_start)
        pagination_previous_button.setAttribute(
            'data-results-showing-end', results_showing_end)
        pagination_previous_button.setAttribute('data-type', 'previous')
    })
}

function add_data_to_pagination_next_button(
    pagination_next_buttons,
    user_search_field_value,
    response_object,
    results_showing_start,
    results_showing_end) {
    Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
        pagination_next_button.setAttribute(
            'data-user-search-term', user_search_field_value)
        pagination_next_button.setAttribute('data-previous-search-start-index',
            response_object['previous_search_start_index'] + ',' + response_object['next_search_start_index'])
        pagination_next_button.setAttribute(
            'data-next-search-start-index', response_object['next_search_start_index'])
        pagination_next_button.setAttribute(
            'data-textunits-found-number', response_object.textunits_found_number)
        pagination_next_button.setAttribute(
            'data-results-showing-start', results_showing_start)
        pagination_next_button.setAttribute(
            'data-results-showing-end', results_showing_end)
        pagination_next_button.setAttribute('data-type', 'next')
    })
}

function generate_vue_regex_array(response_object) {
    let results_counter = 0
    let regex_results_array2 = []
    for (let counter = 0; counter < response_object['result'].list_of_tuples.length; counter++) {
        let some_result = response_object['result'].list_of_tuples[results_counter];
        let regex_results_array1 = []
        regex_results_array1.push(some_result[1])
        regex_results_array1.push(some_result[0])
        regex_results_array2.push(regex_results_array1)
        results_counter += 1;
    }
    return regex_results_array2
}

function generate_vue_regex_array_1000(response_object) {
    let results_counter = 0
    let regex_results_array2 = []
    for (let counter = 0; counter<1000; counter++) {
        let some_result = response_object['result'].list_of_tuples[results_counter];
        let regex_results_array1 = []
        regex_results_array1.push(some_result[1])
        regex_results_array1.push(some_result[0])
        regex_results_array2.push(regex_results_array1)
        results_counter += 1;
    }
    return regex_results_array2
}

function add_data_to_regex_results(response_object) {
    let regex_results_htmlcollection = document.getElementsByClassName('regex_result');
    let data_insertion_counter = 0
    Array.from(regex_results_htmlcollection).forEach(function (regex_result) {
        regex_result.setAttribute('data-search-term', response_object['result'].list_of_tuples[data_insertion_counter][0]);
        data_insertion_counter += 1
    });
}

function remove_action_icons_boxshawdow() {
    let results_icon_info_buttons = document.getElementsByClassName('pca-results-icon-info');
    Array.from(results_icon_info_buttons).forEach(function (results_icon_info_button) {
        results_icon_info_button.style.boxShadow = "none"
    })
    let results_icon_play_buttons = document.getElementsByClassName('pca-results-icon-play');
    Array.from(results_icon_play_buttons).forEach(function (results_icon_play_button) {
        results_icon_play_button.style.boxShadow = "none"
    })
    let results_icon_download_buttons = document.getElementsByClassName('pca-results-icon-download');
    Array.from(results_icon_download_buttons).forEach(function (results_icon_download_button) {
        results_icon_download_button.style.boxShadow = "none"
    })
}

function add_data_to_info_icon(response_object) {
    let results_icon_info_buttons = document.getElementsByClassName('pca-results-icon-info');
    let result_name_counter = 0
    Array.from(results_icon_info_buttons).forEach(function (results_icon_info_button) {
        results_icon_info_button.setAttribute('data-author', response_object['result' + result_name_counter].author);
        results_icon_info_button.setAttribute('data-authors-gender', response_object['result' + result_name_counter].authors_gender);
        results_icon_info_button.setAttribute('data-novel', response_object['result' + result_name_counter].novel);
        results_icon_info_button.setAttribute('data-chapter', response_object['result' + result_name_counter].chapter);
        results_icon_info_button.setAttribute('data-chapter-number', response_object['result' + result_name_counter].section);
        results_icon_info_button.setAttribute('data-reader', response_object['result' + result_name_counter].reader);
        results_icon_info_button.setAttribute('data-readers-gender', response_object['result' + result_name_counter].readers_gender);
        results_icon_info_button.setAttribute('data-readers-dialect', response_object['result' + result_name_counter].readers_dialect);
        results_icon_info_button.setAttribute('data-context', response_object['result' + result_name_counter].context);
        results_icon_info_button.setAttribute('data-text-function', response_object['result' + result_name_counter].sentence_type);
        results_icon_info_button.setAttribute('data-audio-file-name', response_object['result' + result_name_counter].audio_file_name);
        results_icon_info_button.setAttribute('data-textunit-start', response_object['result' + result_name_counter].textunit_start);
        results_icon_info_button.setAttribute('data-textunit-end', response_object['result' + result_name_counter].textunit_end);
        results_icon_info_button.setAttribute('data-order-in-chapter', response_object['result' + result_name_counter].order_in_chapter);
        result_name_counter++
    })
}

function remove_audio_player(response_object) {
    let holder = document.querySelector('.holder')
    if (holder) {holder.parentNode.removeChild(holder)}
    let controls = document.querySelector('.controls')
    if (controls) {controls.parentNode.removeChild(controls)}
    let volume = document.querySelector('.volume')
    if (volume) {volume.parentNode.removeChild(volume)}
    let download = document.querySelector('.download')
    if (download) {download.parentNode.removeChild(download)}
}

export {
    return_checked_array,
    return_database_indexes_array,
    return_checked_string,
    return_database_index_string,
    pcawildcards_to_pythonregex,
    generate_results_array,
    add_custom_dropdowns,
    add_data_to_pagination_previous_button_atstart,
    add_data_to_pagination_next_button_atstart,
    add_data_to_pagination_previous_button,
    add_data_to_pagination_next_button,
    generate_vue_regex_array,
    generate_vue_regex_array_1000,
    add_data_to_regex_results,
    remove_action_icons_boxshawdow,
    add_data_to_info_icon,
    remove_audio_player
}