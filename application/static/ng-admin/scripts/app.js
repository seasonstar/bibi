'use strict';
/**
 * @ngdoc overview
 * @name sbAdminApp
 * @description
 * # sbAdminApp
 *
 * Main module of the application.
 */
angular
  .module('sbAdminApp', [
    'oc.lazyLoad',
    'ui.router',
    'angular-loading-bar',
    'bgf.paginateAnything',
    'angular-advanced-searchbox',
    'xeditable',
    "checklist-model",
    'ng.ueditor',
  ])
  .run(function(editableOptions) {
      editableOptions.theme = 'bs3';
  })
  .config(['$stateProvider','$urlRouterProvider','$ocLazyLoadProvider',function ($stateProvider,$urlRouterProvider,$ocLazyLoadProvider) {

    $ocLazyLoadProvider.config({
      debug:true,
      events:true,
    });
    $urlRouterProvider.otherwise('/dashboard/home');
    $stateProvider
      .state('dashboard', {
        url:'/dashboard',
        templateUrl: '../../static/ng-admin/views/dashboard/main.html',
        resolve: {
            loadMyDirectives:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load(
                {
                    name:'sbAdminApp',
                    files:[
                    '../../static/ng-admin/scripts/directives/header/header.js',
                    '../../static/ng-admin/scripts/directives/header/header-notification/header-notification.js',
                    '../../static/ng-admin/scripts/directives/sidebar/sidebar.js',
                    '../../static/ng-admin/scripts/directives/sidebar/sidebar-search/sidebar-search.js',
                    '../../static/ng-admin/scripts/directives/modal-dialog/modal-dialog.js',
                    '../../static/ng-admin/scripts/directives/logistics/header.js',
                    '../../static/ng-admin/scripts/directives/logistics/body.js',
                    '../../static/ng-admin/scripts/directives/logistics/remark.js',
                    '../../static/ng-admin/scripts/directives/logistics/irrdetail.js',
                    ]
                })
            }],
        }
    })
      .state('dashboard.home',{
        url:'/home',
        controller: 'MainCtrl',
        templateUrl:'../../static/ng-admin/views/dashboard/home.html',
        resolve: {
          loadMyFiles:function($ocLazyLoad) {
            return $ocLazyLoad.load({
              name:'sbAdminApp',
              files:[
              '../../static/ng-admin/scripts/controllers/main.js',
              '../../static/ng-admin/scripts/directives/dashboard/stats/stats.js'
              ]
            })
          }
        }
    })
      .state('dashboard.item',{
        url:'/item/:item',
        controller: 'ItemCtrl',
        templateUrl:'../../static/ng-admin/views/item/list.html',
        resolve: {
          loadMyFiles:function($ocLazyLoad) {
            return $ocLazyLoad.load({
              name:'Item',
              files:[
              '../../static/ng-admin/scripts/controllers/item.js',
              '../../static/ng-admin/scripts/directives/item/item-box.js',
              '../../static/ng-admin/scripts/directives/item/spec.js',
              ]
            })
          },
        }
    })
      .state('dashboard.logistics',{
        url:'/logistics/:item',
        controller: 'LogisticsCtrl',
        templateUrl:'../../static/ng-admin/views/logistics/list.html',
        resolve: {
          loadMyFiles:function($ocLazyLoad) {
            return $ocLazyLoad.load({
              name:'Logistics',
              files:[
              '../../static/ng-admin/scripts/services/logistics.js',
              '../../static/ng-admin/scripts/controllers/logistics.js',
              ]
            })
          },
        }
    })
      .state('dashboard.logistics_delay',{
        url:'/logistics_delay',
        controller: 'LogisticsDelayCtrl',
        templateUrl:'../../static/ng-admin/views/logistics_delay/base.html',
        resolve: {
          loadMyFiles:function($ocLazyLoad) {
            return $ocLazyLoad.load({
              name:'LogisticsDelay',
              files:[
              '../../static/ng-admin/scripts/services/logistics_delay.js',
              '../../static/ng-admin/scripts/controllers/logistics_delay.js',
              ]
            })
          },
        },
    })
      .state('dashboard.logistics_delay.list', {
        url: '/:status',
        views: {
          '': {
            templateUrl: '../../static/ng-admin/views/logistics_delay/list.html',
            controller: function($scope,$rootScope, $stateParams, LogisticsDelay){
                $rootScope.delayStatus = $stateParams.status;

            }
          },
          'hint@dashboard.logistics_delay': {
            templateProvider: function($stateParams){
                return "<small> -> " + $stateParams.status + "</small>";
            },
          },
        },
    })
      .state('dashboard.logistics_irregular',{
        url:'/logistics_irregular',
        controller: 'LogisticsIrregularCtrl',
        templateUrl:'../../static/ng-admin/views/logistics_irregular/base.html',
        resolve: {
          loadMyFiles:function($ocLazyLoad) {
            return $ocLazyLoad.load({
              name:'LogisticsIrregular',
              files:[
              '../../static/ng-admin/scripts/services/logistics_irregular.js',
              '../../static/ng-admin/scripts/controllers/logistics_irregular.js',
              ]
            })
          },
        }
    })
      .state('dashboard.logistics_irregular.list', {
        url: '/:process_status',
        views: {
          '': {
            templateUrl: '../../static/ng-admin/views/logistics_irregular/list.html',
            controller: function($scope, $stateParams, LogisticsIrregular){
                $scope.process_status = $stateParams.process_status;

            }
          },
          'hint': {
            templateProvider: function($stateParams){
                return "<small> -> " + $stateParams.process_status + "</small>";
            },
          },
        },
    })
  }]);
