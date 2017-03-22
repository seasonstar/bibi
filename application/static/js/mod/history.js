define('mod/history', ['underscore'], function(_) {
    return function(fn) {
        return (function (His){
            His.prototype = {
                record: function(fn, args) {
                    this.stack.push({fn:fn, args: args,
                                       time: Date.now()});
                    fn.apply(this, args); // fn should not have side effect such as IO Fn.
                    return this.record;
                },
                call: function(from, to) {
                    (function(self) {
                        _.each(self.stack.slice(from, to), function(obj) {
                            obj.fn.apply(self, obj.args)
                        })                        
                    })(this)
                }
            }
            return fn.call(this, new His());
        })(function() {
            this.stack = [];
        })
    }
})
