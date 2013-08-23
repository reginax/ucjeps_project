$(document).ready(function() {
    $('.drillDown').click(function() {
        $(this).hide();
        $(this).parent().children('.drilled').show();
        $(this).parent().children('.drillUp').show();
    });
    
    $('.drillUp').click(function() {
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

});

function textToggle(divName) {
    var ele = document.getElementById(divName);
    var ele_toggle = document.getElementById(divName+'_toggle');
    if (ele.style.display == 'none') {
         ele.style.display='block';
        ele_toggle.innerHTML = "hide";
    }
    else {
        ele.style.display='none';
        ele_toggle.innerHTML = "show";
    }
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
});

