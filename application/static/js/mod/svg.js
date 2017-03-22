define('mod/svg', ['mod/d3'], function(d3) {
    return function(fn) {
        return (function(Svg) {
            Svg.prototype = {
                init: function(cfg) {
                    this.svg = d3.select(cfg&&cfg.tar || 'body').append('svg');
                    this.svg.style('width', cfg&&cfg.w || window.innerWidth);
                    this.svg.style('height', cfg&&cfg.h || window.innerHeight * 2);
                    this.svg.style({'position': 'absolute',
                                     'z-index': '1000'});
                    return this;
                },
                resize: function(w, h) {
                    this.svg.attr('width', w || window.innerWidth);
                    this.svg.attr('height', h || window.innerHeight * 2);
                    return this;                    
                },
                drawRect: function(x, y, w, h, style, fn) {
                    return (function (self, obj) {
                        rect.attr({
                                x: x,
                                y: y,
                                width: w,
                                height: h
                            })
                            .style(style);
                        fn? fn.call(self, obj): void(0);
                        return obj;
                    })(this, d3.select("svg").append('rect'));
                },
                drawCircle: function(x, y, r, style, fn) {
                    return (function (self, obj) {
                        obj.attr({
                                cx: x,
                                cy: y,
                                r: r
                            })
                            .style(style);
                        fn? fn.call(self, obj): void(0);
                        return obj;
                    })(this, d3.select("svg").append('circle'))
                },
                lineTo: function(x1, y1, y2, y2) {
                    (function (self, obj) {
                        rect.attr({
                                x1: x1,
                                y1: y1,
                                x2: x2,
                                y2: y2
                            })
                            .style(style);
                        fn? fn.call(self, obj): void(0);
                    })(this, d3.select("svg").append('line'))
                    return this;
                },
                dropShadow: function(obj) {
                    (function(filter) {
                        filter.append("feGaussianBlur")
                            .attr("in", "SourceAlpha")
                            .attr("stdDeviation", 5)
                            .attr("result", "blur");
                        
                        filter.append("feOffset")
                            .attr("in", "blur")
                            .attr("dx", 5)
                            .attr("dy", 5)
                            .attr("result", "offsetBlur");

                     (function(feMerge){
                            feMerge
                                .append("feMergeNode")
                                .attr("in", "offsetBlur");

                            feMerge.append("feMergeNode")
                                .attr("in", "SourceAlpha");
                            
                        })(filter.append("feMerge"));
                    })(d3.select('svg')
                       .append('defs')
                       .append('filter')
                       .attr("id", "svg-drop-shadow")
                       .attr("height", "130%"))
                    obj.style('filter', 'url(#svg-drop-shadow)');
                },
                remove: function() {
                    $(this.svg[0][0]).remove();
                    delete this;
                }
            }
            return fn.call(this, new Svg());
        })(function() {
        })
    }
})
