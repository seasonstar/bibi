define('mod/scroll', ['jquery'], function($) {
    return function(fn) {
        (function(obj) {
            obj.prototype = {
                init: function(fn) {
                    (function(self){
                        self.loading.appendTo($('body'));
                        $(window).bind('scroll', function(e) {
                            (function(loading) {
                                loading.offset().top - $(window).scrollTop() <
                                    screen.height && !loading.hasClass('locked') ?
                                    (function() {
                                        fn.call(self, e)
                                    })(): void(0)
                            })(self.loading)
                        })
                    })(this)
                },
                lock: function() {
                    this.loading.addClass('locked')
                },
                unlock: function() {
                    this.loading.removeClass('locked')
                }
            }
            fn.call(this, new obj);
        })(function() {
            this.loading = $("<div class='loading'></div>");
        })
    }
});
