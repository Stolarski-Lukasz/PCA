// triggering search button on pressing Enter START [I may add the activation of the button graphic effects...]
///////////////////////////////////////////////////

// Get the input field
var pca_search_button = document.getElementById("pca-search-button");
var input = document.getElementById("pca-search-input");

// Execute a function when the user releases a key on the keyboard
input.addEventListener("keyup", function (event) {
  // Cancel the default action, if needed
  event.preventDefault();
  // Number 13 is the "Enter" key on the keyboard
  if (event.keyCode === 13) {
    console.log("sss")
    // Trigger the button element with a click
    pca_search_button.click();
    // here
    var button = new bootstrap.Button(pca_search_button)
    button.toggle()
  }
});

// triggering search button on pressing Enter ENDED
///////////////////////////////////////////////////