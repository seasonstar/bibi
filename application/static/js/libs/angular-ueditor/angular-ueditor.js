
/**
Created by Dio on 17-9.
http://inhu.net
 */

(function() {
  "use strict";
  (function() {
    var NGUeditor;
    NGUeditor = angular.module("ng.ueditor", []);
    NGUeditor.directive("ueditor", [
      function() {
        return {
          restrict: "C",
          require: "ngModel",
          scope: {
            config: "=",
            ready: "="
          },
          link: function($S, element, attr, ctrl) {
            var _NGUeditor;
            _NGUeditor = (function() {
              function _NGUeditor() {
                this.bindRender();
                this.initEditor();
                return;
              }


              /**
               * 初始化编辑器
               * @return {[type]} [description]
               */

              _NGUeditor.prototype.initEditor = function() {
                var _UEConfig, _editorId, _self;
                _self = this;
                if (typeof UE === 'undefined') {
                  console.error("Please import the local resources of ueditor!");
                  return;
                }
                _UEConfig = $S.config ? $S.config : {};
                _editorId = attr.id ? attr.id : "_editor" + (Date.now());
                element[0].id = _editorId;
                this.editor = new UE.getEditor(_editorId, _UEConfig);
                return this.editor.ready(function() {
                  _self.editorReady = true;
                  _self.editor.addListener("contentChange", function() {
                    ctrl.$setViewValue(_self.editor.getContent());
                    if (!$S.$$phase) {
                      $S.$apply();
                    }
                  });
                  _self.setEditorContent();
                  if (typeof $S.ready === "function") {
                    $S.ready(_self.editor);
                  }
                });
              };

              _NGUeditor.prototype.setEditorContent = function(content) {
                if (content == null) {
                  content = this.modelContent;
                }
                if (this.editor && this.editorReady) {
                  this.editor.setContent(content);
                }
              };

              _NGUeditor.prototype.bindRender = function() {
                var _self;
                _self = this;
                ctrl.$render = function() {
                  _self.modelContent = (ctrl.$isEmpty(ctrl.$viewValue) ? "" : ctrl.$viewValue);
                  _self.setEditorContent();
                };
              };

              return _NGUeditor;

            })();
            new _NGUeditor();
          }
        };
      }
    ]);
  })();

}).call(this);

//# sourceMappingURL=angular-ueditor.js.map
