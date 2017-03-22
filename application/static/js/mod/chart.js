define('mod/chart', ['mod/jquery',
                     'underscore',
                     'mod/canvas',
                     'mod/svg',
                     'mod/bubble'],
       function($, _, Cvs, Svg, bubble) {
           return function(fn) {
               return (function(Obj) {
                   Obj.prototype = {
                       init: function(tar) {
                           this.cvs = Cvs(function(C){
                               C.init({tar:tar});
                               return C;
                           });
                           this.svg = Svg(function(S){
                               S.init({tar:tar});
                               return S
                           })
                           this.inited = true;
                           return this;
                       },
                       showBubble: function(obj, data) {
                           $(obj).hover(function(e){
                               e.preventDefault();
                               $(this).attr('r', 10);
                               bubble($(this), data, function(b) {
                               })
                           }, function(e) {
                               e.preventDefault();
                               $(this).attr('r', 5);
                               $('.bubble').remove();
                           })
                           return this;
                       },
                       clear: function() {
                           this.cvs.ctx.strokeStyle = this.defaultColor;
                           this.cvs.ctx.fillStyle = this.defaultColor;
                           return this;
                       },
                       drawCoordinates: function(cfg) {
                           (function(self) {
                               self.cvs.ctx.beginPath();
                               self.clear();
                               self.cvs.ctx.strokeStyle = cfg.coordColor || self.defaultColor;
                               self.cvs.ctx.fillStyle = cfg.textColor || self.defaultColor;
                               cfg.title?
                                   (function(x, y) {
                                       self.cvs.ctx.font = "14px Arial";
                                       self.cvs.ctx.fillText(cfg.title, x, y);
                                       self.cvs.ctx.stroke();
                                   })(cfg.titlePosi && cfg.px + cfg.titlePosi.x || (cfg.px + cfg.w/2 - 20),
                                      cfg.titlePosi && cfg.py - cfg.h - cfg.titlePosi.y || cfg.py - cfg.h):
                                   void(0);
                               self.cvs.ctx.font = "9px Arial";                          
                               self.cvs.ctx.moveTo(cfg.px, cfg.py);
                               self.cvs.ctx.lineTo(cfg.px + cfg.w, cfg.py);
                               self.cvs.ctx.moveTo(cfg.px, cfg.py);
                               self.cvs.ctx.lineTo(cfg.px, cfg.py - cfg.h);
                               self.cvs.ctx.stroke();
                               (function(sx, sy, data) {
                                   self.cvs.ctx.beginPath();
                                   self.clear();
                                   self.cvs.ctx.moveTo(cfg.px, cfg.py);
                                   _.each(cfg.dx, function(x, i) {
                                       self.cvs.ctx.moveTo(i * sx + cfg.px, cfg.py)
                                       self.cvs.ctx.lineTo(i * sx + cfg.px, cfg.py + 10)
                                       self.cvs.ctx.fillText(x, i * sx + cfg.px - 5, cfg.py + 20);
                                   });
                                   self.cvs.ctx.moveTo(cfg.px, cfg.py);
                                   _.each(cfg.dy, function(y, i) {
                                       self.cvs.ctx.moveTo(cfg.px, cfg.py - i * sy)
                                       self.cvs.ctx.lineTo(cfg.px - 10, cfg.py - i * sy)
                                       self.cvs.ctx.fillText(y, cfg.px - 40, cfg.py - i * sy + 5)
                                   });
                                   self.cvs.ctx.stroke();
                               })(cfg.w/cfg.dx.length,
                                  cfg.h/cfg.dy.length, cfg.data)
                           })(this)
                           return this;
                       },
                       showData: function(cfg, sx, sy, data) {
                           self.cvs.ctx.beginPath();
                           self.clear();
                           self.cvs.ctx.moveTo(cfg.px, cfg.py);
                           _.each(cfg.dx, function(x, i) {
                               self.cvs.ctx.moveTo(i * sx + cfg.px, cfg.py)
                               self.cvs.ctx.lineTo(i * sx + cfg.px, cfg.py + 10)
                               self.cvs.ctx.fillText(x, i * sx + cfg.px - 5, cfg.py + 20);
                           });
                           self.cvs.ctx.moveTo(cfg.px, cfg.py);
                           _.each(cfg.dy, function(y, i) {
                               self.cvs.ctx.moveTo(cfg.px, cfg.py - i * sy)
                               self.cvs.ctx.lineTo(cfg.px - 10, cfg.py - i * sy)
                               self.cvs.ctx.fillText(y, cfg.px - 40, cfg.py - i * sy + 5)
                           });
                           self.cvs.ctx.stroke();
                       },
                       drawChart: function(cfg) {
                           (function(self){
                               self.drawCoordinates(cfg);
                               self.clear();
                               self.cvs.ctx.moveTo(cfg.px, cfg.py);
                               self.cvs.ctx.beginPath();
                               self.cvs.ctx.strokeStyle = cfg.lineColor || self.defaultColor;
                               (function(sx, sy, data, style) {
                                   _.each(data, function(d, i) {
                                       self.svg.drawCircle(i * sx + cfg.px,
                                                           cfg.py - (1 - sy/cfg.h) * d * cfg.h/cfg.dy[cfg.dy.length -1],
                                                           5, style,
                                                           function(obj) {
                                                               self.showBubble(obj[0][0], d);
                                                           });
                                       self.cvs.ctx.lineTo(i * sx +cfg.px,
                                                           cfg.py - (1 - sy/cfg.h) * d * cfg.h/cfg.dy[cfg.dy.length -1], 5);

                                   });
                               })(cfg.w/cfg.dx.length,
                                  cfg.h/cfg.dy.length, cfg.data,
                                  {
                                      'fill': cfg.lineColor || self.defaultColor,
                                      'stroke-width': '1',
                                      'stroke': cfg.lineColor || self.defaultColor
                                  })
                               self.cvs.ctx.stroke();
                           })(this)
                       },
                       remove: function() {
                           this.cvs.remove();
                           this.svg.remove();
                           delete this;
                       }
                   }
                   return fn.call(this, new Obj())
               })(function() {
                   this.defaultColor = "#01DFFC";
               })
           }
})
