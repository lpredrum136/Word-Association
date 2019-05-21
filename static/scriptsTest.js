$(document).ready(function() {
    
    // Change between classic and network view
    $('#classic').change(function () { 
        if (this.checked) {
            $('.panel-group').fadeIn('slow');
        }
        else {
            $('.panel-group').fadeOut('slow');
        }
    });

    $('#network').change(function () { 
        if (this.checked) {
            $('#mynetwork').fadeIn('slow');
        }
        else {
            $('#mynetwork').fadeOut('slow');
        }
    });

    // Hide the network div by default on page load
    $('#mynetwork').hide();

    // click on a word to immediately start new query
    // Initialise aggregated score when building word path
    $('#synonyms .btn.m-1').click(function() {
        var url_to_go = `/synonyms?word=${$.trim(this.innerHTML.split('<span')[0])}`; // get the word only and construct to redirect url
        scoreToAdd = this.innerHTML.split('ml-1">')[1].split('</span>')[0]; // get the score of the word

        // alert(`Score is ${scoreToAdd}`);

        // Save the score (not accumulate)
        localStorage.setItem("scoreToAdd", scoreToAdd);

        // Save the score
        // localStorage.setItem("scoreToAdd", parseInt(parseInt(localStorage.getItem("scoreToAdd")) + parseInt(scoreToAdd))); // Because localStorage treats everything as string

        // redirect to url above
        document.location.href = url_to_go;

        // alert('You click on ' + this.innerHTML.split('<span')[0]);        
    });

    // Click in #related also go to new page
    $('#related .btn.m-1').click(function() {
        var url_to_go = `/navbarSearch?word=${$.trim(this.innerHTML.split('<span')[0])}`; // get the word only and construct to redirect url
        
        // Clear localstorage because user stray on another path
        localStorage.clear();

        // redirect to url above
        document.location.href = url_to_go;
    });

    // Click in #concepts also go to new page
    $('#concepts .btn.m-1').click(function() {
        var url_to_go = `/navbarSearch?word=${$.trim(this.innerHTML.split('<span')[0])}`; // get the word only and construct to redirect url
        
        // Clear localstorage because user stray on another path
        localStorage.clear();

        // redirect to url above
        document.location.href = url_to_go;
    });

    // Word Bag
    var storage_keys = [];
    for (var i = 0; i < localStorage.length; i++) {
        storage_keys.push(localStorage.key(i));
        console.log(storage_keys[i]);
    }

    // Update distance
    var html_to_display, word_to_change, score_to_change;
    var results_to_change = document.getElementById('synonyms').getElementsByClassName('btn m-1');
    for (var i = 0; i < results_to_change.length; i++) {
        // Get the word
        word_to_change = $.trim(results_to_change[i].innerHTML.split('<span')[0]);
        // Get the score
        score_to_change = results_to_change[i].innerHTML.split('ml-1">')[1].split('</span>')[0];
        // Display accumulated score if the word is not in word bags yet
        if (storage_keys.length != 0) {
            if (!storage_keys.includes(word_to_change)) {
                html_to_display = parseInt(score_to_change) + parseInt(localStorage.getItem("scoreToAdd"));
                html_to_display = html_to_display.toString();
                // scores_to_accumulate[i].innerHTML = html_to_display;
                results_to_change[i].getElementsByClassName('badge badge-warning badge-pill ml-1')[0].innerHTML = html_to_display;
            }
            else {
                results_to_change[i].getElementsByClassName('badge badge-warning badge-pill ml-1')[0].innerHTML = localStorage.getItem(word_to_change);
            }
        }        
    }

    /* Append the new words into localStorage */    
    localStorage.setItem($('#originalWord').html(), 0); // The original word always has score 0
    var word_bag = document.getElementById('synonyms').getElementsByClassName('btn m-1');
    var word_name, word_score; // Get all the words, synonyms only
    for (var i = 0; i < word_bag.length; i++) {
        // store the score of each word in localStorage with its key as the word itself
        // get the word
        word_name = $.trim(word_bag[i].innerHTML.split('<span')[0]);
        // get its score
        word_score = word_bag[i].innerHTML.split('ml-1">')[1].split('</span>')[0];
        // if the word is already in localStorage (already in storage_keys array), no change
        localStorage.setItem(word_name, word_score);
    }

    // Test in console log
    for (var i = 0; i < localStorage.length; i++) {
        console.log(localStorage.key(i));
        console.log(localStorage.getItem(localStorage.key(i)));
    }

    // Highlight the first item in the word path, i.e. the original word
    $('.page-link').first().addClass('bg-primary text-white');

    // Highlight the item currently selected in the word path, i.e. the current word
    var current_word = $('#currentWord').html();
    $(".page-link").each(function() {
        if($(this).html() == current_word) {
            $(this).addClass("bg-primary text-white");
        }
    });

    // Press enter on the navbar search is equal to click on 'Search'
    $('#navbarSearch').keypress(function (e) { 
        var keycode = (e.keycode ? e.keycode: e.which);
        if (keycode == '13') {
            $('#navbarSearchButton').click(); // To show the alert, same as when click on 'Search'
            return false;
        } // equivalent to 'enter'
    });

    // Press enter on the modal that pop up is equal to 'Proceed'
    /* $('#navbarSearchProceed').keypress(function (e) { 
        var keycode = (e.keycode ? e.keycode: e.which);
        if (keycode == '13') {
            $('#navbarSearchProceed').click(); // To show the alert, same as when click on 'Search'
            return false;
        } // equivalent to 'enter'
    }); */

    // Click on Proceed in modal pop up when click on 'Search' above, will actually submit the form and clear the localStorage. That means starting again.
    $('#navbarSearchProceed').click(function () {
        localStorage.clear();
        $('#navbarSearchForm').submit();        
    });

    // Click on Reset Word Path button will also start everything again
    $('#resetWordPath').click(function () {
        localStorage.clear();
        // alert('You click on reset word path');
    });

    // Click on Logo on navbar will also start everything again
    $('.navbar-brand').click(function () { 
        localStorage.clear();        
    });

    // Click on the errorRedirect (only show when there is an error) will also start everything again
    $('.errorRedirect').click(function () { 
        localStorage.clear();
    });

    // HomePage: If user input nothing, cannot press Search button
    // Already fix by adding "required" in the index.html. LOL

    // Result page: If user input nothing in navbarsearch, cannot proceed
    $('#navbarSearchButton').attr('disabled', true);// Disable it first

    $('#navbarSearch').on('keyup', function () {
        var textarea_value = $("#navbarSearch").val();
        if (textarea_value != '') {
            $('#navbarSearchButton').attr('disabled', false);
        } else {
            $('#navbarSearchButton').attr('disabled', true);
        }
    });

    // In #concepts, click on an external link will render the button unclickable
    var external_links = $('#concepts .badge-success');
    for (var i = 0; i < external_links.length; i++) {
        parent_node = external_links.eq(i).parent().off('click');
    }
});