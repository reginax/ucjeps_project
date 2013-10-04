function getFormData(formId) {
    //create requestObj from search form
    var searchForm = $(formId).find(':input').not($('button'));
    var formData = {};
    $.each(searchForm, function (formData) {
        return function (index, inputItem) {
            if ($(inputItem).attr('type') == 'checkbox') {
                if ($(inputItem).is(':checked')) {
                    formData[$(inputItem).attr('name')] = $(inputItem).val();
                }
            }
            else {
                formData[$(inputItem).attr('name')] = $(inputItem).val();
            }
        }
    }(formData));

    return formData;
}

function chooseSlideDirection(targetId) {
    var Elem = $(targetId);
    if ($(Elem).css("display") == "none") { Elem.slideDown(); }
    else { Elem.slideUp(); }
}


$(document).ready(function () {
    $('#about').click(function() {
        chooseSlideDirection('#aboutTarget');
        $('#helpTarget').slideUp();
        $('#creditsTarget').slideUp();
    });
    $('#help').click(function() {
        chooseSlideDirection('#helpTarget');
        $('#aboutTarget').slideUp();
        $('#creditsTarget').slideUp();
    });
    $('#credits').click(function() {
        chooseSlideDirection('#creditsTarget');
        $('#helpTarget').slideUp();
        $('#aboutTarget').slideUp();
    });
    
    $("#acceptterms").click(function () {
        $(this).css({
            background: "",
            border: ""
        });
    });

    $('#search-reset').click(function () {
        $('#search')[0].reset();
        $('#resultsPanel').html('');
    });

    $('#search-list, #search-full, #search-grid').click(function () {
        var formData = getFormData('#search');
        formData[$(this).attr('name')] = '';

        $.post("/public/results/", formData).done(function (data) {
            if (!formData['acceptterms']) {
                $("#acceptterms")
                    .css({
                        background: "yellow",
                        border: "3px red solid"
                    });
            }
            else {
                $('#resultsPanel').html(data);
                $('#resultsListing').tablesorter({
                    headers: {
                        0: {sorter: false},
                        1: {width: '100px' },
                        2: {width: '260px' },
                        4: {width: '90px', sorter: 'isoDate' },
                        9: {width: '180px' }
                    }
                });
                $('#tabs').tabs({ active: 0 });
            }
        });
    });


    $(document).on('click', '.map-item', function () {
        var Elem = $(this).siblings('.small-map');
        if ($(Elem).css("display") == "none") {
            Elem.slideDown();
        }
        else {
            Elem.slideUp();
        }
    });

    $(document).on('click', '.facet-item', function () {
        var key = ($(this).attr('data-facetType'));
        var value = ($(this).text());

        if (key != '') {
            var keyElement = $('#' + key);
            var keyElQual = $('#' + key + '_qualifier');
            if (keyElement != null) {
                keyElement.val(value);
                if (keyElQual != null) {
                    keyElQual.val('exact');
                }
            }
        }

        var formData = getFormData('#search');
        // TODO: CURRENTLY DEFAULT TO SEARCH-LIST BUT SHOULD HAVE A PERSISTENT DISPLAY TYPE? CURRENTLY DOESN'T ON DEV
        formData['search-list'] = '';

        $.post("/public/results/", formData).done(function (data) {
            $('#resultsPanel').html(data);
            $('#resultsListing').tablesorter({
                headers: {
                    0: {sorter: false},
                    1: {width: '100px' },
                    2: {width: '260px' },
                    4: {width: '90px', sorter: 'isoDate' },
                    9: {width: '180px' }
                }
            });
            $('#tabs').tabs({ active: 1 });
        });
    });

    $(document).on('click', '#map-bmapper, #map-google', function () {
        var formData = getFormData('#selectedItems');
        // formData[$(this).attr('name')] = '';

        if ($(this).attr('id') == 'map-bmapper') {
            $.post("/public/bmapper/", formData).done(function (data) {
                window.open(data, '_blank');
            });
        } else if ($(this).attr('id') == 'map-google') {
            $.post("/public/gmapper/", formData).done(function (data) {
                $('#maps').html(data);
            });
        }
    });
});