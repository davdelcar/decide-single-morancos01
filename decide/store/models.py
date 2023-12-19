from django.db import models
from base.models import BigBigField
from django.utils.translation import gettext_lazy as _


class Vote(models.Model):
    voting_id = models.PositiveIntegerField(verbose_name=_('Voting ID'))    
    voter_id = models.PositiveIntegerField(verbose_name=_('Voter ID'))

    a = BigBigField()
    b = BigBigField()

    voted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}: {}'.format(self.voting_id, self.voter_id)
    
    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
