# Python Imports
import datetime
import json

# Rest Framework Imports
from rest_framework import serializers
# from rest_framework.decorators import action
from rest_framework.response import Response

# Local Imports
import mwpriya.models as mwpriya
import mwpriya.forms as forms

import utils
from mwbase.serializers.messages import MessageSerializer, ParticipantSimpleSerializer, MessageSimpleSerializer
from mwbase.serializers.misc import PhoneCallSerializer, NoteSerializer
from mwbase.serializers.visits import VisitSimpleSerializer, VisitSerializer

# mwbase Imports
import mwbase.models as mwbase
from mwbase.serializers import participants


class ParticipantSerializer(participants.ParticipantSerializer):

    class Meta:
        model = mwpriya.Participant
        fields = '__all__'


#############################################
#  ViewSet Definitions
#############################################

class ParticipantViewSet(participants.ParticipantViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    forms = forms

    def get_queryset(self):
        qs = mwpriya.Participant.objects.all().order_by('study_id')
        # Only return the participants for this user's facility
        if self.action == 'list':
            return qs.for_user(self.request.user, superuser=True)
        else:
            # return qs
            return qs.prefetch_related('phonecall_set')

    def get_serializer_class(self):
        # Return the correct serializer based on current action
        if self.action == 'list':
            return ParticipantSimpleSerializer
        else:
            return ParticipantSerializer

    ########################################
    # Overide Router POST, PUT, PATCH
    ########################################

    def partial_update(self, request, study_id=None, *args, **kwargs):
        ''' PATCH - partial update a participant '''

        instance = self.get_object()
        instance.preg_status = request.data['preg_status']
        instance.sms_status = request.data['sms_status']
        instance.send_time = request.data['send_time']
        instance.send_day = request.data['send_day']
        instance.prep_initiation = utils.angular_datepicker(request.data['prep_initiation'])
        instance.due_date = utils.angular_datepicker(request.data['due_date'])
        instance.quick_notes = request.data['quick_notes']

        instance.save()
        instance_serialized = ParticipantSerializer(mwpriya.Participant.objects.get(pk=instance.pk),
                                                    context={'request': request}).data
        return Response(instance_serialized)
