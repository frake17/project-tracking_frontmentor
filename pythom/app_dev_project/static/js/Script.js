// JavaScript source code
//$("#box").on('keyup', function () {
    //var matcher = new RegExp($(this).val());
    //$('#item').show().not(function () {
        //return matcher.test($(this).find('.stock_name').text())
    //}).hide();
//});

$(document).ready(function(){
  $("#box").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#item-container #item").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});

$(document).ready(function () {
    //select the POPUP FRAME and show it
    //$("#popup,.mask").hide().fadeIn(1);
    //$(".d-flex, .flex-row, .flex-column").css('filter', 'blur(5px)');
    $('.mask').fadeOut(1);

    //close the POPUP if the button with id="close" is clicked
    $(".mask").on("click", function () {
        $("#popup,.mask").fadeOut(1);
        $(".d-flex, .flex-row, .flex-column, .shop-item, .flex-colum").css('filter', 'none');
    });
});

$(document).ready(function () {
    $('#notification').on('click', function () {
        $("#popup,.mask").hide().fadeIn(1);
        $(".d-flex, .flex-row, .flex-column, .shop-item, .flex-colum").css('filter', 'blur(5px)');
    });
})