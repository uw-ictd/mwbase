(function(){
  'use strict';

  // Prepare the 'mwachx' module for subsequent registration of controllers and delegates
  angular.module('mwachx', [ 'ui.bootstrap', 'ui.bootstrap.showErrors', 'ngRoute', 'ngResource' ])
  	.config(['$resourceProvider', '$httpProvider', function($resourceProvider, $httpProvider) {
	  // Don't strip trailing slashes from calculated URLs
	  $resourceProvider.defaults.stripTrailingSlashes = false;
	  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
	  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	}])
	.config(['showErrorsConfigProvider', function(showErrorsConfigProvider) {
  showErrorsConfigProvider.trigger('keypress');
}]);
  
})();