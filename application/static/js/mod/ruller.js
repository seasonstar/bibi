define('mod/ruller', ['mod/jquery', 'mod/bubble'], function($, bubble) {
    return function(fn) {
        return (function(R) {
            R.prototype = {
                init: function(dataList, dom, cfg) {
                    this.data = dataList;
                    return (function(self){

                        if (cfg && cfg.css) {
                            self.css = cfg.css;
                        }
                        if (cfg && cfg.flagCss) {
                            self.flagCss = cfg.flagCss;
                        }
                        self.ruller = $(self.rullerTpml).css(self.css);
                        dataList.map(function(d) {
                            self.ruller.append($(self.elementsTpml).css({
                                width: self.ruller.width()/dataList.length
                            }).html(d).css({
                                display: 'inline-block'
                            }));
                        });
                        self.ruller.appendTo($(dom));
                        self.ruller.on('click', '.r-element', function(e) {
                            console.log('click')
                            e.preventDefault();
                            self.select($(this));
                            return false;
                        });
                        self.inited = true;
                        return self;
                    })(this)
                },
                initDis: function(dom) {
                    $('#r-show').remove();
                    return $('<div id="r-show" selectable="false"></div>').appendTo(dom)
                },
                initIndex: function(max, fn) {
                    var ruller = this.ruller;
                    var indexF = this.indexF = $(this.indexTpml).css({
                        color: this.css.color,
                        position: 'absolute',
                        left: this.ruller.offset().left,
                        top: this.ruller.offset().top + 30
                    }).appendTo($('body')).html('↑');
                    var indexT = this.indexT = $(this.indexTpml).css({
                        color: this.css.color,
                        position: 'absolute',
                        left: this.ruller.offset().left + this.ruller.width(),
                        top: this.ruller.offset().top + 30
                    }).appendTo($('body')).html('↑');
                    var data = this.data;

                    [this.indexT, this.indexF].map(function(i) {
                        i.bind('mousedown', function(e) {
                            $(this).addClass('r-dragging');
                            (function(self) {
                                $(document).bind('mousemove', function(e) {
                                    self.css({
                                        left: e.offsetX < ruller.offset().left?
                                            ruller.offset().left:
                                            e.offsetX > ruller.offset().left + ruller.width()?
                                            ruller.offset().left + ruller.width():
                                            e.offsetX,
                                    });
                                    $('.bubble').remove();
                                    self[0].data = (e.offsetX - ruller.offset().left)/ruller.width()*data[data.length-1];
                                    bubble(self, parseInt(self[0].data), function() {

                                    }, {
                                        x: -20,
                                        y: 50
                                    });
                                });
                                $(document).bind('mouseup', function(e) {
                                    $(document).unbind('mousemove');
                                    fn.call(this, indexF, indexT);
                                })
                            })($(this));
                        })
                    });

                    return this;
                },
                select: function(ele) {
                    if ($('.r-element.r-selected').length >= 2) {
                        $('.r-selected', this.ruller).removeClass('r-selected')
                    }
                    $(ele).addClass('r-selected')
                    return this;
                },
                remove: function() {
                    this.ruller && this.ruller.remove();
                    this.indexT && this.indexT.remove()
                    this.indexF && this.indexF.remove()
                    delete this;
                }
            };
            return fn.call(this, new R());
        })(function() {
            this.rullerTpml = "<div class='r-ruller'></div>";
            this.elementsTpml = "<label class='r-element'></label>";
            this.indexTpml = "<label class='r-index'></label>";
            this.css = {
                width: '300px',
                color: '#fff'
            };
        });
    }
    
})
