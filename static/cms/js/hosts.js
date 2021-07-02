//添加主机之新增数据弹窗
// (点击保存之后执行的js代码，不仅是新增数据之后进行保存操作，编辑完数据之后也需要进行保存操作)

$(function () {
    $('#save_banner_btn').click(function (event) {
        event.preventDefault();
        var self = $(this);
        var dialog = $('#modal-dialog');

        var nameInput = $("input[name='name']");


        var ipInput = $("input[name='link_url']");


        // var priorityInput = $("input[name='priority']");


        var name = nameInput.val();
        console.log(name)
        var ip = ipInput.val();
        console.log(ip)
        console.log(status)
        // var priority = priorityInput.val();
        // console.log(priority)
        var submitType = self.attr('data-type');
        var bannerId = self.attr('data-id');
        console.log("22222")

        if (!name || !ip ) {
            zlalert.alertInfo('请输入所有数据');
            return;
        }

        //判断是新增还是编辑完数据之后进行的保存操作

        var url = '';
        if (submitType == 'update') {
            url = '/cms/ubanner/';
        } else {
            url = '/cms/add_host/'
        }
        zlajax.post({
            'url': url,
            'data': {
                'name': name,
                'ip': ip,
                'banner_id': bannerId
            },
            'success': function (data) {
                if (data['code'] == 200) {
                    //点击保存，弹窗就隐身
                    dialog.modal('hide');

                    window.location.reload()
                } else {
                    zlalert.alertInfo(data['message']);
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError()
            }
        });
    });

});



//轮播图编辑数据弹窗(只是把数据弹窗出来，保存操作还是要调用上面的代码)
$(function () {
    $('.edit-banner-btn').on('click', function (event) {
        var $this = $(this);
        var dialog = $('#banner-dialog');
        dialog.modal('show');

        var tr = $this.parent().parent();
        var name = tr.attr('data-name');
        var img = tr.attr('data-img');
        var link = tr.attr('data-link');
        var priority = tr.attr('data-priority');
        var nameInput = dialog.find('input[name=name]');
        var imgInput = dialog.find('input[name=img_url]');
        var linkInput = dialog.find('input[name=link_url]');
        var priorityInput = dialog.find('input[name=priority]');
        var saveBtn = dialog.find('#save_banner_btn');

        nameInput.val(name);
        imgInput.val(img);
        linkInput.val(link);
        priorityInput.val(priority);
        saveBtn.attr('data-type', 'update');
        saveBtn.attr('data-id', tr.attr('data-id'));

    });
});

//主机删除数据弹窗
$(function () {
    $('.delete-banner-btn').on('click', function () {
        var banner_id = $(this).parent().parent().attr('data-id');
        zlalert.alertConfirm({
            'msg': '确定要删除这条状态吗?',
            'confirmCallback': function () {
                zlajax.post({
                    'url': '/cms/del_host/',
                    'data': {
                        'banner_id': banner_id
                    },
                    'success': function (data) {
                        if (data['code'] == 200) {
                            window.location.reload();
                        } else {
                            zlalert.alertInfo(data['message'])
                        }
                    }

                })
            }
        });
    });
});


//初始化七牛
// $(function () {
//
//     //zlqiniu对象的setup 方法的传参
//     zlqiniu.setup({
//         'domain': 'http://q7bncq283.bkt.clouddn.com/',
//         //上传图片的按钮
//         'browse_btn': 'upload-btn',
//         //提交的url
//         'uptoken_url': '/c/uptoken/',
//         'success': function (up, file, info) {
//             //上传成功后，显示图片的url
//             // var imageInput = $("input[name='img_url']");
//             // imageInput.val(file.name);
//         }
//     });
// });
