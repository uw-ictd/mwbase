from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from mwbase.models import AutomatedMessageQuerySetBase, AutomatedMessageBase
from utils import enums

class AutomatedMessageHIVQuerySet(AutomatedMessageQuerySetBase):
    """
    Used to map a single description to an AutomatedMessage.
    """

    def from_description(self, description, exact=False):
        """
        Return AutomatedMessage for description

        :param description (str): base.group.condition.hiv.offset string to look for
        :returns: AutomatedMessage matching description or closes match if not found
        """
        send_base, group, condition, hiv_messaging, second, send_offset = description.split('.')
        hiv = hiv_messaging == "Y"
        second_preg = second == "Y"
        send_offset = int(send_offset)

        # Special case for post date messages go back and forth between week 41 and 42 messages
        if send_base == 'edd' and send_offset < -2:
            send_offset = (send_offset + 1) % -2 - 1

        return self.from_parameters(send_base, group, condition, send_offset, hiv, second_preg, exact=exact)
        
    def from_parameters(self, send_base, group, condition='normal', send_offset=0, hiv=False, second_preg=False, exact=False):
        # TODO: Need Logic for second_preg lookup ordering
        # Look for exact match of parameters
        try:
            return self.get(send_base=send_base, send_offset=send_offset,
                            group=group, condition=condition, hiv_messaging=hiv, second_preg=second_preg)
        except ObjectDoesNotExist as e:
            if exact == True:
                return None
            # No match for participant conditions continue to find best match
            pass

        # Create the base query set with send_base and offset
        message_offset = self.filter(send_base=send_base, send_offset=send_offset)

        if hiv:
            # Try to find a non HIV message for this conditon
            try:
                return message_offset.get(condition=condition, group=group, hiv_messaging=False)
            except ObjectDoesNotExist as e:
                pass

            # Force condition to normal and try again with group and hiv=True
            try:
                return message_offset.get(condition="normal", group=group, hiv_messaging=hiv)
            except ObjectDoesNotExist as e:
                pass

        if condition != "normal":
            # Force condition to normal and try again
            try:
                return message_offset.get(condition="normal", group=group, hiv_messaging=False)
            except ObjectDoesNotExist as e:
                pass

        if group == "two-way":
            # Force group to one-way and try again
            try:
                return message_offset.get(condition=condition, group="one-way", hiv_messaging=False)
            except ObjectDoesNotExist as e:
                pass

        if condition != "normal" and group != "one-way":
            # Force group to one-way and force hiv_messaging off return message or None
            return message_offset.filter(condition='normal', group='one-way', hiv_messaging=False).first()

    def from_excel(self, msg):
        """
        Replace fields of message content with matching description
        """
        auto = self.from_description(msg.description(), exact=True)
        if auto is None:
            return self.create(**msg.kwargs()), 'created'
        else:
            msg_english = msg.english if msg.english != '' else msg.new
            changed = msg_english != auto.english or msg.swahili != auto.swahili or msg.luo != auto.luo

            auto.english = msg_english
            auto.swahili = msg.swahili
            auto.luo = msg.luo
            auto.save()

            return auto, 'changed' if changed else 'same'


class AutomatedMessageHIV(AutomatedMessageBase):
    """
    Automated Messages for sending to participants. These represent message _templates_
    not message _instances_.
    """

    SEND_BASES_CHOICES = (
        ('edd', 'Before EDD'),
        ('over', 'Post Dates'),
        ('dd', 'Postpartum'),
        ('visit', 'Visit'),
        ('signup', 'From Signup'),
        ('connect', 'Reconnect'),
        ('bounce', 'Bounce'),
        ('loss', 'Loss'),
        ('stop', 'Stop'),
    )

    CONDITION_CHOICES = (
        ('art', 'Starting ART'),
        ('adolescent', 'Adolescent'),
        ('first', 'First Time Mother'),
        ('normal', 'Normal'),
        ('nbaby', 'No Baby'),
    )

    class Meta:
        app_label = 'mwhiv'

    objects = AutomatedMessageHIVQuerySet.as_manager()

    priority = models.IntegerField(default=0)

    english = models.TextField(blank=True)
    swahili = models.TextField(blank=True)
    luo = models.TextField(blank=True)

    comment = models.TextField(blank=True)

    group = models.CharField(max_length=20, choices=enums.GROUP_CHOICES)  # 2 groups
    hiv_messaging = models.BooleanField() # True or False
    second_preg = models.BooleanField()  # True or False

    def category(self):
        return "{0.send_base}.{0.group}.{0.condition}.{1}.{2}".format(self, 'Y' if self.hiv_messaging else 'N', 'Y' if self.second_preg else 'N')

    def description(self):
        return "{0}.{1}".format(self.category(), self.send_offset)

    def text_for(self, participant, extra_kwargs=None):
        text = self.get_language(participant.language)

        message_kwargs = participant.message_kwargs()
        if extra_kwargs is not None:
            message_kwargs.update(extra_kwargs)
        return text.format(**message_kwargs)

    def get_language(self, language):
        # TODO: Error checking
        return getattr(self, language)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<AutomatedMessageHIV: {}>".format(self.description())