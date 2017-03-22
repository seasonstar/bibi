define('mod/ajaxUploader', ['mod/jquery'], function($) {
	return function(settings){
		$(settings.target).on('click',function(o){
            var uploader = $(o.currentTarget);
			var input = $('<input type="file" id="uploader" style="display:none" />');
			if (settings.multiple) {
				input.attr('multiple','multiple'); // 多文件上传
			}
			input.change(function(){
				if (this.value != '') {
					var fd = new FormData();
					for (var i = 0; i < this.files.length; i++) {
						fd.append('upload_'+i, this.files[i]);
					}
                    fd.append('id', uploader.data('id'));
					var xhr = new XMLHttpRequest();
					if (settings.progress) {
						xhr.upload.addEventListener("progress",settings.progress,false);
					}
					if (settings.load) {
						xhr.addEventListener('load',settings.load,false);
					}
					xhr.open('POST', uploader.data('url'));
					xhr.setRequestHeader('X-Requested-With','XMLHttpRequest');
					xhr.send(fd);
				}
			}).appendTo('body').click();
			return false;
		})
	}
})
