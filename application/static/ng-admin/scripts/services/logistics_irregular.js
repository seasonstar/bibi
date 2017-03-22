'use strict';

angular.module('sbAdminApp')
	.factory('LogisticsIrregular', function($http) {
		return {
            sum: function(){
                return $http.get('/admin/n/logistics_irregular')
            },
            getList: function(st){
                return $http.get('/admin/n/logistics_irregular/'+st)
            },
        };
	});
