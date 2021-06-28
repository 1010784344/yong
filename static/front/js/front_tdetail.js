function sleep(time) {
    var startTime = new Date().getTime() + parseInt(time, 10);
    while(new Date().getTime() < startTime) {}
};




//倒计时异步函数
function startTimer() {
        var displays = $('#mytime');

        var timer = 3599;
        var minutes, seconds;
        // console.log(duration)
        // console.log(minutes)
        // console.log(seconds)
        // console.log(timer)
        var refresh = setInterval(function () {
            minutes = parseInt(timer / 60, 10)
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            var output = "00 : " + minutes + " : " + seconds;
            // alert(output)
            // console.log(typeof displays)
            // console.log(displays)
            // console.log(output)
            // displays.html(output);
            displays.text(output);
            //修改title 的标签值
            // $("title").html(output + " - TimerTimer");

            if (--timer < 0) {
                displays.text("Time's Up!");
                clearInterval(refresh);  // exit refresh loop
                // var music = $("#over_music")[0];
                // music.play();
                alert("Time's Up!");
            }
        }, 1000);

    }
//将进度条替换为为倒计时页面
function mysub(doname,workname){
    console.log(doname)
    console.log(workname)

                        var tmp = $('#contest-btn')

                        var realtmep = '<div class="extend">\n' +
                        '                    <div class="linkwz" id="ccurl" data-id="tmpurl" >\n' +
                        '                        <a href="http" title="http" target="_blank">http</a>\n' +
                        '                    </div>\n' +
                        // '                    <div class="setintover"><span id="cd_h">00 : </span><span id="cd_f">58 : </span><span id="cd_m">57</span>\n' +
                        '                    <div class="setintover">\n' +
                            '    <p id="mytime"></p>\n' +
                        '\n' +
                        '                    </div>\n' +
                        '\n' +
                        '                        <div class="operation_div">\n' +
                        '                            <div class="issued" id="overtime" >延长时间(<span>3</span>)</div>\n' +
                        '                            <div> </div>\n' +
                        '                            <div class="issued" id="recreate" onclick="redeal()" >重新创建</div>\n' +
                        '\n' +
                        '                        </div>\n' +
                        '\n' +
                        '\n' +
                        '                    </div>'

                        realtmep = realtmep.replace(/http/g, doname)
                        realtmep = realtmep.replace('tmpurl', workname)
                        tmp.html(realtmep)
                        // tmp.html('<div class="extend">\n' +
                        // '                    <div class="linkwz">\n' +
                        // '                        <a href="http://eci-2ze56d54cxd7xie6m6kw.cloudeci1.ichunqiu.com:80" title="http://eci-2ze56d54cxd7xie6m6kw.cloudeci1.ichunqiu.com:80" target="_blank">http://eci-2ze56d54cxd7xie6m6kw.cloudeci1.ichunqiu.com:80</a>\n' +
                        // '                    </div>\n' +
                        // // '                    <div class="setintover"><span id="cd_h">00 : </span><span id="cd_f">58 : </span><span id="cd_m">57</span>\n' +
                        // '                    <div class="setintover">\n' +
                        //     '    <p id="mytime"></p>\n' +
                        // '\n' +
                        // '                    </div>\n' +
                        // '\n' +
                        // '                        <div class="operation_div">\n' +
                        // '                            <div class="issued" onclick="">延长时间(<span>3</span>)</div>\n' +
                        // '                            <div> </div>\n' +
                        // '                            <div class="issued" onclick="">重新创建</div>\n' +
                        // '\n' +
                        // '                        </div>\n' +
                        // '\n' +
                        // '\n' +
                        // '                    </div>')

                    }







// 生成随机uuid(防止多用户请求进度条混乱)
function guid(){
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c){
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
});
}



//创建赛题按钮触发进度条和计时器
$(function(){
   $('#comment-btn').on('click',function(event){
       event.preventDefault();
       //判断用户是否登录，没有登录就跳转登录页面
       var login_tag=$('#login-tag').attr('data-is-login');
       if (! login_tag){
           window.location='/signin/'
       }else{
            // 生成唯一的uuid
           var uuid = guid();
           var this_url = '/acontest/' + uuid
             var post_id=$('#post-content').attr('data-id');
            $.getJSON(this_url,{"task_id":post_id}, function(res){


            });


                var obj = $('#contest-btn')

                obj.html('<div  class="progress-div">\n' +
                    '\t        <div class="progress">\n' +
                    '\t            <div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="min-width: 2em; width: 2%;">2%\n' +
                    '\t            </div>\n' +
                    '\t        </div>\n' +
                    '\t    </div>')
                // 设置定时器,隔段时间请求一次数据
                var sitv = setInterval(function(){
                    // prog_url指向请求进度的url，后面会在flask中设置
                    var prog_url = '/show_progress/' + uuid
                    $.getJSON(prog_url, function(num_progress){
                        $('.progress-div').css('visibility', 'visible');
                        $('.progress-bar').css('width', num_progress.res + '%');
                        $('.progress-bar').css('background', 'Darkorange');
                        $('.progress-bar').css('text-align', 'center');
                        $('.progress-bar').text(num_progress.res + '%');
                        if(num_progress.res == '100'){
                            console.log(num_progress)
                            clearInterval(sitv);
                            var doname = num_progress.domains
                            var workname = num_progress.workname
                            mysub(doname,workname)
                            //倒计时定时任务开启
                            startTimer();

                        }
                    });
                }, 500)
            // 触发后台存储数据业务开始执行,后台返回数据之后，getjson 下面的js代码才会继续执行

//              var tmp_url = '/progress_data/' + uuid
//            console.log(9999999)
//             $.getJSON(tmp_url, function(res){
//                 console.log(11111)
//                 console.log('#######')
//                 console.log(res)
//
//                 // 清楚定时器
//                 clearInterval(sitv);
//                 if(res.res == '100'){
//                     $('.progress-bar').css('width', '100%');
//                     $('.progress-bar').text('100%');
// //
// //                     //进度条换成倒计时 html 代码块
//                         var doname = res.domains
//                     mysub(doname)
//                     //倒计时定时任务开启
//                     startTimer();
//
//
//
//
//                 }else{
//                     $('.progress-bar').css('background', 'red');
//                     setTimeout(function(){
//                         alert('失败了!');
//                     }, 1);
//                 }
//             })
    }
       })
})



//提交评论
// $(function(){
//    $('#upload-btn').on('click',function(event){
//        event.preventDefault();
//        //判断用户是否登录，没有登录就跳转登录页面
//        var login_tag=$('#login-tag').attr('data-is-login');
//        if (! login_tag){
//            window.location='/signin/'
//        }else{
//            var content=window.ue.getContent();
//            var post_id=$('#post-content').attr('data-id');
//            zlajax.post({
//               'url':'/acomment/' ,
//                'data':{
//                   'content':content,
//                    'post_id':post_id
//                },
//                'success':function(data){
//                   if(data['code']==200){
//                       zlalert.alertSuccessToast(msg='评论发表成功');
//                       window.location.reload();
//                   }else{
//                         zlalert.alertInfo(data['message']);
//                   }
//                }
//            });
//        }
//
//    }) ;
// });


//创建赛题（无进度条）
// $(function(){
//    $('#comment-btn').on('click',function(event){
//        event.preventDefault();
//        //判断用户是否登录，没有登录就跳转登录页面
//        var login_tag=$('#login-tag').attr('data-is-login');
//        if (! login_tag){
//            window.location='/signin/'
//        }else{
//            // var content=window.ue.getContent();
//            var post_id=$('#post-content').attr('data-id');
//            zlajax.get({
//               // 'url':'/acomment/' ,
//                'url':'/acontest/' ,
//                'data':{
//                   // 'content':content,
//                    'task_id':post_id
//                },
//                'success':function(data){
//                   if(data['code']==200){
//                       zlalert.alertSuccessToast(msg='任务创建成功');
//                       // window.location.reload();
//                   }else{
//                         zlalert.alertInfo(data['message']);
//                   }
//                }
//            });
//        }
//
//    });
// });

// function redeal(){
//    $('#recreate').on('click',function(event){
//        // event.preventDefault();
//        //判断用户是否登录，没有登录就跳转登录页面
//        console.log('hhhhhello')
//    })
// }


//重新创建
function redeal(){
   $('#recreate').on('click',function(event){
       // event.preventDefault();
       //判断用户是否登录，没有登录就跳转登录页面
       console.log('hhhhhello')
       var login_tag=$('#login-tag').attr('data-is-login');
       if (! login_tag){
           window.location='/signin/'
       }else{
            // 生成唯一的uuid
           var uuid = guid();
           var this_url = '/rcontest/' + uuid
             var work_name=$('#ccurl').attr('data-id');
           console.log(work_name)
            $.getJSON(this_url,{"work_name":work_name}, function(res){


            });


                var obj = $('#contest-btn')

                obj.html('<div  class="progress-div">\n' +
                    '\t        <div class="progress">\n' +
                    '\t            <div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="min-width: 2em; width: 2%;">2%\n' +
                    '\t            </div>\n' +
                    '\t        </div>\n' +
                    '\t    </div>')
                // 设置定时器,隔段时间请求一次数据
                var sitv = setInterval(function(){
                    // prog_url指向请求进度的url，后面会在flask中设置
                    var prog_url = '/show_progress/' + uuid
                    $.getJSON(prog_url, function(num_progress){
                        $('.progress-div').css('visibility', 'visible');
                        $('.progress-bar').css('width', num_progress.res + '%');
                        $('.progress-bar').css('background', 'Darkorange');
                        $('.progress-bar').css('text-align', 'center');
                        $('.progress-bar').text(num_progress.res + '%');
                        if(num_progress.res == '100'){
                            console.log(num_progress.res)
                            clearInterval(sitv);
                            var doname = num_progress.domains
                            var workname = num_progress.workname
                            mysub(doname,workname)
                            //倒计时定时任务开启
                            startTimer();

                        }
                    });
                }, 500)

    }
       })
}


//提交flag
function subflag(){
   $('#flag-btn').on('click',function(event){
       // event.preventDefault();
       //判断用户是否登录，没有登录就跳转登录页
       var login_tag=$('#login-tag').attr('data-is-login');
       if (! login_tag){
           window.location='/signin/'
       }else{

           var work_name=$('#ccurl').attr('data-id');
           var flagInput = $("input[name='flaginfo']");
           var tmpflag = flagInput.val();
           zlajax.get({
                    'url': '/aanswer/',
                    'data': {
                        'work_name': work_name,
                        'flaginfo': tmpflag
                    },
                    'success': function (data) {
                        if (data['code'] == 200) {

                            if (data['message'] == '回答错误！'){
                                zlalert.alertErrorToast(data['message']);
                                sleep(1000)
                                window.location.reload();


                            } else if (data['message'] == '回答正确！'){

                                zlalert.alertSuccessToast(data['message']);
                                sleep(1000)
                                window.location.reload();

                            }



                            // window.location.reload();
                        } else {
                            zlalert.alertInfo(data['message'])
                        }
                    }

                })






    }
       })
}



































// $(function(){
//    $('#recreate').on('click',function(event){
//        event.preventDefault();
//        //判断用户是否登录，没有登录就跳转登录页面
//        var login_tag=$('#login-tag').attr('data-is-login');
//        if (! login_tag){
//            window.location='/signin/'
//        }else{
//            // var content=window.ue.getContent();
//            var post_id=$('#ccurl').attr('data-id');
//            zlajax.post({
//               // 'url':'/acomment/' ,
//                'url':'/rcontest/' ,
//                'data':{
//                   // 'content':content,
//                    'task_id':post_id
//                },
//                'success':function(data){
//                   if(data['code']==200){
//                       zlalert.alertSuccessToast(msg='任务创建成功');
//                       // window.location.reload();
//                   }else{
//                         zlalert.alertInfo(data['message']);
//                   }
//                }
//            });
//        }
//
//    });
// });