'use strict';

angular.module('sbAdminApp')
    .controller('LogisticsDelayCtrl', function($scope, $http, $stateParams, LogisticsDelay) {
        LogisticsDelay.sum().success(function(data){
            $scope.sums = data.results;
        });

        $scope.tempParams = {};
        $scope.searchParams = {};
        $scope.availableSearchParams = [
            { key: "id", name: "ID", placeholder: "包裹ID" },
            { key: "cn_tracking_no", name: "CTN", placeholder: "国际运单号" },
            { key: "partner_tracking_no", name: "MAYBI", placeholder: "MB No" },
        ];
        $scope.DelayTypeList = {
            'PAYMENT_RECEIVED': ["下单延缓","其他"],
            'PROCESSING': ["其他"],
            'SHIPPING': ["其他"],
            'PORT_ARRIVED': ["其他"],
        };

        $scope.setParams = function(event) {
            event.preventDefault();

            angular.forEach($scope.tempParams, function(value, key) {
                $scope.searchParams[key] = value;
            });
        };

        $scope.reset = function() {
            $scope.searchParams = {};
        };
        $scope.delayFilter = function(type) {
            $scope.curr_delay_type = type;
        };

        $scope.$on('$locationChangeSuccess', function(event) {
            $scope.curr_delay_type = '';
        });

        $scope.complete = function(content) {
            if (content.message == 'OK'){
                alert("completed");
            } else {
                alert(content.message+','+content.desc);
            }
        };

  });
