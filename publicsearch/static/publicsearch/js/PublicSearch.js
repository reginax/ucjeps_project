$(document).ready(function () {
    $('.drillDown').click(function () {
        $(this).hide();
        $(this).parent().children('.drilled').show();
        $(this).parent().children('.drillUp').show();
    });

    $('.drillUp').click(function () {
        $(this).hide();
        $(this).parent().children('.drilled').hide();
        $(this).parent().children('.drillDown').show();
    });

    $('#resultsListing').tablesorter({
        headers: {
            0: {sorter: false},
            1: {width: '100px' },
            2: {width: '260px' },
            4: {width: '90px' },
            9: {width: '180px' }
        }
    });


    $( "#tabs" ).tabs();
    // need to figure out how to make the tab the user was using the active tab...help!
    //$( "#tabs" ).tabs( "option", "active", 1 );

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
            else {
                //console.log(el.attr('name'), el.val());
                $('<input type="hidden" name="' + el.attr('name') + '" />')
                    .val(el.val())
                    .appendTo('#selectedItems');
            }
        });
    });

});

$.fn.togglepanels = function () {
    return this.each(function () {
        $(this).addClass("ui-accordion ui-accordion-icons ui-widget ui-helper-reset")
        .find("h3")
        .addClass("ui-accordion-header ui-helper-reset ui-state-default ui-corner-top ui-corner-bottom")
        .hover(function () {
            $(this).toggleClass("ui-state-hover");
        })
        .prepend('<span class="ui-icon ui-icon-triangle-1-e"></span>')
        .click(function () {
            $(this)
                .toggleClass("ui-accordion-header-active ui-state-active ui-state-default ui-corner-bottom")
                .find("> .ui-icon").toggleClass("ui-icon-triangle-1-e ui-icon-triangle-1-s").end()
                .next().slideToggle();
            return false;
        })
        .next()
        .addClass("ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom")
        .hide();
    });
};

function textToggle(divName) {
    var ele = document.getElementById(divName);
    var ele_toggle = document.getElementById(divName + '_toggle');
    if (ele.style.display == 'none') {
        ele.style.display = 'block';
        ele_toggle.innerHTML = "hide";
    }
    else {
        ele.style.display = 'none';
        ele_toggle.innerHTML = "show";
    }
    return false;
}


function submitForm(facetContext, key, value) {
    //console.log(key, value);
    document.getElementById(key).value = value;
    document.getElementById('facetContext').value = facetContext;
    document.forms['search'].submit();
    return false;
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

