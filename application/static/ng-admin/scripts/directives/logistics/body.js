'use strict';

/**
 * @ngdoc directive
 * @name izzyposWebApp.directive:adminPosHeader
 * @description
 * # adminPosHeader
 */
angular.module('sbAdminApp')
    .directive('logisticsBody',function($sce) {
    	return {
  		templateUrl: '../../static/ng-admin/scripts/directives/logistics/body.html',
  		restrict: 'E',
  		replace: true,
        controller: function($scope, $http, $filter){
            $scope.IrrTypeNames = {
                'OTHER': "其他",
            };
            $scope.ProcessStatusNames = {
                'WAITING_PROCESS': "待处理",
                'PROCESSING': "处理中",
                'PROCESSED': "已处理",
            };
            $scope.IrrTypeList = {
                'OTHER': ['其它'],
            };
            $scope.DelayTypeList = {
                'PAYMENT_RECEIVED': ["下单延缓","其他"],
                'PROCESSING': ["其他"],
                'SHIPPING': ["其他"],
                'PORT_ARRIVED': ["其他"],
            };

            $scope.irrFormShown = false;
            $scope.delayFormShown = false;

            $scope.toggleIrrForm = function() {
                $scope.irrFormShown = !$scope.irrFormShown;
            };
            $scope.toggleDelayForm = function(status) {
                $scope.delayFormShown = !$scope.delayFormShown;
                $scope.delayTypes = $scope.DelayTypeList[status];
            };
            var attr_by_log_stat = {
                'PAYMENT_RECEIVED': 'payment_received_date',
                'PROCESSING': 'processing_date',
                'SHIPPING': 'shipping_date',
                'PORT_ARRIVED': 'port_arrived_date',
                'RECEIVED': 'received_date',
            }
            function GetDateDiff(startTime, endTime, diffType) {
                //将xxxx-xx-xx的时间格式，转换为 xxxx/xx/xx的格式
                startTime = startTime.replace(/\-/g, "/");
                endTime = endTime.replace(/\-/g, "/");
                //将计算间隔类性字符转换为小写
                diffType = diffType.toLowerCase();
                var sTime = new Date(startTime);      //开始时间
                var eTime = new Date(endTime);  //结束时间
                //作为除数的数字
                var divNum = 1;
                switch (diffType) {
                    case "second":
                        divNum = 1000;
                        break;
                    case "minute":
                        divNum = 1000 * 60;
                        break;
                    case "hour":
                        divNum = 1000 * 3600;
                        break;
                    case "day":
                        divNum = 1000 * 3600 * 24;
                        break;
                    default:
                        break;
                }
                return parseInt((eTime.getTime() - sTime.getTime()) / parseInt(divNum));
            }

            var today =new Date();

            try {
                var now_date = today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate()+" "+today.getHours()+":"+today.getMinutes()+":"+today.getSeconds();
                var curr_date = $scope.m.detail[attr_by_log_stat[$scope.m.detail.status]];
                var created_date = $filter('date')($scope.m.created_at.$date, 'yyyy-MM-dd HH:mm:ss');
                var formated_curr_date = $filter('date')(curr_date.$date, 'yyyy-MM-dd HH:mm:ss');
                $scope.m.curr_date = $filter('date')($scope.m.created_at.$date, 'yyyy-MM-dd');
                $scope.diff_date = GetDateDiff(created_date, now_date, "day")
                $scope.now_diff_date = GetDateDiff(formated_curr_date, now_date, "day")
            } catch(err) {
                console.log(err);
            };

            $scope.saveDelayForm = function(reason) {
                $http({
                    method: 'PUT',
                    url: '/admin/n/update',
                    data: JSON.stringify({
                        lid: $scope.m.id,
                        delay: reason,
                    }),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.m.detail.delay_details = data.delays;
                        console.log('ok');
                    } else {
                        console.log('Not OK');
                    }
                })
            };

            $scope.checkDelay = function(delay) {
                $http({
                    method: 'PUT',
                    url: '/admin/n/update_delay',
                    data: JSON.stringify({
                        lid: $scope.m.id,
                        status: delay.status,
                        is_done: delay.is_done,
                    }),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        console.log('ok');
                    } else {
                        console.log('Not OK');
                    }
                })

            };

            $scope.saveIrrForm = function(type, reason, desc) {
                $http({
                    method: 'PUT',
                    url: '/admin/n/update',
                    data: JSON.stringify({
                        lid: $scope.m.id,
                        irregularity: {
                            type: type,
                            reason: reason,
                            desc: desc,
                            status: $scope.m.detail.status,
                        },
                    }),
                    headers: {'Content-Type': 'application/json'}
                }).success(function(data){
                    if (data.message == 'OK') {
                        $scope.m.detail.irregular_details = data.irregularities;
                        console.log('ok');
                    } else {
                        console.log('Not OK');
                    }
                })
            };

            var btn_str = '<button class="cancel btn btn-xs btn-info">Close</button>'

            $scope.openOperation= function() {
                $scope.operationShown = true;
                $http.get("/admin/n/logs/logistic/"+$scope.m.id
                ).success(function(result){
                    $scope.operation_history= $sce.trustAsHtml(result.replace(btn_str, '<br/>'))
                });
            };
            $scope.closeOperation = function() {
                $scope.operationShown = false;

            };

            $scope.openTracking = function() {
                $scope.trackingShown = true;
                $http.get("/admin/n/logs/express/"+$scope.m.id
                ).success(function(result){
                    $scope.tracking_history= $sce.trustAsHtml(result.replace(btn_str, '<br/>'))
                });
            };
            $scope.closeTracking = function() {
                $scope.trackingShown = false;

            };

            $scope.retrieveTracking = function() {
                $http.get("/admin/n/refresh/"+
                        $scope.m.detail.cn_logistic_name+'/'+
                        $scope.m.detail.cn_tracking_no).success(function(data){
                            if (data.message=="OK"){
                                alert("success");
                            }
                        })
            };

            $scope.closeLogistic= function() {
                $http.get("/admin/n/close/"+$scope.m.id)
                    .success(function(data){
                        if (data.message=="OK"){
                            angular.element(document
                                .querySelector('[data-mid="'+$scope.m.id+'"]')).remove();
                            alert("success");
                        }
                    })
            };

            $scope.moveTo = function(status) {
                $http.get("/admin/n/back_status", {
                    params: {
                        lid: $scope.m.id,
                        status: status,
                    }
                }).success(function(data){
                    if (data.message=="OK") {
                        alert("success");
                    }
                })
            };
            $scope.splitQuantity = function(quantity, entry_id) {
                $http.post("/admin/n/split_quantity", {
                    quantity: quantity,
                    lid: $scope.m.id,
                    eid: entry_id
                }).success(function(data){
                    if (data.message=="OK"){
                        alert("OK");
                        $scope.m.entries = data.entries;
                    } else {
                        alert(data.message+ ', '+data.desc);
                    };
                });
            };

        },
  	}
  });
