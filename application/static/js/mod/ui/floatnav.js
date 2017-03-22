define('mod/ui/floatnav', ['jquery'], function($) {
    var _nav;
    return {
        init: function(wrap, nav) {
            $(window).bind('scroll', function() {
                nav.toArray().map(_nav = function(o) {
                    var scrollPosi = window.scrollY + wrap[0].offsetTop - wrap[0].offsetHeight;
                    var src = $(o.href.match("#.+")[0])[0];
                    if (scrollPosi > src.offsetTop && scrollPosi < src.offsetTop + src.offsetHeight) {
                        if (!$(o).parent().hasClass('on')) {
                            $('.on', wrap).removeClass('on');
                            $(o).parent().addClass('on');
                        }
                    }
                });
            });
        },
        remove: function() {
            $(window).unbind('scroll', _nav);
            delete(nav);
        }
    };
});
