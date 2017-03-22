define('mod/canvas', ['mod/jquery'], function($) {
    return function(fn) {
        return (function(Cvs) {
            Cvs.prototype = {
                init: function(cfg) {
                    this.canvas.attr('width', cfg&&cfg.w || window.innerWidth);
                    this.canvas.attr('height', cfg&&cfg.h || window.innerHeight * 2);
                    this.canvas.appendTo(cfg && cfg.tar && $(cfg.tar) || $('body'))
                        .css({'position': 'absolute'});
                    return this;
                },
                resize: function(w, h) {
                    (function(img, canvas, self) {
                        img.src = canvas[0].toDataURL();
                        canvas.attr('width', w || window.innerWidth);
                        canvas.attr('height', h || window.innerHeight * 2);
                        self.ctx.drawImage(img, 0, 0)
                    })(new Image(), this.canvas, this)
                    return this;
                },
                lineTo: function(x, y) {
                    this.ctx.lineTo(x, y);
                    return this;
                },
                moveTo: function(x, y) {
                    this.ctx.moveTo(x, y);
                    return this;
                },
                stroke: function() {
                    this.ctx.stroke();
                    return this;
                },
                beginPath: function() {
                    this.cxt.beginPath();
                    return this;
                },
                remove: function() {
                    this.canvas.remove();
                    delete this;
                }
            }
            return fn.call(this, new Cvs());
        })(function() {
            this.canvas = $("<canvas></canvas>");
            this.ctx = this.canvas[0].getContext('2d');
        })
    }
})
