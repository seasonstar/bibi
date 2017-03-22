define('mod/dialog', ['jquery'], function($, window) {
    return function(html, cfg) {
        return $('<section class="dialog">%s</section>'.replace('%s', html))
            .css({
                'position': cfg && cfg.fixed == true? 'fixed': 'absolute',
                'display': 'block',
                'background-color': '#fff',
                'z-index': 1000,
                'padding': '20px',
                'top': cfg && cfg.top || '50%',
                'left': cfg && cfg.left || '50%',
                'min-width': cfg && cfg.width || '200',
                'min-height': cfg && cfg.height || '100',
            })
    }
})
