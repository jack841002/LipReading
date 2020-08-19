// 新增
$("#addButton").click(function(){
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: '{{ csrf_token }}' },
    });

    var fm = new FormData()
    var addFile = document.getElementById('addFile').files[0]    // 獲取上傳的檔案物件
    console.log(addFile)                                        // 列印檔案物件
    var addText = $("#addText").val();
    if(addFile == null || addText == ""){
        alert("請選擇影片並填寫文本標籤");
        return
    }
    fm.append('file', addFile)
    fm.append('text', addText)

    $.ajax({
        url: '/addData/',                             //後端的URL
        type: 'POST',                               //response的資料格式
        cache: false,
        contentType: false,
        processData: false,
        data: fm,                                    //傳送給後端的資料
        dataType:"json",

        success: function(response_result) {
            result = response_result['result'];
            $('#addText').val(result);
        },
        error: function(xhr) {
            console.log(xhr.responseText);
            alert("失敗");
        }
    });
});

// 訓練
$("#trainButton").click(function(){
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: '{{ csrf_token }}' },
    });

    var send = "train"
    $.ajax({
        url: '/trainData/',                             //後端的URL
        type: 'POST',                               //response的資料格式
        data: {                                     //傳送給後端的資料
            'train': send,
        },
        dataType:"json",

        success: function(response_result) {
            result = response_result['result'];
            alert(result);
        },
        error: function(xhr) {
            console.log(xhr.responseText);
            alert("失敗");
        }
    });
});

// 預測
$("#predictButton").click(function(){
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: '{{ csrf_token }}' },
    });

    var fm = new FormData()
    var predictFile = document.getElementById('predictFile').files[0]    // 獲取上傳的檔案物件
    console.log(predictFile)                                        // 列印檔案物件
    // var predictText = $("#predictText").val();
    if(predictFile == null){
        alert("請選擇要預測的影片");
        return
    }
    fm.append('file', predictFile)

    $.ajax({
        url: '/predictData/',                             //後端的URL
        type: 'POST',                               //response的資料格式
        cache: false,
        contentType: false,
        processData: false,
        data: fm,                                    //傳送給後端的資料
        dataType:"json",

        success: function(response_result) {
            result = response_result['result'];
            $('#predictText').val(result);
        },
        error: function(xhr) {
            console.log(xhr.responseText);
            alert("失敗");
        }
    });
});
