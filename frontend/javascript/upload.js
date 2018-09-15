var Upload = function (file) {
    this.file = file;
    console.log($.ajax)
};

Upload.prototype.getType = function() {
    return this.file.type;
};
Upload.prototype.getSize = function() {
    return this.file.size;
};
Upload.prototype.getName = function() {
    return this.file.name;
};
Upload.prototype.doUpload = function () {
    var that = this;
    var formData = new FormData();

    // add assoc key values, this will be posts values
    formData.append("file", this.file, this.getName());
    formData.append("upload_file", true);

    $.ajax({
        type: "POST",
        url: "http://localhost:8000/upload",
        xhr: function () {
            var myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                myXhr.upload.addEventListener('progress', that.progressHandling, false);
            }
            return myXhr;
        },
        success: function (data) {
          $('.item,.url').remove();
          for (i = 0; i < data.length; i++) {
            // 子要素（.tag)にdate[i].hashtagsを代入
              $('.tags').append(data[i].hashtags);
              // imgタグを作成
              img = $("<img>").addClass('item');
              // imgタグのsrcアトリビュートにdata[i]を代入
              img.attr('src', data[i].img_src);
              // 親要素(grid)に作成したimgタグを追加
              $('.grid').append(img);
              // 画像にリンクを追加
              img.wrap($('<div class="photo"><div class="inner"><a>').prop('href',data[i].instagram_url).addClass('url'));
            }
        },

        error: function (error) {
            console.log(error)
        },
        async: true,
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        timeout: 60000
    });
};

Upload.prototype.progressHandling = function (event) {
    var percent = 0;
    var position = event.loaded || event.position;
    var total = event.total;
    var progress_bar_id = "#progress-wrp";
    if (event.lengthComputable) {
        percent = Math.ceil(position / total * 100);
    }
    // update progressbars classes so it fits your code
    $(progress_bar_id + " .progress-bar").css("width", +percent + "%");
    $(progress_bar_id + " .status").text(percent + "%");
};
