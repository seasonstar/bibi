'use strict';
/**
 * @ngdoc function
 * @name sbAdminApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the sbAdminApp
 */
angular.module('sbAdminApp')
  .controller('ItemCtrl', function($scope, $http, $stateParams) {
      $http.get('/admin/i/categories').success(function(data){
        var categories = data.categories;
        console.log(data);
        //sub_cates.splice(0, 0, 'ALL');
        angular.forEach(categories, function(cate,index) {
            categories[index].sub_list.splice(0,0, {en: 'ALL', cn: 'ALL'});
        });

        $scope.categories = categories;
      })
      $scope.searchParams = {};
      $scope.searchParams['query'] = $stateParams.item;

      $scope.setCate= function(main_cate, sub_cate){
          $scope.searchParams = {};
          if (sub_cate == 'ALL'){
              $scope.searchParams['sub_category'] = '';
              $scope.searchParams['main_category'] = main_cate;
          } else {
              $scope.searchParams['sub_category'] = sub_cate;
              $scope.searchParams['main_category'] = main_cate;
          }
          $scope.curr_cate= sub_cate;
          $scope.curr_main_cate= main_cate;
      };
      $scope.setParams = function() {
          $scope.searchParams['query'] = $scope.tempQuery;
          $scope.searchParams['creator'] = $scope.tempExtra;
          if ($scope.curr_cate!= 'ALL'){
              $scope.searchParams['cate'] = $scope.curr_cate
          }
          $scope.reloadPage = true;
      };
      $scope.reset = function() {
          $scope.tempQuery = null;
          $scope.tempExtra= null;
          $scope.searchParams = {};
      };

      $scope.toggleAll = function() {
          if ($scope.selectedAll) {
            $scope.selectedAll = false;
          } else {
            $scope.selectedAll = true;
          };
          angular.forEach($scope.results, function(item) {
            item.expand = $scope.selectedAll;
          });
      };

        $scope.toggleModal = function() {
            $scope.modalShown = !$scope.modalShown;
        };

        $scope.modalShown = false;
        $scope.logClose = function() {
            console.log('close!');
        };
        $scope.newItem = {};
        $scope.createItem= function() {
            $http({
                method: 'POST',
                url: '/admin/i/add_item',
                data: JSON.stringify($scope.newItem),
                headers: {'Content-Type': 'application/json'}
            }).success(function(data){
                console.log(data);
                if (data.message == 'OK') {
                    $scope.modalShown = false;
                    $scope.newItem = {};
                    $scope.searchParams['cate'] = 'unclassified'
                    $scope.reloadPage = true;
                } else {
                    alert(data.message+', '+data.desc);
                }
            })
        };

  });
