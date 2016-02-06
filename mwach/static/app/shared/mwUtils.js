(function() {
  'use strict';

angular.module('mwachx')
  .factory('mwachxUtils',['$filter',function($filter){
    var service = {
      convert_form_date:function(date) {
        return $filter('date')(date,'yyyy-MM-dd');
      },

      convert_dates:function(form_scope) {
        /* Check all values in form_scope and convert dates to yyyy-MM-dd format*/
        console.log('Converting:',form_scope);
        angular.forEach(form_scope, function(value,key) {
          if ( value instanceof Date) {
            console.log(value,key);
            form_scope[key] = service.convert_form_date(value)
          }
        });
      },

      days_str:function(days) {
        if (-7 < days && days < 7)
          return days+'d';
        var weeks = Math.round(Number(days)/7);
        return weeks+'w';
      },
    }

    return service;
  }]);

// *************************************
// Directive for making DIV's editable
// *************************************
angular.module('mwachx')
.directive("contenteditable", function() {
  return {
    restrict: "A",
    require: "ngModel",
    link: function(scope, element, attrs, ngModel) {

      function read() {
        ngModel.$setViewValue(element.html());
      }

      ngModel.$render = function() {
        element.html(ngModel.$viewValue || "");
      };

      element.bind("blur keyup change", function() {
        scope.$apply(read);
      });
    }
  };
})

// *************************************
// Filter to capitalize first letter: from
// *************************************
angular.module('mwachx')
.filter('capitalize', function() {
  return function(input, scope) {
    if (input!=null)
    input = input.toLowerCase();
    return input.substring(0,1).toUpperCase()+input.substring(1);
  }
});

})();
