
function addZero(number) {
    var newNumber = number;
    if (number.toString().length == 1) newNumber = "0" + number.toString();
    return newNumber;
}

// deposit history
// $(".dh-rank-value").each(function (index) {
//     const amount = $(".dh-rank-value").length;
//     $(this).text(index + 1);
// });


// copy referral
$("#copy-referral-link").on("click", function () {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($("#referral-link").val()).select();
    document.execCommand("copy");
    $temp.remove();
});

$(window).on('load', function() {
	$('#ex1').height($(window).outerHeight(true));
	$('#ex2').height($(window).outerHeight(true));
	$('#ex3').height($(window).outerHeight(true));
    // $('#ex3').modal('show');
});
	
