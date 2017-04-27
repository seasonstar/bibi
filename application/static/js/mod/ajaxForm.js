define('mod/ajaxForm', ['jquery', 'underscore'], function($, _) {
    return function(dom, callback) {
        (function(cfg) {
            $(dom).on('click', '.submit', function(e) {
                e.preventDefault();
                $.ajax({
                    url: cfg.url,
                    type: cfg.type,
                    dataType: cfg.dataType || 'json',
                    processData: cfg.type == 'get'? true:false,
                    enctype: 'multipart/form-data',
                    contentType: cfg.type == 'get'? 'application/x-www-form-urlencoded; charset=UTF-8': false,
                    beforeSend:function(){
                        $("#loading").fadeIn();
                    },
                    timeout:30000,
                    error: function() {
                        $("#loading").fadeOut();
                        alert("响应时间过长或系统出错");
                    },
                    data: (function(res, f) {

                        _.each($('input[type!=submit]', dom), function(o) {
                            f.save(o, res, (function(o) {
                                if (o.attr('type') === 'file') {
                                    if (o[0].files) {
                                        return (function(f) {
                                            return {
                                                k: o.attr('name'),
                                                v: f
                                            }
                                        })(o[0].files.length > 1?
                                           o[0].files:
                                           o[0].files[0])
                                    }
                                } else if (o.attr('type') === 'checkbox') {
                                    if (o.is('input:checked')) {
                                        return {
                                            k: o.attr('name'),
                                            v: o.val()
                                        }
                                    }
                                } else {
                                    return {
                                        k: o.attr('name'),
                                        v: o.val()
                                    }
                                }
                            })($(o)))
                        });
                        _.each($('textarea', dom), function(o) {
                            f.save(o, res, (function(o) {
                                return {
                                    k: o.attr('name'),
                                    v: o.val()
                                }
                            })($(o)))
                        });

                        _.each($('select', dom), function(o) {
                            f.save(o, res, (function(o) {
                                return {
                                    k: o.attr('name'),
                                    v: $('option:selected', o).val()
                                }
                            })($(o)))
                        });
                        return res;
                    })(cfg.type === 'get'?
                       {}:
                       new FormData(),
                      {
                          save: function(o, d, r) {
                              if ($(o).attr('required')&&!r.v) {
                                  throw('required field cant be empty')
                              }
                              if (r != undefined){
                                  cfg.type === 'get'?
                                    d[r.k] = r.v:
                                    d.append(r.k, r.v);
                              }
                          }
                      }),
                }).done(function (r) {
                    if (callback) callback.call(this, r, e);
                    $("#loading").fadeOut();
                });
            })

        })((function(o) {
            if (o.is('form')) {
                return {
                    type: o.data('type') || o.attr('method'),
                    url: o.data('url') || o.attr('action'),
                    dataType: o.data('data-type')
                }
            } else {
                return {
                    type: o.data('type'),
                    url: o.data('url'),
                    dataType: o.data('data-type')
                }
            }
        })(dom))
    }
});
