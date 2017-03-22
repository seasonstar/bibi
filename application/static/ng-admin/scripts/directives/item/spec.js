'use strict';

/**
 * @ngdoc directive
 * @name izzyposWebApp.directive:adminPosHeader
 * @description
 * # adminPosHeader
 */
angular.module('sbAdminApp')
    .directive('spec',function($http) {
    	return {
  		templateUrl: '../../static/ng-admin/scripts/directives/item/spec.html',
  		restrict: 'E',
  		replace: true,
        link: function(scope, element, attrs) {
            scope.saveSpec = function(spec) {
                $http({
                    method: 'PUT',
                    url: '/admin/i/update_spec',
                    data: JSON.stringify(spec),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        scope.spec = data.spec;
                        console.log(data.spec);
                        alert(data.message);
                    } else {
                        console.log(data);
                        alert(data.message+', '+data.desc);
                    }
                })
            };
            scope.removeSpec = function(sku) {
                $http({
                    method: 'DELETE',
                    url: '/admin/i/delete_spec',
                    data: JSON.stringify({
                        sku:sku,
                    }),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        element.parent().remove();
                        alert(data.message);
                    }
                })
            };
        },
  	}
  });
