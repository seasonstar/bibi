'use strict';

angular.module('sbAdminApp')
	.directive('remark',function(){
	    return {
        templateUrl:'../../static/ng-admin/scripts/directives/logistics/remark.html',
        restrict: 'E',
        replace: true,
        controller: function($scope, $http){
            $scope.addRemark = function(remark) {
                $http({
                    method: 'PUT',
                    url: '/admin/n/update',
                    data: JSON.stringify({
                        remark: remark,
                        lid: $scope.m.id,
                    }),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.m.detail.remarks = data.remarks;
                        console.log('ok');
                    } else {
                        console.log('Not OK, ' + data.desc);
                    }
                })
            }

        },
    }
  });
