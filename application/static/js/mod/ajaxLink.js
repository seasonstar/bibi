define('mod/ajaxLink', ['jquery'], function($) {
    return function(dom, cb) {
        dom.on('click', function(e) {
            e.preventDefault();
            return (function(self) {
                $.ajax({
                    url: self.attr('href'),
                    data: self.data(),
                    type: self.attr('type')
                }).done(cb);
                self.data('reload')?window.location.reload():void(0);
            })($(this))
            return false;
        })
    }
})
