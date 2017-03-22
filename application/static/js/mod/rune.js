define('mod/rune', ['jquery', 'underscore'], function($, _){
    return function(dom, handle,  callback) {
        (function(Fn, hd, cb) {
            Fn.prototype = {
                init: function() {
                    (function(self) {
                        self.dom
                            .on('DOMSubtreeModified', '.editable', function(e) {
                                e.preventDefault();
                                $(this).addClass('edited');
                                self._onEdit? self._onEdit.call(this): void(0)
                            }).on('blur', '.editable', function(e) {
                                e.preventDefault();
                                self._onEdited? self._onEdited.call(this): void(0)
                            })
                        
                    })(this)
                    return this;
                },
                cache: function() {
                    this._cache = this.data();
                    return this;
                },
                data: function() {
                    return (function(data){
                        _.each($('.editable', dom), function(o) {
                            (function(o){
                                data[o.data('key')] = o.text();
                            })($(o));
                        })
                        return data;
                    })({});
                },
                switch: function() {
                    _.each($('.editable', dom), function(o) {
                        (function(o){
                            o.attr('contenteditable') == 'true' ?
                                o.attr('contenteditable', 'false'):
                                o.attr('contenteditable', 'true');
                        })($(o))
                    });
                    return this;
                },
                onEdit: function(fn) {
                    this._onEdit = fn;
                    return this;
                },
                onEdited: function(fn) {
                    this._onEdited = fn;
                    return this;
                }
                
            }
            hd.call(this, new Fn())
            if (cb) return cb.call(this)
        })(function() {
            (function(self) {
                self.dom = $(dom);
                self._cache = {};
            })(this);
        }, handle, callback);
    }
})
