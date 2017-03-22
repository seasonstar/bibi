'use strict';

/**
 * @ngdoc directive
 * @name izzyposWebApp.directive:adminPosHeader
 * @description
 * # adminPosHeader
 */
angular.module('sbAdminApp')
    .directive('irrDetail',function() {
    	return {
  		templateUrl: '../../static/ng-admin/scripts/directives/logistics/irrdetail.html',
  		restrict: 'E',
  		replace: true,
        controller: function($scope, $http){
            var IrrStepSolutions = {
                '人手推错UTN': ['改正、重推'],
                '下错单、改状态时没核对': ['补下订单', '退多余货物'],
                '少件': ['联系官网，催促补发', '客服SMS'],
                '多件': ['取得商品信息，导入订单', '寄回公司'],
                '漏件': ['联系用户，整单取消', '退款', '上传Return label/Return Sheet',
                          '接收退回包裹的UTN、相关费用信息'],
                '丢件': ['联系用户，选择等待', '重新下单'],
                '漏推UTN': ['补推UTN'],
            };

            $scope.stepSelection = {
                steps: {}
            };

            $scope.IrrDetailShown = false;
            $scope.showIrrDetail = function() {
                $scope.IrrDetailShown= !$scope.IrrDetailShown;
                $scope.stepSolutions = IrrStepSolutions[$scope.irr.reason];
                $scope.stepSelection.steps = $scope.irr.steps;
            };

            $scope.addStep= function(solution) {
                $http({
                    method: 'PUT',
                    url: '/admin/n/update_irr_step',
                    data: {
                        lid: $scope.m.id,
                        solutions: $scope.stepSelection.steps,
                        irr_type: $scope.irr.irr_type,
                        reason: $scope.irr.reason,
                    },
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.irr = data.irr_detail;
                        console.log('ok');
                    } else {
                        console.log('Not OK');
                    }
                })

            };
            $scope.is_done = $scope.irr.process_status == 'PROCESSED';
            $scope.setDone = function() {

                $http({
                    method: 'PUT',
                    url: '/admin/n/set_irr_done',
                    data: {
                        lid: $scope.m.id,
                        irr_type: $scope.irr.irr_type,
                        process_status: $scope.is_done == false ? 'PROCESSED' : 'PROCESSING',

                    },
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.irr = data.irr_detail;
                        $scope.is_done = !$scope.is_done;
                        console.log('ok');
                    } else {
                        console.log('Not OK');
                    }
                })
            };
            $scope.addIrrRemark = function(remark) {
                $http({
                    method: 'PUT',
                    url: '/admin/n/update_irr_remark',
                    data: JSON.stringify({
                        lid: $scope.m.id,
                        irr_type: $scope.irr.irr_type,
                        irr_remark: remark,
                    }),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.irr = data.irr_detail;
                        console.log('ok');
                    } else {
                        console.log('Not OK, ' + data.desc);
                    }
                })
            }

        },
  	}
  });
