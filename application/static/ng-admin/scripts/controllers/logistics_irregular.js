'use strict';

angular.module('sbAdminApp')
  .controller('LogisticsIrregularCtrl', function($scope, $http, LogisticsIrregular) {
      LogisticsIrregular.sum().success(function(data){
        $scope.sums = data.results;
      });

      $scope.setType = function(irr_type){
          $scope.curr_type = irr_type;
      };

      $scope.searchParams = {};
      $scope.availableSearchParams = [
          { key: "id", name: "ID", placeholder: "包裹ID" },
          { key: "cn_tracking_no", name: "CTN", placeholder: "国际运单号" },
          { key: "partner_tracking_no", name: "MB", placeholder: "MB No" },
      ];
  });
