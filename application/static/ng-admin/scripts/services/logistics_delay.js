'use strict';

angular.module('sbAdminApp')
	.factory('LogisticsDelay', function($http) {
		return {
            sum: function(){
                return $http.get('/admin/n/logistics_delay')
            },
            getList: function(st){
                return $http.get('/admin/n/logistics_delay/'+st)
            },
        };
	});
