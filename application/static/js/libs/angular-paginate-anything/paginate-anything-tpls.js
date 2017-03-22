(function() {
  'use strict';

  // 1 2 5 10 25 50 100 250 500 etc
  function quantizedNumber(i) {
    var adjust = [1, 2.5, 5];
    return Math.floor(Math.pow(10, Math.floor(i/3)) * adjust[i % 3]);
  }

  // the j such that quantizedNumber(j) is closest to i
  function quantizedIndex(i) {
    if(i < 1) { return 0; }
    var group = Math.floor(Math.log(i) / Math.LN10),
        offset = i/(2.5 * Math.pow(10, group));
    if(offset >= 3) {
      group++;
      offset = 0;
    }
    return 3*group + Math.round(Math.min(2, offset));
  }

  function quantize(i) {
    if(i === Infinity) { return Infinity; }
    return quantizedNumber(quantizedIndex(i));
  }

  // don't overwrite default response transforms
  function appendTransform(defaults, transform) {
    defaults = angular.isArray(defaults) ? defaults : [defaults];
    return (transform) ? defaults.concat(transform) : defaults;
  }

  angular.module('bgf.paginateAnything', []).

    directive('bgfPagination', function () {
      var defaultLinkGroupSize = 3, defaultClientLimit = 250, defaultPerPage = 50;

      return {
        restrict: 'AE',
        scope: {
          // required
          url: '=',
          collection: '=',

          // optional
          urlParams: '=?',
          headers: '=?',
          page: '=?',
          perPage: '=?',
          perPagePresets: '=?',
          autoPresets: '=?',
          clientLimit: '=?',
          linkGroupSize: '=?',
          reloadPage: '=?',
          size: '=?',
          passive: '@',
          transformResponse: '=?',

          // directive -> app communication only
          numPages: '=?',
          numItems: '=?',
          serverLimit: '=?',
          rangeFrom: '=?',
          rangeTo: '=?'
        },
        templateUrl: function(element, attr) {
          return attr.templateUrl || 'src/paginate-anything.html';
        },
        replace: true,
        controller: ['$scope', '$http', function($scope, $http) {

          $scope.reloadPage   = false;
          $scope.serverLimit  = Infinity; // it's not known yet
          $scope.Math         = window.Math; // Math for the template

          if(typeof $scope.autoPresets !== 'boolean') {
            $scope.autoPresets = true;
          }

          var lgs = $scope.linkGroupSize, cl = $scope.clientLimit;
          $scope.linkGroupSize  = typeof lgs === 'number' ? lgs : defaultLinkGroupSize;
          $scope.clientLimit    = typeof cl  === 'number' ? cl : defaultClientLimit;

          $scope.updatePresets  = function () {
            if($scope.autoPresets) {
              var presets = [], i;
              for(i = Math.min(3, quantizedIndex($scope.perPage || defaultPerPage));
                  i <= quantizedIndex(Math.min($scope.clientLimit, $scope.serverLimit));
                  i++) {
                presets.push(quantizedNumber(i));
              }
              $scope.perPagePresets = presets;
            } else {
              $scope.perPagePresets = $scope.perPagePresets.filter(
                function (preset) { return preset <= $scope.serverLimit; }
              ).concat([$scope.serverLimit]);
            }
          };

          $scope.gotoPage = function (i) {
            if(i < 0 || i*$scope.perPage >= $scope.numItems) {
              return;
            }
            $scope.page = i;
          };

          $scope.linkGroupFirst = function() {
            var rightDebt = Math.max( 0,
              $scope.linkGroupSize - ($scope.numPages - 1 - ($scope.page + 2))
            );
            return Math.max( 0,
              $scope.page - ($scope.linkGroupSize + rightDebt)
            );
          };

          $scope.linkGroupLast = function() {
            var leftDebt = Math.max( 0,
              $scope.linkGroupSize - ($scope.page - 2)
            );
            return Math.min( $scope.numPages-1,
              $scope.page + ($scope.linkGroupSize + leftDebt)
            );
          };

          $scope.isFinite = function() {
            return $scope.numPages < Infinity;
          };

          function requestRange(request) {
            $scope.$emit('pagination:loadStart', request);
            $http({
              method: 'GET',
              url: $scope.url,
              params: $scope.urlParams,
              headers: angular.extend(
                {}, $scope.headers,
                { 'Range-Unit': 'items', Range: [request.from, request.to].join('-') }
              ),
              transformResponse: appendTransform($http.defaults.transformResponse, $scope.transformResponse)
            }).success(function (data, status, headers, config) {
              var response = parseRange(headers('Content-Range'));
              if(status === 204 || (response && response.total === 0)) {
                $scope.numItems = 0;
                $scope.collection = [];
              } else {
                $scope.numItems = response ? response.total : data.length;
                $scope.collection = data || [];
              }

              if(response) {
                $scope.rangeFrom = response.from;
                $scope.rangeTo   = response.to;
                if(length(response) < response.total) {
                  if(
                    ( request.to < response.total - 1) ||
                    (response.to < response.total - 1 && response.total < request.to)
                  ) {
                    if(!$scope.perPage || length(response) < $scope.perPage) {
                      if($scope.autoPresets) {
                        var idx = quantizedIndex(length(response));
                        if(quantizedNumber(idx) > length(response)) {
                          idx--;
                        }
                        $scope.serverLimit = quantizedNumber(idx);
                      } else {
                        $scope.serverLimit = length(response);
                      }
                      $scope.perPage = $scope.Math.min(
                        $scope.serverLimit,
                        $scope.clientLimit
                      );
                    }
                  }
                }
              }
              $scope.numPages = Math.ceil($scope.numItems / ($scope.perPage || defaultPerPage));

              $scope.$emit('pagination:loadPage', status, config);
            }).error(function (data, status, headers, config) {
              $scope.$emit('pagination:error', status, config);
            });
          }

          $scope.page = $scope.page || 0;
          $scope.size = $scope.size || 'md';
          if($scope.autoPresets) {
            $scope.updatePresets();
          }

          $scope.$watch('page', function(newPage, oldPage) {
            if($scope.passive === 'true') { return; }

            if(newPage !== oldPage) {
              if(newPage < 0 || newPage*$scope.perPage >= $scope.numItems) {
                return;
              }

              var pp = $scope.perPage || defaultPerPage;

              if($scope.autoPresets) {
                pp = quantize(pp);
              }

              requestRange({
                from: newPage * pp,
                to: (newPage+1) * pp - 1
              });
            }
          });

          $scope.$watch('perPage', function(newPp, oldPp) {
            if($scope.passive === 'true') { return; }

            if(typeof(oldPp) === 'number' && newPp !== oldPp) {
              var first = $scope.page * oldPp;
              var newPage = Math.floor(first / newPp);

              if($scope.page !== newPage) {
                $scope.page = newPage;
              } else {
                requestRange({
                  from: $scope.page * newPp,
                  to: ($scope.page+1) * newPp - 1
                });
              }
            }
          });

          $scope.$watch('serverLimit', function(newLimit, oldLimit) {
            if($scope.passive === 'true') { return; }

            if(newLimit !== oldLimit) {
              $scope.updatePresets();
            }
          });

          $scope.$watch('url', function(newUrl, oldUrl) {
            if($scope.passive === 'true') { return; }

            if(newUrl !== oldUrl) {
              if($scope.page === 0){
                $scope.reloadPage = true;
              } else {
                $scope.page = 0;
              }
            }
          });

          $scope.$watch('urlParams', function(newParams, oldParams) {
            if($scope.passive === 'true') { return; }

            if(!angular.equals(newParams, oldParams)) {
              if($scope.page === 0){
                $scope.reloadPage = true;
              } else {
                $scope.page = 0;
              }
            }
          }, true);

          $scope.$watch('headers', function(newHeaders, oldHeaders) {
            if($scope.passive === 'true') { return; }

            if(!angular.equals(newHeaders, oldHeaders)) {
              if($scope.page === 0){
                $scope.reloadPage = true;
              } else {
                $scope.page = 0;
              }
            }
          }, true);

          $scope.$watch('reloadPage', function(newVal, oldVal) {
            if($scope.passive === 'true') { return; }

            if(newVal === true && oldVal === false) {
              $scope.reloadPage = false;
              requestRange({
                from: $scope.page * $scope.perPage,
                to: ($scope.page+1) * $scope.perPage - 1
              });
            }
          });

          $scope.$watch('transformResponse', function(newTransform, oldTransform) {
            if($scope.passive === 'true') { return; }
            if(!newTransform || !oldTransform) { return; }

            // If applying a transform to returned data, it makes sense to start at the first page if changed
            // Unfortunately it's not really possible to compare function equality
            // In lieu of that, for now we'll compare string representations of them.
            if(!angular.equals(newTransform.toString(), oldTransform.toString())) {
              if($scope.page === 0){
                $scope.reloadPage = true;
              } else {
                $scope.page = 0;
              }
            }
          }, true);

          var pp = $scope.perPage || defaultPerPage;

          if($scope.autoPresets) {
            pp = quantize(pp);
          }

          requestRange({
            from: $scope.page * pp,
            to: ($scope.page+1) * pp - 1
          });
        }]
      };
    }).

    filter('makeRange', function() {
      // http://stackoverflow.com/a/14932395/3102996
      return function(input) {
        var lowBound, highBound;
        switch (input.length) {
        case 1:
          lowBound = 0;
          highBound = parseInt(input[0], 10) - 1;
          break;
        case 2:
          lowBound = parseInt(input[0], 10);
          highBound = parseInt(input[1], 10);
          break;
        default:
          return input;
        }
        var result = [];
        for (var i = lowBound; i <= highBound; i++) { result.push(i); }
        return result;
      };
    });


  function parseRange(hdr) {
    var m = hdr && hdr.match(/^(?:items )?(\d+)-(\d+)\/(\d+|\*)$/);
    if(m) {
      return {
        from: +m[1],
        to: +m[2],
        total: m[3] === '*' ? Infinity : +m[3]
      };
    } else if(hdr === '*/0') {
      return { total: 0 };
    }
    return null;
  }

  function length(range) {
    return range.to - range.from + 1;
  }
}());

angular.module('bgf.paginateAnything').run(['$templateCache', function($templateCache) {
  'use strict';

  $templateCache.put('src/paginate-anything.html',
    "<div class=paginate-anything><ul class=\"pagination pagination-{{size}} links\" ng-if=\"numPages > 1\"><li ng-class=\"{disabled: page <= 0}\"><a href ng-click=gotoPage(page-1)>&laquo;</a></li><li ng-if=\"linkGroupFirst() > 0\"><a href ng-click=gotoPage(0)>1</a></li><li ng-if=\"linkGroupFirst() > 1\" class=disabled><a href>&hellip;</a></li><li ng-repeat=\"p in [linkGroupFirst(), linkGroupLast()] | makeRange\" ng-class=\"{active: p === page}\"><a href ng-click=gotoPage(p)>{{p+1}}</a></li><li ng-if=\"linkGroupLast() < numPages - 2\" class=disabled><a href>&hellip;</a></li><li ng-if=\"isFinite() && linkGroupLast() < numPages - 1\"><a href ng-click=gotoPage(numPages-1)>{{numPages}}</a></li><li ng-class=\"{disabled: page >= numPages - 1}\"><a href ng-click=gotoPage(page+1)>&raquo;</a></li></ul><div class=per-page ng-if=\"perPagePresets.length > 0 && numPages > 1\"><select ng-model=$parent.perPage ng-options=\"p for p in perPagePresets\"></select>per page</div></div>"
  );

}]);
