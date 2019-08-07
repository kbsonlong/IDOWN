function validateForm(info) {
    if (info==null || info=="") {
        alert(info+"请检查用户名和密码是否填写");
        return false;
    }
    else {
        return true;
    }
}
// 解码
function decodeUnicode(str) {
    str = str.replace(/\\/g, "%");
    return unescape(str);
}
function get_connect_info() {
    var host = $.trim($('#host').val());
    var port = $.trim($('#port').val());
    var user = $.trim($('#user').val());
    var auth = $("input[name='auth']:checked").val();
    var pwd = $.trim($('#password').val());
    var password = window.btoa(pwd);
    var ssh_key = null;


    var formData = new FormData();
    var csrf = $("[name='csrfmiddlewaretoken']").val();
    formData.append('user', user);
    formData.append('password', password);
    formData.append('csrfmiddlewaretoken', csrf);
    if (auth === 'key') {
        var pkey = $('#pkey')[0].files[0];
        formData.append('pkey', pkey);
        formData.append('auth', auth);
    }else {
        formData.append('pkey', null);
        formData.append('auth', auth);
    }

    if (validateForm(user)) {
        $.ajax({
            url: '/webssh/upload_ssh_key/',
            type: 'post',
            data: formData,
            async: false,
            processData: false,
            contentType: false,
            mimeType: 'multipart/form-data',
            success: function (data) {
                ssh_key = data;
                alert(decodeUnicode( data ));
            }
        });
    }

    var connect_info1 = 'host=' + host + '&port=' + port + '&user=' + user + '&auth=' + auth;
    var connect_info2 = '&password=' + password + '&ssh_key=' + ssh_key;
    var connect_info = connect_info1 + connect_info2;
    return connect_info
}


function get_term_size() {
    var init_width = 12;
    var init_height = 20;

    var windows_width = $(window).width();
    var windows_height = $(window).height();

    return {
        cols: Math.floor(windows_width / init_width),
        rows: Math.floor(windows_height / init_height),
    }
}


function websocket(info) {
    var cols = get_term_size().cols;
    var rows = get_term_size().rows;
    var connect_info;
    if (info) {
        connect_info = info;
    }else {
        connect_info = get_connect_info();
    }

    var term = new Terminal(
        {
            cols: cols,
            rows: rows,
            useStyle: true,
            cursorBlink: true
        }
        ),
        protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://',
        socketURL = protocol + location.hostname + ((location.port) ? (':' + location.port) : '') +
            '/webssh/?' + connect_info + '&width=' + cols + '&height=' + rows;

    var sock;
    sock = new WebSocket(socketURL);

    // 打开 websocket 连接, 打开 web 终端
    sock.addEventListener('open', function () {
        // $('#section').addClass('hide');
        //清空div原有数据，避免再次打开窗口时仍保留历史
        $('#terminal').html("");
        $('#form').addClass('hide');
        $('#webssh-terminal').removeClass('hide');
        term.open(document.getElementById('terminal'));
    });

    // 读取服务器端发送的数据并写入 web 终端
    sock.addEventListener('message', function (recv) {
        var data = JSON.parse(recv.data);
        var message = data.message;
        var status = data.status;
        if (status === 0) {
            term.write(message)
        } else {
            window.location.reload()
        }
    });

    /*
    * status 为 0 时, 将用户输入的数据通过 websocket 传递给后台, data 为传递的数据, 忽略 cols 和 rows 参数
    * status 为 1 时, resize pty ssh 终端大小, cols 为每行显示的最大字数, rows 为每列显示的最大字数, 忽略 data 参数
    */
    var message = {'status': 0, 'data': null, 'cols': null, 'rows': null};

    // 向服务器端发送数据
    term.on('data', function (data) {
        message['status'] = 0;
        message['data'] = data;
        var send_data = JSON.stringify(message);
        sock.send(send_data)
    });

    // 监听浏览器窗口, 根据浏览器窗口大小修改终端大小
    $(window).resize(function () {
        var cols = get_term_size().cols;
        var rows = get_term_size().rows;
        message['status'] = 1;
        message['cols'] = cols;
        message['rows'] = rows;
        var send_data = JSON.stringify(message);
        sock.send(send_data);
        term.resize(cols, rows)
    })
}
