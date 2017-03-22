define('mod/bubble', ['mod/jquery'], function($) {
    return function(dom, text, fn, bias) {
        return (function(self) {
            return (function(bubble){
                bubble.css({
                    left: dom.offset().left + 20 + (bias&&bias.x || 0),
                    top: dom.offset().top - 20 + (bias&&bias.y || 0)});
                return fn.call(self, bubble);
            })($(self.tpml.replace('%s', text))
               .appendTo($('body'))
               .css(self.style)
               .attr(self.attr))
        })({
            tpml: "<div class='bubble'><span>%s</span></div>",
            style: {
                'position': 'absolute',
                'display': 'block',
                'z-index': '1500'
            },
            attr: {
                selectable: 'false'
            }
        })
    }
})
