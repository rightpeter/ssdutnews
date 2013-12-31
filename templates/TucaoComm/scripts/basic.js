$(document).ready(function() {

	$('#content').keyup(function() {
		$('#rest-num').text($('#content').val().length+"/240");
	});

	$('.normal-input-button').click(function() {
		if($('#content').val().length > 240) {
			
		}
		$.post("/tucao/comm", {id: $('#id').value,content: $('#content').val()});
	});
});
