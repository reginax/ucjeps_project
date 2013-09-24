$(document).ready(function () {
    $('#resultsListing').tablesorter({
        headers: {
            0: {sorter: false},
            1: {width: '100px' },
            2: {width: '260px' },
            4: {width: '90px' },
            9: {width: '180px' }
        }
    });
    
    // $( "#tabs" ).tabs( "option", "active", $('#pane').val() );
    
    // instantiate '#tabs' as an instance of tabs, with an active panel of the value of the hidden form element
    // each time a different panel is activated (beforeActivate event triggered) 
    // the hidden input value of '#pane' is set with the new panels's index-1 
    // if we make the results bit AJAX-y, we can probably get rid of this input element and just keep track of it in the JS
    $( "#tabs" ).tabs({ active: $('#pane').val(),
        beforeActivate: function() {
            return function( e, ui ) {
                $('#pane').val(ui.newPanel.index()-1);
            }
        }()
    });
    
    // we copy the input values from the search form and add them to selectedItems form
    // as hidden values to preserve those values after each selection is made.
    $('#selectedItems').submit(function () {

        $('#search input').each(function () {
            var el = $(this);
            //console.log(el.attr('name'), ': type is', el.attr('type'), el.val());
            if (el.attr('type') == 'radio') {
                //console.log('check', el.checked);
                if ($('input[name="' + name + '"]:checked').length != 0) {
                    //if (el.checked) {
                    //console.log('radio', el.attr('name'), el.val());
                    $('<input type="hidden" name="' + el.attr('name') + '" />')
                }
            }
            else if (el.attr('type') == 'checkbox') {
                //console.log('check', el.checked);
                if ($('input[name="' + name + '"]:checked').length != 0) {
                    //if (el.checked) {
                    $('<input type="hidden" name="' + el.attr('name') + '" />')
                }
            }
            else {
                //console.log(el.attr('name'), el.val());
                $('<input type="hidden" name="' + el.attr('name') + '" />')
                    .val(el.val())
                    .appendTo('#selectedItems');
            }
        });
    });

});

function submitForm(key, value) {
    //console.log(key, value);
    if (key != '') {
        var keyElement = document.getElementById(key);
        var keyElQual = document.getElementById(key + '_qualifier');
        if (keyElement != null) {
            keyElement.value = value;
            if (keyElQual != null) {
                keyElQual.value = 'exact';
            }
        }
    document.forms['search'].submit();
    return false;
    }
}

$(function () {
    $("[id^=select-items]").click(function (event) {
        var selected = this.checked;
        var mySet = $(this).attr("name");
        mySet = mySet.replace('select-', '');
        // console.log(mySet);
        // Iterate each checkbox
        $("[name^=" + mySet + "]").each(function () {
            this.checked = selected;
        });
    });
    return false;
});

