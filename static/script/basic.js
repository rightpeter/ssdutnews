$(document).ready(function() {

	$('#content').keyup(function() {
		$('#rest-num').text($('#content').val().length+"/240");
	});

	$('#tucao-submit').click(function() {
		//if($('#content').val().length > 240) {
			
		//}
		$.post("/tucao/comm?"+(new Date()).valueOf(), {id: $('#id').attr("value"),content: $('#content').val()}, function (res) {
			console.log(res);
			window.location.reload();
		});
	});

    $(".body-full").hide();
    // 点击 more 显示更多内容
    $(".body-abstract").click(function() {
        $(".body-full").show("fast");
        $(".body-abstract").hide();
    });
});
