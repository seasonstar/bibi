'use strict';

/**
 * @ngdoc directive
 * @name izzyposWebApp.directive:adminPosHeader
 * @description
 * # adminPosHeader
 */
angular.module('sbAdminApp')
    .directive('itemBox',function() {
    	return {
  		templateUrl: '../../static/ng-admin/scripts/directives/item/item-box.html',
  		restrict: 'E',
  		replace: true,
        link: function(scope, element, attrs) {
            scope.toggle = function(){
                scope.item.expand = !scope.item.expand;
            };
        },
        controller: function($scope, $http, $location){
            $scope.ATTRS= [
                {value: 'color', text: 'color'},
                {value: 'size', text: 'size'},
                {value: 'style', text: 'style'}
            ];
            $scope.showAttrs= function() {
                var selected = [];
                angular.forEach($scope.ATTRS, function(s) {
                  if ($scope.item.meta.attributes.indexOf(s.value) >= 0) {
                    selected.push(s.text);
                  }
                });
                return selected.length ? selected.join(', ') : 'null';
            };
            $scope.saveItem = function(item) {
                $http({
                    method: 'PUT',
                    url: '/admin/i/update',
                    data: JSON.stringify(item),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        alert(data.message);
                    } else {
                        console.log(data);
                        alert(data.message+', '+data.desc);
                    }
                })
            };
            $scope.newSpec = {
                item_id: $scope.item.meta._id,
                price: $scope.item.meta.price,
                original_price: $scope.item.meta.original_price,
                china_price: $scope.item.meta.china_price,
            };
            $scope.addSpec = function(){
                $http({
                    method: 'POST',
                    url: '/admin/i/add_spec',
                    data: JSON.stringify($scope.newSpec),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.item.specs.push(data.spec);
                        console.log(data.spec);
                        alert(data.message);
                    } else {
                        console.log(data);
                        alert(data.message+', '+data.desc);
                    }
                })

            }

        },
  	}
  });
