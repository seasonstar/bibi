'use strict';

angular.module('sbAdminApp')
	.factory('Logistics', function($http) {
		return {
            query: function(){
                return $http.get('/admin/n/logistics')
            }
        };
	});
