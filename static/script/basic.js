$(document).ready(function() {

	$('#content').keyup(function() {
		$('#rest-num').text($('#content').val().length+"/240");
	});

	$('.normal-input-button').click(function() {
		//if($('#content').val().length > 240) {
			
		//}
		$.post("/tucao/comm?"+(new Date()).valueOf(), {id: $('#id').attr("value"),content: $('#content').val()}, function (res) {
			console.log(res);
			window.location.reload();
		});
	});
});
