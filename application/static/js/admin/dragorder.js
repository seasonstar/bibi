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
                  $(b).replaceWith(copy_a);
                  copy_a.find('.banner-order').html(r.bfrom);
                  copy_b.find('.banner-order').html(r.bto);
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
