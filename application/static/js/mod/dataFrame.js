define('mod/dataFrame', ['mod/rune', 'mod/jquery'], function(R) {
    return function(handel, kwargs) {
        return (function (Sheet){
            Sheet.prototype = {
                addRow: function() {
                    var row = $($('tr', this.dom)[1]).clone();
                    row.children().text('');
                    this.dom.append(row);
                    return this;
                },
                delRow: function() {
                    var rows = $('tr', this.dom);
                    $(rows[rows.length-1]).remove();
                    return this;
                },
                addCol: function() {
                    var rows  = this.dom.children('tr')
                    $('tr', this.dom).toArray().map(function(o, i) {
                        var td = $($('td, th', $(o))[1]).clone();
                        $(o).append(td.text(''));
                    })
                    return this;
                },
                delCol: function() {
                    $('tr', this.dom).toArray().map(function(o) {
                        var cols = $('th, td', o);
                        $(cols[cols.length-1]).remove();
                    })
                    return this;
                },
                data: function() {
                    var rows = $('tr', this.dom);
                    var columns = $('th', $(rows[0])).toArray().slice(1).map(function(o, i) {
                        return $(o).text();
                    })
                    var data = rows.toArray().slice(1).map(function(o) {
                        key = $('th', $(o)).text()
                        if (key) {
                            return [key, $('td', $(o)).toArray().map(function(o) {
                                return $(o).text();
                            })]
                        }
                    })
                    return {
                        data: data,
                        columns: columns
                    }
                },
                remove: function() {
                    delete this;
                }
            }
            return handel.call(this, new Sheet(kwargs));
        })(function(kwargs) {
            this.dom = kwargs.dom;
        });
    }
})
