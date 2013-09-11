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

    // $('#map-google').click(function () {
    //     $('#pane').val(2);
    // });
    // $('#map-bmapper').click(function () {
    //     $('#pane').val(2);
    // });
    
    var activePane = $('#pane').val();
    $( "#tabs" ).tabs({ active: activePane,
        beforeActivate: function(activePane) {
            return function( e, ui ) {
                activePane = ui.newPanel.index() - 1;
                $('#pane').val(activePane);
                console.log(activePane);
            }
        }(activePane) 
    });
    
    
    //console.log('pane is:', $('#pane').val());
    // $( "#tabs" ).tabs( "option", "active", $('#pane').val() );

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


function submitForm(pane, key, value) {
    //console.log(key, value);
    if (key != '') {
        document.getElementById(key).value = value;
    }
    document.getElementById('pane').value = pane;
    //console.log('pane',pane);
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

