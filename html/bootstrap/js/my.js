var path = "http://127.0.0.1:8000/"

$.extend({
    'load': function () {
        $.ajax({
            url: path + "list/",
            type: "GET",
            dataType: "json",//请求的数据类型
            timeout: 5000,
            success: function (returnData) {
                $.insert_table(returnData.datas)
            }
        });
    },
    'dateFormat': function (fmt, date) {
        let ret;
        const opt = {
            "Y+": date.getFullYear().toString(),        // 年
            "m+": (date.getMonth() + 1).toString(),     // 月
            "d+": date.getDate().toString(),            // 日
            "H+": date.getHours().toString(),           // 时
            "M+": date.getMinutes().toString(),         // 分
            "S+": date.getSeconds().toString()          // 秒
            // 有其他格式化字符需求可以继续添加，必须转化成字符串
        };
        for (let k in opt) {
            ret = new RegExp("(" + k + ")").exec(fmt);
            if (ret) {
                fmt = fmt.replace(ret[1], (ret[1].length == 1) ? (opt[k]) : (opt[k].padStart(ret[1].length, "0")))
            }
        }
        return fmt;
    },
    'search_list': function (time1) {
        $.ajax({
            url: path + "search/",
            type: "GET",
            // contentType: "application/json;charset=UTF-8",
            data: {
                "get_time": time1,
            },
            dataType: "json",//请求的数据类型
            timeout: 5000,
            success: function (returnData) {
                $.insert_table(returnData.datas)
                if (returnData.flag == true) {
                    setTimeout($.search_list(time1), 10 * 1000);
                }
                $("#state").html('结束')
            }
        });
    },
    'search_start': function (keys_list, search_engines, page_count, get_time) {
        $.ajax({
            url: path + "search/",
            type: "POST",
            contentType: "application/json;charset=UTF-8",
            data: JSON.stringify({
                "keys_list": keys_list,
                "search_engines": search_engines,
                "page_count": page_count,
                "get_time": get_time
            }),
            dataType: "json",//请求的数据类型
            timeout: 5000,
            success: function (returnData) {
                console.log(returnData)
            }
        });
    },
    'insert_table': function (datas) {
        $('#mytab').bootstrapTable('destroy');
        $('#mytab').bootstrapTable({
            data: datas,//请求路径
            striped: true, //是否显示行间隔色
            pagination: true,//是否分页
            // 如果设置了分页，首页页码
            pageNumber: 1,
            // 每页的记录行数
            pageSize: 10,
            // 可供选择的每页的行数
            pageList: [5, 50, 100],
            sidePagination: 'client',//服务端处理分页,客户端处理则为 client 服务器server
            columns: [{
                checkbox: true,
                align: 'center',
                width: '20px'
            }, {
                title: 'ID',
                field: 'id',
                sortable: true,
                width: '40px'
            }, {
                title: '标题',
                field: 'title',
                width: '150px'
            }, {
                title: '关键字',
                field: 'keyword',
                width: '60px'
            }, {
                title: '来源',
                field: 'source',
                width: '40px'
            },
                {
                    title: '抓取时间',
                    field: 'get_time',
                    width: '90px'
                },
                {
                    title: 'URL',
                    field: 'url',
                    width: '180px'
                }]
        });
    },
    'search_run': function () {
        var keylist = $.trim($("#keylist").val());
        var search_engines = new Array();
        $(".checkbox").find('input:checkbox').each(function () { //遍历所有复选框
            if ($(this).prop('checked') == true) {
                search_engines.push($(this).val())
            }
        });
        var page_count = $("#page_count").val()
        if (keylist.length > 0 && search_engines.length > 0 &&page_count.length>0) {
            var keylist_array = new Array();
            keylist_array = keylist.split("\n");
            $("#state").html('运行中')
            flag = true
            let date = new Date()
            var get_time = $.dateFormat("YYYY-mm-dd HH:MM:SS", date)
            $.search_start(keylist_array, search_engines, page_count, get_time)
            $.search_list(get_time)
        }
    },
    'getCheckS': function () {
        var rows = $("#mytab").bootstrapTable('getSelections'); // 获得要删除的数据
        var ids = new Array(); // 声明一个数组
        $(rows).each(function () { // 通过获得别选中的来进行遍历
            ids.push(this.id); // cid为获得到的整条数据中的一列
        });
        return ids
    },
    'del': function (ids) {
        $.ajax({
            url: path + "info/",
            type: "DELETE",
            contentType: "application/json;charset=UTF-8",
            data: JSON.stringify({
                "ids": ids,
            }),
            dataType: "json",//请求的数据类型
            timeout: 5000,
            success: function (data) {
                console.log(data)
                if (data.code == 200) {
                    $.load()
                }
            }
        });
    },
    'btn_del': function () {
        if (!confirm("是否确认删除？"))
            return;
        ids = $.getCheckS()
        //后端删除的方法
        $.del(ids)
    },
    'search_key': function () {
        var key = $("#search_text").val()
        if (key.length > 0) {
            $.ajax({
                url: path + "list/",
                type: "GET",
                // contentType: "application/json;charset=UTF-8",
                data: {
                    "keyword": key,
                },
                dataType: "json",//请求的数据类型
                timeout: 5000,
                success: function (returnData) {
                    $.insert_table(returnData.datas)
                }
            });
        }
    },
    'get_one': function (id) {
        $.ajax({
            url: path + "info/",
            type: "GET",
            // contentType: "application/json;charset=UTF-8",
            data: {
                "id": time1,
            },
            dataType: "json",//请求的数据类型
            timeout: 5000,
            success: function (returnData) {
                $.insert_table(returnData.datas)
                var title = $('<h2>', {
                    text: returnData.datas.title
                });
                title.appendTo('body');
                var content = $('<h2>', {
                    text: returnData.datas.content
                });
                title.appendTo('content');
            }
        });
    },
    'btn_see': function () {
        ids = $.getCheckS()
        $(ids).each(function () {
            window.location = 'Article.html?id=' + this;
        });
    }
});
$($.load());
$("#btn_run").click($.search_run);
$("#btn_repeat").click($.load);
$("#btn_delete").click($.btn_del)
$("#btn_key").click($.search_key)
$("#btn_see").click($.btn_see)