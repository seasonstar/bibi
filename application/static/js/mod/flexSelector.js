define('mod/flexSelector', ['jquery', 'underscore', 'mod/rune'], function($, _, R) {
    return function(fn, cfg, cb) {
        (function(O) {
            O.prototype = {
                init: function(selector, title) {
                    this.wrap.appendTo($(selector).css('position', 'relative'));
                    return this;
                },
                data: function(data) {
                    (function(self) {
                        _.map(data, function(d){
                            $(self.itemTpml).html(d).css(self.item_css)
                                .appendTo(self.wrap)
                                .hover(function(){
                                    $(this).css('color', '#09d')
                                }, function() {
                                    $(this).css('color', '#08c')                                    
                                });
                        });
                    })(this)
                    return this;
                },
                added: function(fn) {
                    this._added = fn;
                    return this;
                },
                show: function() {
                    $('.item', this.wrap).css('display', 'block');
                    return this;
                },
                hide: function() {
                    $('.item', this.wrap).css('display', 'none');
                    return this;
                },
                hover: function(fh, fb) {
                    this.wrap.hover(fh, fb);
                    return this;
                }
            }
            fn(new O())
        })(function(cfg) {
            this.wrap = $("<ul class='selector'></ul>");
            this.edit = $("<li class='editable'>Add New</li>");
            this.itemTpml = "<li class='item'>%s</li>";
            if (cfg && cfg.flexiable) {
                cfg.flexText? editTpml.html(cfg.flexText): void(0);
                this.wrap.html(this.edit);
            };
            this.wrap.css({
                'top': '15px',
                'left': '-50px',
                'position': 'absolute',
                'display': 'inline-block',
                'z-index': 1000,
                'list-style-type': 'none',
                'background-color': '#fff'
            });
            this.item_css = {
                'display': 'block',
                'width': 'auto',
                'min-width': '100px',
                'height': '20px',
                'margin': '0',
                'padding': '5px 0',
                'color': '#08c',
                'background-color': '#fff'
            };
            R(this.wrap ,function(R){
                //
            })
        })
    }
})
