require.config({
  paths: {
    jquery: 'libs/require-jquery',
    underscore: 'libs/underscore',
    backbone: 'libs/backbone',
    text: 'libs/text'
  },
  urlArgs: "bust=" +  Date.now()
});

define(function (require) {
  var $ = require('jquery');
  var _ = require('underscore');
  var ajaxForm = require('mod/ajaxForm');
  var dialog = require('mod/dialog');
  var mall_source_dlg = require('text!templates/mall_source_dialog.html');

  _.each($('.ajax-form'), function(o){
      ajaxForm($(o), function(r) {
          if (r.message == 'OK') {
              window.setTimeout(function() {
                  $($(o).data('target')).attr('src', r.url);
              }, 3000)
          };
      });
  });
  $('ul.nav-second-level').toggle(400);
  $('#side-menu li').click(function () {
    $(this).children('ul.nav-second-level').toggle(400);
  });

  $('.btn-xs.link').click(function(e) {
      window.location = $(this).attr('href');
      return false;
  });

  $('.btn-xs.cancel').click(function(e) {
      e.preventDefault();
      window.confirm('Cancel, make sure plz!')?
      $.ajax({
          url: $(this).attr('href'),
          type: 'get',
          data: {
              reason: window.prompt('put some reason.')
          },
          success: function() {
              window.location.reload();
          }
      }): void(0);
      return false;
  });

    _.map($('.mall-source-section'), function(f) {
        ajaxForm($(f), function(r, e) {
            $('.dialog').remove();
            (function (dlg) {
                ajaxForm($('.ajax-form', dlg), function(r, e) {
                    var remark = dlg.find('input[name="remark"]').val();
                    var lid = dlg.find('input[name="lid"]').val();
                    var curr_panel = $('li#'+lid);
                    curr_panel.find('.order_remark').text('Order Remark: '+remark);
                    dlg.remove();
                })
            })(
                dialog(_.template(mall_source_dlg, data=r), {
                    left: e.pageX - 300,
                    top: e.pageY,
                    width: 300
                }).css({
                    'background-color': '#fff',
                    'border': '1px solid #ddd',
                    'padding': '20px'
                }).appendTo('body').on('click', '.cancel', function(e) {
                    e.preventDefault();
                    $(e.delegateTarget).remove();
                }))
            });
        })

    $('.panel-heading').click(function (e) {
        e.preventDefault();
        var hidden = $(this).parent().find('.panel-body');
        hidden.hasClass('hide')?hidden.removeClass('hide'):hidden.addClass('hide');
    });

    $('div.expandContent').hide();
    $('div.item').hover(function() {
        $('div.expandContent', this).toggle();
    });

});
