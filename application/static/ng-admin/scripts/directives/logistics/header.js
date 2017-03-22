'use strict';

/**
 * @ngdoc directive
 * @name izzyposWebApp.directive:adminPosHeader
 * @description
 * # adminPosHeader
 */
angular.module('sbAdminApp')
    .directive('logisticsHeader',function() {
    	return {
  		templateUrl: '../../static/ng-admin/scripts/directives/logistics/header.html',
  		restrict: 'E',
  		replace: true,
        link: function(scope, element, attrs) {
            scope.toggle = function(){
                scope.m.expand = !scope.m.expand;
            };
        },
        controller: function($scope, $http, $location){
            $scope.modalShown = false;
            $scope.logClose = function() {
                console.log('close!');
            };
            $scope.CHANNELS= {
                '4px': ['', 'US_EPAC','HKDHL'],
            };

            $scope.toggleModal = function() {
                $scope.modalShown = !$scope.modalShown;
            };

            var entriesNum = 0;
            angular.forEach($scope.m.entries, function(entry) {
                entriesNum += entry.quantity;
            });
            $scope.m.entriesNum = entriesNum;

            $scope.saveForm = function() {
                $http({
                    method: 'PUT',
                    url: '/admin/n/update',
                    data: JSON.stringify({
                        lid: $scope.m.id,
                        cn_tracking_no: $scope.m.detail.cn_tracking_no,
                        cn_logistic_name: $scope.m.detail.cn_logistic_name,
                        extra: $scope.m.detail.extra,
                        status: $scope.m.detail.status,
                        partner: $scope.m.detail.partner,
                        channel: $scope.m.detail.channel,
                        route: $scope.m.detail.route,
                        real_weight: $scope.m.detail.real_weight,
                    }),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.modalShown = false;
                        var url = $location.url();
                        if (url.substring(0, 26) !=  '/dashboard/logistics_delay') {
                            angular.element(document
                                .querySelector('[data-mid="'+$scope.m.id+'"]')).remove();
                        }
                    } else {
                        console.log(data);
                        alert(data.message+', '+data.desc);
                    }
                })
            };
        },
  	}
  });
