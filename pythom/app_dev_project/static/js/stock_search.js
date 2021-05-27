$("#box").on('keyup', function () {
    var matcher = new RegExp($(this).val());
    $('.item').show().not(function () {
        return matcher.test($(this).find('.name').text())
    }).hide();
});