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
    
    $('#resultsListing').tablesorter();
    
});