
$(function () {
    //选中获取验证码按钮，并绑定事件
    $("#captcha-btn").click(function (event) {
        event.preventDefault();
        //获取用户输入的邮箱
        //如果没有输入邮箱就想获取验证码，就会提示用户输入邮箱，后面的代码也不会再执行了
        var email = $("input[name='email']").val();
        if (!email) {
            zlalert.alertInfoToast('请输入邮箱');
            return;
        }
        zlajax.get({
            'url': '/cms/sendcaptcha/',
            'data': {'email': email},
            'success': function (data) {
                if (data['code'] == 200) {
                    zlalert.alertSuccessToast('邮件已发送成功！请注意查收！');
                } else {
                    zlalert.alertInfo(data['message']);
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError();
            }
        });
    });
});


$(function () {
    $("#submit").click(function (event) {
        event.preventDefault();

        // 先获取标签对象
        var emailE = $("input[name='email']");
        var captcheE = $("input[name='captcha']");

        //再获取标签里面的值
        var email = emailE.val();
        var captcha = captcheE.val();

        zlajax.post({
            'url': '/cms/resetemail/',
            'data': {'email': email, 'captcha': captcha},
            'success': function (data) {
                if (data['code'] == 200) {
                    emailE.val("");
                    captcheE.val("");
                    zlalert.alertSuccessToast('恭喜！邮箱修改成功');
                } else {
                    zlalert.alertInfo(data['message']);
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError();
            }
        });
    });
});



