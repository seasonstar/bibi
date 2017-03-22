define('mod/nodeTree', ['mod/jquery',
                        'underscore',
                        'mod/canvas',
                        'mod/svg',
                        'mod/bubble'],
       function($, _, Cvs, Svg, bubble) {
           return function(fn) {
               return (function(Tree, Node, Cvs, Svg, cfg) {
                   Node.prototype = {
                       show: function(x, y) {
                           return (function(self) {
                               self.x = x;
                               self.y = y;
                               console.log(self.color)
                               self.dom = Svg.drawCircle(x, y, 20, {
                                   
                                   'fill': self.color,
                                   'stroke-width': '1',
                                   'stroke': self.color,
                               }, function(obj) {
                                   self.showBubble(obj[0][0], self.data);
                                   self.enableDrag(obj[0][0]);
                                   return self;
                               });
                               return self;
                           })(this);
                       },
                       showChild: function(nodeList, r) {
                           return (function(self) {
                               _.map(nodeList, function(n, i) {
                                   n.move(self.x + r * Math.sin(Math.pi / 4 + i * Math.pi / 36),
                                          self.y - r * Math.cos(Math.pi / 4 + i * Math.pi / 36));
                                   Cvs.moveTo(self.x, self, y);
                                   Cvs.lineTo(self.x + r * Math.sin(Math.pi / 4 + i * Math.pi / 36),
                                                  self.y - r * Math.cos(Math.pi / 4 + i * Math.pi / 36));
                                   Cvs.stroke();
                               });
                               return self;
                           })(this);
                       },
                       move: function(x, y) {
                           this.x = x;
                           this.y = y;
                           this.dom.attr({cx: this.x, cy: this.y});
                           return this;
                       },
                       showBubble: function(obj, data) {
                           $(obj).hover(function(e){
                               $(this).attr('r', 40);
                               bubble($(this), data, function(b) {
                               });
                           }, function(e) {
                               $(this).attr('r', 20);
                               $('.bubble').remove();
                           });
                           return this;                               
                       },
                       enableDrag: function(obj) {
                           return (function(self) {
                               $(obj).on('mousedown', function(e) {
                                   self.move(e.offsetX, e.offsetY);
                                   $(document).bind('mousemove', function(e) {
                                       self.move(e.offsetX, e.offsetY);                                       
                                   });
                                   return self;
                               });
                               $(obj).on('mouseup', function(e) {
                                   $(document).unbind('mousemove');
                               });                               
                           })(this);

                       },
                       add: function(node) {
                           this.child.push(node);
                           return this;
                       },
                       refact: function() {
                           return showChild();
                       }
                   };
                   Tree.prototype = {
                       init: function(x, y, cfg) {
                           Cvs.init();
                           Svg.init();
                           cfg&&cfg.color? this.color=cfg.color:void(0);
                           this.Node = Node;
                           this.inited = true;
                           return this;
                       },
                       setRoot: function(x, y, data, cfg) {
                           return (function(node, self) {
                               self.roots.push(node);
                               //Svg.dropShadow(node.dom);
                               return self;
                           })((new Node(x, y, data, 'root', cfg)).show(x, y), this)
                       },
                       add: function(node, data, x, y) {
                           node.add(new Node(x, y, data));
                           node.showChild();
                           return this;
                       },
                       DFS: function(node, key) {
                           return node.subNode.length?
                               (function() {
                                   return (function(res) {
                                       return res.legnth && res;
                                   })(node.subNode.filter(function(n) {
                                       return this.DFS(n, key);
                                   }));
                               })(): (function() {
                                   return node.key == key;
                               })();
                       },
                       remove: function() {
                           Cvs.remove();
                           Svg.remove();
                           delete this;
                       }
                   };
                   return fn.call(this, new Tree());
               })(function() {
                   this.roots = [];

                   return;
               }, function(x, y, data, key, cfg) {
                   this.color = cfg && cfg.color || '#FFF'
                   this.x = x;
                   this.y = y;
                   this.data = data;
                   this.subNode = [];
                   this.key = key;
                   return;
               }, Cvs(function(C) {
                   return C;
               }), Svg(function(S) {
                   return S;
               }), {
                   color: '#FFF'
               });
           };
       });
