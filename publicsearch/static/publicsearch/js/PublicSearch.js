function getFormData(formId) {
    //create requestObj from search form
    searchForm = $(formId).find(':input').not($('button'));
    formData = {};
    $.each(searchForm, function(formData){
        return function(index, inputItem) {
            formData[$(inputItem).attr('name')] = $(inputItem).val();
        }
    }(formData));
    
    return formData;
}

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
    
    $('#tabs').tabs({ active: 0 });
    
    $('#search-reset').click(function() {
        $('#search')[0].reset();
        $('#resultsPanel').html('');
    });
    
    $('#search-list, #search-full, #search-grid').click(function() {
        formData = getFormData('#search');
        formData[$(this).attr('name')] = '';

        $.post("/public/results/", formData).done(function(data) {
            $('#resultsPanel').html(data);
            $('#tabs').tabs({ active: 0 });
        });
    });
    
    $(document).on('click', '.facet-item', function() {
        key = ($(this).attr('data-facetType'));
        value = ($(this).text());
        
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
        
        formData = getFormData('#search');
        // TODO: CURRENTLY DEFAULT TO SEARCH-LIST BUT SHOULD HAVE A PERSISTENT DISPLAY TYPE? CURRENTLY DOESN'T ON DEV
        formData['search-list'] = '';
        
        $.post("/public/results/", formData).done(function(data) {
            $('#resultsPanel').html(data);
            $('#tabs').tabs({ active: 1 });
        });
    });
    
    $(document).on('click', '#map-bmapper, #map-google', function() {
        formData = getFormData('#selectedItems');
        // formData[$(this).attr('name')] = '';
        
        if ($(this).attr('id') == 'map-bmapper') {
            $.post("/public/bmapper/", formData).done(function(data) {
                window.open(data, '_blank');
            });
        } else if ($(this).attr('id') == 'map-google') {
            $.post("/public/gmapper/", formData).done(function(data) {
                $('#maps').html(data);
            });
        }
    });
});