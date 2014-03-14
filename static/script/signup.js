var validity_checking_url="http://tucao.pedestal.cn/api?callback=?";
var post_url = "http://tucao.pedestal.cn/signup";
//validity_checking_url = "test.js";
var email_key;
var name_key;
var password_key;

$(document).ready(function() {
	$('#email-address').blur(validity_checking);
	$('#nick-name').blur(validity_checking);
	$('#password').blur(is_password_legal);
	$('#password-confirmation').blur(is_password_matched);
	$('#submit').click(submit_register_form);
	init();
});

	function init() {
		$('#email-address').val($.cookie('email'));
		$('#nick-name').val($.cookie('name'));
		$('#password').val($.cookie('password'));
		$('#password-confirmation').val($.cookie('repassword'));
	}

	function save_form_to_cookie(email, nickname, password1, password2, is_subscribed) {
		$.cookie('email', email);
		$.cookie('name', nickname);
		$.cookie('password', password1);
		$.cookie('repassword', password2);
        $.cookie('is_subscribed', is_subscribed);
	}
	function submit_register_form() {
		var email = $('#email-address').val();
		var nickname=$('#nick-name').val();
		var password1=$('#password').val();
		var password2=$('#password-confirmation').val();
		var is_subscribed=$('#is-subscribed').checked ? 1 : 0;

		is_password_legal();
		is_password_matched();
		
		$('#email-address').blur();
		$('#nick-name').blur();

		save_form_to_cookie(email,nickname,password1,password2, is_subscribed);

		post_register_data(email, nickname, password1, password2, is_subscribed);
	}

    function post_register_data(email, name, password, repassword, is_subscribed) {
            _xsrf = $.cookie('_xsrf');
             $.post(post_url, {
                    email: email,
                    name: name,
                    password: password,
                    repassword: repassword,
                    is_subscribed: is_subscribed,
                    _xsrf: _xsrf,
                });
    }

	function is_password_legal() {
		var passwd=$('#password').val();
		if (passwd.length < 8  || passwd.length > 16) {
			// 密码长度不正确
			$('#password').siblings(':first').html("密码长度不正确");
			return -1;
		} else {
			$('#password').siblings(':first').html("推荐8-16位字母、数字组合");
			return 0;
		}
	}

	function is_password_matched() {
		var passwd1=$('#password').val();
		var passwd2=$('#password-confirmation').val();
		if (passwd1 != passwd2) {
			// 两次密码不匹配
			$('#password-confirmation').siblings(':first').html("两次密码不匹配");
            password_key = 0;

            $('#submit').addClass('btn-disabled');
			return -1;
		} else {
			$('#password-confirmation').siblings(':first').html("");
            password_key = 1;
              if (email_key && name_key && password_key) {
                   $('#submit').removeClass('btn-disabled');
              } else {
                 $('#submit').addClass('btn-disabled');
              }
			return 0;
		}
	}


	function validity_checking(type, value) {
		type = $(this).attr('id')=="nick-name" ? "NAME" : "EMAIL";
		value = $(this).val();
		if (value == "") {
			// 不能为空
			$(this).siblings(':first').html("不能为空");
			return 0;
		}
		$.getJSON(validity_checking_url,{
			type: type,
			value: value, 
			}, function(data){
				var label_id = data.type=="EMAIL" ? "email-address":"nick-name";
				if (data.status == "UNIQUE") {
					$('#'+label_id).siblings(':first').html(data.type+"可以使用");
                    data.type=="EMAIL"?email_key=1:name_key=1;
				}
				if (data.status == "REPEATED") {
					$('#'+label_id).siblings(':first').html(data.type+"已被使用");
                    data.type=="EMAIL"?email_key=0:name_key=0;
				}
			});
        if (email_key && name_key && password_key) {
            $('#submit').removeClass('btn-disabled');
        } else {
            $('#submit').addClass('btn-disabled');
        }
	}

