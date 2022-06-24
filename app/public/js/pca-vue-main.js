import {
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
} from "./pca-vue-auxiliary.js"


const vue_app = Vue.createApp({
  data() {
    return {
      searching: false,
      results_morethanzero: false,
      results_regex: false,
      results_zero: false,
      results_arrayofarrays: [[["Text before1", "keyword1", "text after1"]], [["Text before2", "keyword2", "text after2"], ["", "keyword3", ""]]],
      regex_results_heading: "",
      regex_results_data: [],
      pagination_info_data: "",
      regex_hover: false,
      author: "",
      aurthors_gender: "",
      novel: "",
      chapter_title: "",
      chapter_number: "",
      reader: "",
      readers_gender: "",
      readers_dialect: "",
      context: "",
      text_function: "",
      audio_start_in_chapter: "",
      audio_finish_in_chapter: ""
    }
  },
  delimiters: ["${", "}$"],
  methods: {
    search(event) {
      // deactivating active link in the menu
      let navigation_links = document.getElementsByClassName('nav-link');
      Array.from(navigation_links).forEach(function (item) {
        item.className = "nav-link"
      })

      // Getting user input values
      let user_search_field_value
      if (event.target.className == "regex_result") {
        user_search_field_value = event.target.dataset.searchTerm
      } else {
        let pca_search_input = document.getElementById('pca-search-input')
        let user_search_field_value_original = pca_search_input.value;
        user_search_field_value = pcawildcards_to_pythonregex(user_search_field_value_original)
      }

      // preparing filtering values to be sent to server - helper functions are used here
      let all_checkboxes_series = document.querySelectorAll('.checkboxes_series');
      let check_state_array_2 = [];
      all_checkboxes_series.forEach(function (checkbox) {
        check_state_array_2.push(checkbox.checked);
      })
      let checked_array = return_checked_array(check_state_array_2);
      let database_indexes_array = return_database_indexes_array(checked_array);
      let checked_string = return_checked_string(checked_array);
      let database_indexes_string = return_database_index_string(database_indexes_array);

      // sending a GET request
      var comp = this;
      let xhr = new XMLHttpRequest();
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          comp.searching = false
          let json_response = xhr.responseText;
          let response_object = JSON.parse(json_response);

          // this if else statement is for displaying results if there are any, and displaying "No matches were found" otherwise
          if (Object.keys(response_object).length > 4) {

            // this if for intermediate results of regex searches
            if (Object.keys(response_object)[0] == 'result') {

              // this is for cases with less than 1000 types
              if (response_object['result'].list_of_tuples.length < 1001) {
                // general Vue DOM manipulation
                comp.results_morethanzero = false
                comp.results_regex = true

                // Vue regex_results_heading
                comp.regex_results_heading = response_object['result'].list_of_tuples.length + ' types were found:'

                // Vue regex_results
                comp.regex_results_data = generate_vue_regex_array(response_object)

                Vue.nextTick(function () {
                  add_data_to_regex_results(response_object)
                })
              }
              // this is for cases with more than 1000 types
              else {
                // general Vue DOM manipulation
                comp.results_morethanzero = false
                comp.results_regex = true

                // Vue regex_results_heading
                comp.regex_results_heading = response_object['result'].list_of_tuples.length + ' types were found (showing the first 1000):'

                // Vue regex_results
                comp.regex_results_data = generate_vue_regex_array_1000(response_object)

                Vue.nextTick(function () {
                  add_data_to_regex_results(response_object)
                })
              }
              // "normal" search
            } else {
              let results_array3 = generate_results_array(response_object)
              comp.results_arrayofarrays = results_array3
              comp.results_morethanzero = true

              Vue.nextTick(function () {
                // to prevent autoplay of previously activated audio after searching in some cases
                let audio_element = document.querySelector("#audio_element")
                audio_element.pause();
                audio_element.currentTime = 0;

                //creating custom drop-down selectors
                let select_selected_elements = document.getElementsByClassName('select-selected');
                let select_items_elements = document.getElementsByClassName('select-items');
                if (select_selected_elements.length > 0) {
                  Array.from(select_selected_elements).forEach(function (item) {
                    item.parentNode.removeChild(item);
                  });
                  Array.from(select_items_elements).forEach(function (item) {
                    item.parentNode.removeChild(item);
                  });
                  add_custom_dropdowns()
                } else {
                  add_custom_dropdowns()
                }

                // adding data to pagination buttons
                let pagination_previous_buttons = document.getElementsByClassName("pagination_previous_button")
                add_data_to_pagination_previous_button_atstart(pagination_previous_buttons, user_search_field_value, response_object)
                let pagination_next_buttons = document.getElementsByClassName("pagination_next_button")
                add_data_to_pagination_next_button_atstart(pagination_next_buttons, user_search_field_value, response_object)

                // pagination info.
                let pagination_info;
                if (response_object.pagination_bin_size <= response_object.textunits_found_number) {
                  pagination_info = 1 + '-' + response_object.pagination_bin_size + ' / ' + response_object.textunits_found_number;
                  Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
                    pagination_next_button.setAttribute('data-status', 'active');
                  })
                } else {
                  pagination_info = 1 + '-' + response_object.textunits_found_number + ' / ' + response_object.textunits_found_number;
                  Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
                    pagination_next_button.setAttribute('data-status', 'inactive');
                  })

                }
                comp.pagination_info_data = pagination_info

                // resetting action icons and dropdowns
                remove_action_icons_boxshawdow()
                Array.from(select_selected_elements).forEach(function (item) {
                  item.innerHTML = "0";
                })

                add_data_to_info_icon(response_object)

              })
            }
          } else {
            comp.results_morethanzero = false
            comp.results_regex = false
            comp.results_zero = true
          }
        }
      };

      comp.searching = true
      xhr.open('GET', '/search/' + user_search_field_value + '/' + checked_string + '/' + database_indexes_string, true);
      xhr.send();
    },
    pagination(event) {
      // Getting user input values from pagination buttons - the if statement for both clicking the button and the sign inside the buton
      let user_search_field_value_original_frompaginationbutton = event.target.dataset.userSearchTerm
      let user_search_field_value_frompaginationbutton = pcawildcards_to_pythonregex(user_search_field_value_original_frompaginationbutton)

      // preparing filtering values to be sent to server - here helper functions are used
      let all_checkboxes_series = document.querySelectorAll('.checkboxes_series');
      let check_state_array_2 = [];
      all_checkboxes_series.forEach(function (checkbox) {
        check_state_array_2.push(checkbox.checked);
      })
      let checked_array = return_checked_array(check_state_array_2);
      let database_indexes_array = return_database_indexes_array(checked_array);
      let checked_string = return_checked_string(checked_array);
      let database_indexes_string = return_database_index_string(database_indexes_array);

      // sending a GET request
      var comp = this;
      let xhr = new XMLHttpRequest();
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          let json_response = xhr.responseText;
          let response_object = JSON.parse(json_response);

          // this if else statement is for displaying results if there are any, and displaying "No matches were found" otherwise
          if (Object.keys(response_object).length > 4) {
            let results_array3 = generate_results_array(response_object)
            comp.results_arrayofarrays = results_array3
            comp.results_morethanzero = true

            Vue.nextTick(function () {
              //creating custom drop-down selectors
              let select_selected_elements = document.getElementsByClassName('select-selected');
              let select_items_elements = document.getElementsByClassName('select-items');
              if (select_selected_elements.length > 0) {
                Array.from(select_selected_elements).forEach(function (item) {
                  item.parentNode.removeChild(item);
                });
                Array.from(select_items_elements).forEach(function (item) {
                  item.parentNode.removeChild(item);
                });
                add_custom_dropdowns()
              } else {
                add_custom_dropdowns()
              }

              // setting up dynamic 'data-results-showing-start' and 'data-results-showing-end'
              // deducting for pagination_previous_button and adding for pagination_next_button
              let results_showing_start
              let results_showing_end

              if (event.target.dataset.type == 'previous') {
                results_showing_start = parseFloat(
                  event.target.dataset.resultsShowingStart) - parseFloat(response_object.pagination_bin_size)
                results_showing_end = parseFloat(
                  event.target.dataset.resultsShowingEnd) - parseFloat(response_object.pagination_bin_size)
              } else {
                results_showing_start = parseFloat(
                  event.target.dataset.resultsShowingStart) + parseFloat(response_object.pagination_bin_size)
                results_showing_end = parseFloat(
                  event.target.dataset.resultsShowingEnd) + parseFloat(response_object.pagination_bin_size)
              }

              // adding data to pagination buttons
              let pagination_previous_buttons = document.getElementsByClassName("pagination_previous_button")
              add_data_to_pagination_previous_button(
                pagination_previous_buttons,
                user_search_field_value_frompaginationbutton,
                response_object,
                results_showing_start,
                results_showing_end)
              let pagination_next_buttons = document.getElementsByClassName("pagination_next_button")
              add_data_to_pagination_next_button(
                pagination_next_buttons,
                user_search_field_value_frompaginationbutton,
                response_object,
                results_showing_start,
                results_showing_end)

              let pagination_info
              // this if statement deals with results smaller than pagination_bin_size(they are coped with in the else statement - then both pagination_previous_button and pagination_next_button are set to inactive)
              if (response_object.pagination_bin_size <= response_object.textunits_found_number) {
                // pagination_prevous_button - setting it to active if results_showing_start != 0, otherwise setting it to inactive
                if (results_showing_start == 1) {
                  Array.from(pagination_previous_buttons).forEach(function (pagination_previous_button) {
                    pagination_previous_button.setAttribute('data-status', 'inactive')
                    pagination_previous_button.disabled = true
                  })
                } else {
                  Array.from(pagination_previous_buttons).forEach(function (pagination_previous_button) {
                    pagination_previous_button.setAttribute('data-status', 'active')
                    pagination_previous_button.disabled = false
                  })
                }

                // pagination_next_button - this if statement deals with the cases in which results shown is already the maximum results found
                if (results_showing_end >= response_object.textunits_found_number) {
                  pagination_info = results_showing_start + '-' +
                    response_object.textunits_found_number + ' / ' +
                    response_object.textunits_found_number

                  Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
                    pagination_next_button.setAttribute('data-status', 'inactive')
                    pagination_next_button.disabled = true
                  })
                } else {
                  pagination_info = results_showing_start + '-' + results_showing_end +
                    ' / ' + response_object.textunits_found_number
                  Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
                    pagination_next_button.setAttribute('data-status', 'active')
                    pagination_next_button.disabled = false
                  })
                }
              } else {
                pagination_info = 1 + '-' + response_object.textunits_found_number +
                  ' / ' + response_object.textunits_found_number

                Array.from(pagination_previous_buttons).forEach(function (pagination_previous_button) {
                  pagination_previous_button.setAttribute('data-status', 'inactive')
                  pagination_previous_button.disabled = true
                })

                Array.from(pagination_next_buttons).forEach(function (pagination_next_button) {
                  pagination_next_button.setAttribute('data-status', 'inactive')
                  pagination_next_button.disabled = true
                })
              }
              comp.pagination_info_data = pagination_info

              // resetting action icons and dropdowns
              remove_action_icons_boxshawdow()
              Array.from(select_selected_elements).forEach(function (item) {
                item.innerHTML = "0";
              })

              add_data_to_info_icon(response_object)

            })
          } else {
            comp.results_morethanzero = false
            comp.results_zero = true
          }
        }
      };

      // preparing pagination string data and sending the request START
      let previous_search_start_index = event.target.dataset.previousSearchStartIndex;
      let next_search_start_index = event.target.dataset.nextSearchStartIndex;
      let textunits_found_number = event.target.dataset.textunitsFoundNumber;
      let pagination_button_type = event.target.dataset.type

      // the if statement checks which of the two buttons was clicked and then it sends the right request
      if (pagination_button_type == 'previous') {
        xhr.open('GET', '/previous_button/' + user_search_field_value_frompaginationbutton + '/' + checked_string + '/' + database_indexes_string + '/' + previous_search_start_index + '/' + next_search_start_index + '/' + textunits_found_number, true);
        xhr.send();
      }
      else if (pagination_button_type == 'next') {
        xhr.open('GET', '/next_button/' + user_search_field_value_frompaginationbutton + '/' + checked_string + '/' + database_indexes_string + '/' + previous_search_start_index + '/' + next_search_start_index + '/' + textunits_found_number, true);
        xhr.send();
      }
    },
    get_info(event) {
      event.target.style.boxShadow = "0 0 0 3px #81b441"
      this.author = event.target.dataset.author
      this.authors_gender = event.target.dataset.authorsGender
      this.novel = event.target.dataset.novel
      this.chapter_title = event.target.dataset.chapter
      this.chapter_number = event.target.dataset.chapterNumber
      this.reader = event.target.dataset.reader
      this.readers_gender = event.target.dataset.readersGender
      this.readers_dialect = event.target.dataset.readersDialect
      this.context = event.target.dataset.context
      this.text_function = event.target.dataset.textFunction
      this.audio_start_in_chapter = event.target.dataset.textunitStart
      this.audio_finish_in_chapter = event.target.dataset.textunitEnd
    },
    play(event) {
      event.target.style.boxShadow = "0 0 0 3px #81b441"
      remove_audio_player()
      // grabbing the audio file name and textunit start and duration
      let audio_file_name = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.audioFileName;
      let textunit_start = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.textunitStart;

      // I set the beginning to be 0.2 earlier, because it was a bit too late in many cases - THIS COULD BE ADJUSTED LATER
      let aeneas_correction = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.orderInChapter * 0.001;
      aeneas_correction = 0.2 - aeneas_correction;
      textunit_start = textunit_start - aeneas_correction;
      let textunit_end = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.textunitEnd;
      // I shortened all the audio by 0.1 seconds (so - 0.3), because they are usually too long in comparison to text - THIS COULD BE ADJUSTED LATER
      let textunit_duration = textunit_end - textunit_start - aeneas_correction
      let start_buffer = event.target.parentNode.previousElementSibling.previousElementSibling.firstElementChild.value;
      let end_buffer = event.target.parentNode.previousElementSibling.firstElementChild.value;

      // sending a GET request - creating audio START
      ///////////////////////////////////////////////
      let xhr = new XMLHttpRequest();
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          // obtaining the json response
          let json_response = xhr.responseText;
          // transforming the json response to js object
          let response_object = JSON.parse(json_response);
          let resulting_audio_file = response_object.resulting_audio_file;

          // automatic play
          var url = '/results/' + resulting_audio_file;
          Vue.nextTick(function () {
            let audio_source = document.querySelector("#audio_source")
            audio_source.src = url
            new GreenAudioPlayer('.ready-player-1', { showTooltips: true, showDownloadButton: false, enableKeystrokes: true });
          })
        };
      };

      xhr.open('GET', '/create_audio/' + audio_file_name + '/' + textunit_start + '/' + textunit_duration + '/' + start_buffer + '/' + end_buffer, true);
      xhr.send();
      // sending a GET request - creating audio ENDED
      ///////////////////////////////////////////////
    },
    download(event) {
      event.target.style.boxShadow = "0 0 0 3px #81b441"

      // grabbing the audio file name and textunit start and duration
      let audio_file_name = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.audioFileName;
      let textunit_start = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.textunitStart;

      // I set the beginning to be 0.2 earlier, because it was a bit too late in many cases - THIS COULD BE ADJUSTED LATER
      let aeneas_correction = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.orderInChapter * 0.001;
      aeneas_correction = 0.2 - aeneas_correction;
      textunit_start = textunit_start - aeneas_correction;
      let textunit_end = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.dataset.textunitEnd;
      // I shortened all the audio by 0.1 seconds (so - 0.3), because they are usually too long in comparison to text - THIS COULD BE ADJUSTED LATER
      let textunit_duration = textunit_end - textunit_start - aeneas_correction
      let start_buffer = event.target.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.value;
      let end_buffer = event.target.parentNode.previousElementSibling.previousElementSibling.firstElementChild.value;

      // sending a GET request - creating audio START
      ///////////////////////////////////////////////
      let xhr = new XMLHttpRequest();

      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          // obtaining the json response
          let json_response = xhr.responseText;
          // transforming the json response to js object
          let response_object = JSON.parse(json_response);
          let resulting_audio_file = response_object.resulting_audio_file;

          // creating and activating the download link
          let link = document.createElement('a');
          link.href = '/results/' + resulting_audio_file;
          link.download = resulting_audio_file;
          document.body.appendChild(link);
          link.click();
        };
      };

      xhr.open('GET', '/create_audio/' + audio_file_name + '/' + textunit_start + '/' + textunit_duration + '/' + start_buffer + '/' + end_buffer, true);
      xhr.send();
      // sending a GET request - creating audio START
      ///////////////////////////////////////////////
    },
    stop_audio(event) {
      let audio_element = document.querySelector("#audio_element")
      audio_element.pause();
      audio_element.currentTime = 0;
    }
  },
})


vue_app.mount('#wrapper')