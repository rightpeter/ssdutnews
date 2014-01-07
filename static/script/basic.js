$(document).ready(function() {

	var pageid = $('#id').attr("value");
	
	//  Prevpage 和 Nextpage 
	var prevpage = parseInt(pageid) - 1;
	var nextpage = parseInt(pageid) + 1;

	// 隐藏两个按钮
//	$('#prevpage').hide();
//	$('#nextpage').hide();
	
	// url-prevpage url-nextpage 换成指定页面的url
	$.get("/tucao/comm/"+prevpage, function() {
//		$('#prevpage').show();
		$('#prevpage').attr('href', "/tucao/comm/"+prevpage);
        $('#prevpage').removeClass('disabled');
		});
	$.get("/tucao/comm/"+nextpage, function() {
//		$('#nextpage').show();
		$('#nextpage').attr('href', "/tucao/comm/"+nextpage);
        $('#nextpage').removeClass('disabled');
		});

	$('#content').keyup(function() {
		$('#rest-num').text($('#content').val().length+"/240");
	});
	
	$('.level-reply a').click(function() {
		var level = $(this).parent().parent().attr('id');
		$('#content').text('@'+level+': ');
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
