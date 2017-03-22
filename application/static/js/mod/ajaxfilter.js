define('modules/ajaxFilter', ['jquery', 'underscore'], function($, _) {
    return function(fn) {

        (function(obj, fn) {
            obj.prototype = {
                init: function(dom) {
                    $(dom).on('click', '.filter', function(e) {
                        e.preventDefault()
                        this.select(o)
                    });
                    if (self._done) self._done.call(self)
                    return this
                },

                done: function(fn) {
                    this._done = fn
                    return this
                },

                select: function(o) {
                    (function () {
                        $.get(o.data('url'))
                            .done(function(o) {
                                this._selected_el = o
                            })
                        o.addClass(self._css_selected)                        
                    })(this)
                    return this
                },

                render: function(fn) {
                    if (this._selected_el)
                        fn.call(this._selected_el)
                    return this
                }
            }

            fn.call(this, obj)

        }) (function() {
            this._moduleName = 'modules/ajaxFilter',
            this._css_select = 'on',
            this._selected_el = ''
       })
    }
})
