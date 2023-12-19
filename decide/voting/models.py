from django.db import models
from django.db.models import JSONField
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from base import mods
from base.models import Auth, Key


class Question(models.Model):
    desc = models.TextField(verbose_name=_('Description'))

    voting_types = [
        ('OQ', _('Optional Question')),
        ('YN', _('Yes/No Question')),
    ]

    types = models.CharField(max_length=2,
        choices=voting_types,
        default='YN',
        verbose_name=_('Type'),)
    
    vote_blank = models.BooleanField(default=False, verbose_name=_('Vote Blank'))

    def __str__(self):
        return self.desc
        
    def clean(self):
        if self.types == 'YN' and self.vote_blank:
            raise ValidationError(_("Vote Blank cannot be True for Yes/No question type."))
            
    def save(self, *args, **kwargs):
        if self.voting_types == 'YN':
            self.options = [_('Yes'), 'No']
        
        if self.types == 'YN' and self.vote_blank:
            raise ValidationError(_("Vote Blank cannot be True for Yes/No question type."))

        if (
            (self.types == 'OQ')
            and self.vote_blank
            and QuestionOption.objects.filter(
                question__id=self.id, option__startswith="Voto En Blanco"
            ).count()
            == 0
        ):
            enBlanco = QuestionOption(
                question=self, number=self.options.count() + 1, option="Voto En Blanco"
            )
            enBlanco.save()
            self.options.add(enBlanco)
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE, verbose_name=_('Question'))
    number = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Number'))
    option = models.TextField(verbose_name=_('Option'))

    def clean(self) -> None:
        if self.question.types == 'YN':
            if self.option not in [_('Yes'),_('No')]:
                raise ValidationError(_("This is a Yes/No question, option must be 'Yes' or 'No'."))
            if QuestionOption.objects.filter(question=self.question, option=self.option).exists():
                raise ValidationError(_("This option already exists for this question."))
            
    def save(self):
        if self.question.types == 'YN':
            if self.option not in [_('Yes'),_('No')]:
                raise ValidationError(_("This is a Yes/No question, option must be 'Yes' or 'No'."))
        if QuestionOption.objects.filter(question=self.question, option=self.option).exists():
                raise ValidationError(_("This option already exists for this question."))
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)
    
    class Meta:
        verbose_name = _('Question Option')
        verbose_name_plural = _('Question Options')


class Voting(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    desc = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE, verbose_name=_('Question'))

    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Start Date'))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_('End Date'))

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Public Key'))
    auths = models.ManyToManyField(Auth, related_name='votings', verbose_name=_('Auths'))

    tally = JSONField(blank=True, null=True, verbose_name=_('Tally'))
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        votes_format = []
        vote_list = []
        for vote in votes:
            for info in vote:
                if info == 'a':
                    votes_format.append(vote[info])
                if info == 'b':
                    votes_format.append(vote[info])
            vote_list.append(votes_format)
            votes_format = []
        return vote_list

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        opts = []
        for opt in options:
            if isinstance(tally, list):
                votes = tally.count(opt.number)
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })

        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Voting')
        verbose_name_plural = _('Votings')
