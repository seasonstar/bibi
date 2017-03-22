'use strict';
/**
 * @ngdoc function
 * @name sbAdminApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the sbAdminApp
 */
angular.module('sbAdminApp')
  .controller('LogisticsCtrl', function($scope, $http, Logistics, $stateParams) {
      $scope.tempParams = {};
      $scope.tempExtra = 'receiver';
      $scope.searchParams = {};
      $scope.searchParams['query'] = $stateParams.item;
      $scope.availableSearchParams = [
          { key: "id", name: "ID", placeholder: "包裹ID" },
          { key: "cn_tracking_no", name: "CTN", placeholder: "国际运单号" },
          { key: "partner_tracking_no", name: "MB", placeholder: "MB No" },
          { key: "receiver", name: "收件人", placeholder: "..." },
          { key: "order_id", name: "订单号", placeholder: "短单号" },
      ];
      $http.get('/admin/n/partner').success(function(data) {
          $scope.availablePartner= data.results;
      });
      $scope.setStatus = function(st){
          $scope.searchParams = {};
          if (st == 'ALL'){
              $scope.searchParams['status'] = '';
          } else {
              $scope.searchParams['status'] = st;
          }
          $scope.curr_status = st;
      };
      $scope.setParams = function(start, end) {
          $scope.searchParams = {};
          angular.forEach($scope.tempParams, function(value, key) {
              $scope.searchParams[key] = value;
          });
          $scope.searchParams['start'] = start;
          $scope.searchParams['end'] = end;
          $scope.searchParams[$scope.tempExtra] = $scope.tempExtraValue;
          $scope.searchParams['query'] = $scope.tempQuery;
          $scope.searchParams['partner'] = $scope.tempPartner;
          $scope.searchParams['channel'] = $scope.tempChannel;
          if ($scope.curr_status != 'ALL'){
              $scope.searchParams['status'] = $scope.curr_status
          }
          if ($scope.tempQuery){
              $scope.searchParams['include_closed'] = true;
          }
          $scope.reloadPage = true;
      };
      $scope.reset = function() {
          $scope.tempQuery = null;
          $scope.tempExtra = null;
          $scope.tempExtraValue = null;
          $scope.tempPartner = null;
          $scope.tempChannel = null;
          $scope.start = null;
          $scope.end = null;
          $scope.searchParams = {};
      };
      $scope.DateBoxShown = false;
      $scope.showDateFilter = function() {
          $scope.DateBoxShown = !$scope.DateBoxShown;
      }
      $scope.toggleAll = function() {
          if ($scope.selectedAll) {
            $scope.selectedAll = false;
          } else {
            $scope.selectedAll = true;
          };
          angular.forEach($scope.results, function(m) {
            m.expand = $scope.selectedAll;
          });
      };

      $scope.mergeLogistics = function() {
        var selectedLogistics = $scope.results.filter(function(lo) {
            return lo.checked;
        });
        var selected = [];
        angular.forEach(selectedLogistics, function(obj) {
            this.push(obj.id);
        }, selected);
        $http.post("/admin/n/merge", {
            lids: selected,
        }).success(function(data){
            if (data.message=="OK"){
                alert("OK");
                $scope.searchParams['query'] = data.lid;
            } else {
                alert(data.message+ ', '+data.desc);
            };
        });
      };
      $scope.splitEntries = function() {
        var selected = $.map($("input[name='entry']:checked"), function(n, i) {
            return $(n).val();
        });
        $http.post("/admin/n/split_entries", {
            selected: selected,
        }).success(function(data){
            if (data.message=="OK"){
                alert("OK");
                $scope.searchParams['order_id'] = data.oid;
            } else {
                alert(data.message+ ', '+data.desc);
            };
        });

      };

      $scope.exportCSV =  function() {
        $http.get("/admin/n/download", {
            params: $scope.searchParams,
        }).success(function(data, status, headers, config) {
            var anchor = angular.element('<a/>');
            anchor.attr({
                 href: 'data:attachment/csv;charset=utf-8,' + encodeURI(data),
                 target: '_blank',
                 download: 'dump_file.csv'
        })[0].click();

        })
      }

  });
