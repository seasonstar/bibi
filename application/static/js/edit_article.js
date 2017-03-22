require.config({
  paths: {
    jquery: 'libs/require-jquery',
    underscore: 'libs/underscore',
    backbone: 'libs/backbone',
    text: 'libs/text',
  },
  urlArgs: "bust=" +  Date.now()
});


define(function (require) {
  var $                 = require('jquery');
  var ajaxForm          = require('mod/ajaxForm');

  $('ul.nav-second-level').toggle(400);
  $('#side-menu li').click(function () {
    $(this).children('ul.nav-second-level').toggle(400);
  });


  $('.upload-img').each(function() {
    $this = $(this);
    ajaxForm($(this), function(r) {
        window.setTimeout(function() {
            (function(cfg) {
                $(cfg.tar).find('img').attr('src', r.url);
                $.ajax({
                    url: $(cfg.tar).data('api'),
                    type: 'post',
                    data: {img: r.url,
                           id: $(cfg.tar).attr('id')}
                });
            })({tar: $this.data('target')
               })
        }, 5000);
    })
  });
  $('.drop-area').on('dragend', '.draggable', function(e) {
      (function(a, b) {
          $.ajax({
              url: $('.drop-area').data('api'),
              type: "PATCH",
              data: {from: a.data('id'), to: b.data('id')},
              success: function(r) {
                if (r.message === 'OK') {
                  var copy_a = $(a).clone(true);
                  var copy_b = $(b).clone(true);
                  $(a).replaceWith(copy_b);
                  $(b).replaceWith(copy_a)
                }
              }
          })
      })($(e.currentTarget), $($('.over')[0]))

  }).on("dragover", '.draggable', function(e) {
      e.preventDefault();
      e.stopPropagation();
      $(e.currentTarget).addClass('over')
      return false;
  }).on("dragleave", '.draggable', function(e) {
      e.preventDefault();
      e.stopPropagation();
      $(e.currentTarget).removeClass('over')
      return false;
  });

});
