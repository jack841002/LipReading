
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
