(function(){
  'use strict';
  
  /**
   * Main Controller for participants objects?
   * @param $scope
   * @constructor
   */
  angular.module('mwachx')
    .controller('ParticipantController', 
      function ParticipantController($scope, $location, $routeParams, 
        Message, Participant) {

        $scope.participant      = [];
        $scope.fullResponse     = {};

        $scope.messages         = [];


        $scope.detailsList      = [ 
         {'label': 'Nickname',               'value': 'nickname',},
         {'label': 'Study ID',               'value': 'study_id',},
         {'label': 'ANC Number',             'value': 'anc_num',},
         {'label': 'Phone number',           'value': 'phone_number',},
         {'label': 'Status',                 'value': 'status',},
         {'label': 'Estimated Delivery Date','value': 'phone_number',},
         {'label': 'Send Day',               'value': 'send_day',},
         {'label': 'Send Time',              'value': 'send_time',},
         {'label': 'SMS Track',              'value': 'condition',},
         {'label': 'ART Initiation',         'value': 'art_initiation',},
         {'label': 'Previous pregnancies',   'value': 'previous_pregnancies',},
         {'label': 'Family Planning',        'value': 'family_planning',},
         {'label': 'HIV Disclosure',         'value': 'hiv_disclosed',},
         {'label': 'Confirmation Code',      'value': 'validation_key',},
        ];
            
        //
        // Private Methods
        //

        var isDisabled = function(i) {
          return (this.is_pending && (typeof this.related === 'undefined' || this.topic === 'none'));
        }
        // Methods
        
        // Fetch this participant
        Participant.get( {study_id:$routeParams.study_id},
          function(response) {
            $scope.participant = response;

            $scope.participant.hiv_disclosed = 
              (String($scope.participant.hiv_disclosed) === 'null') ?
                'Unknown' :
                ($scope.participant.hiv_disclosed) ?
                  'Yes' : 'No';
        });

        // Fetch messages for this participant
        Message.query( {study_id:$routeParams.study_id},
          function(response) {
            
            $scope.messages = response;
            for (var i = $scope.messages.length - 1; i >= 0; i--) {
              
              $scope.messages[i].show_translation = $scope.messages[i].is_translated;
              $scope.messages[i].isDisabled = isDisabled;
              $scope.messages[i].topic = 'none';

              if ($scope.messages[i].is_system == false && $scope.messages[i].is_outgoing == true) {
                $scope.messages[i].is_nurse = true;
              } else {
                $scope.messages[i].is_nurse = false;
              }

            };
        });

      });

})();