from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Census(models.Model):
    voting_id = models.PositiveIntegerField(verbose_name=_('Voting ID'))
    voter_id = models.PositiveIntegerField(verbose_name=_('Voter ID'))  

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)
        verbose_name = _('Census')
        verbose_name_plural = _('Census')
