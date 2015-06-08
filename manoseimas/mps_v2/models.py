from django.db import models
from autoslug import AutoSlugField

from django.utils.translation import ugettext_lazy as _

from sboard.models import NodeForeignKey

from manoseimas.utils import reify


class CrawledItem(models.Model):
    source = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_mp_full_name(mp):
    return mp.full_name


class ParliamentMember(CrawledItem):
    slug = AutoSlugField(populate_from=get_mp_full_name)
    source_id = models.CharField(max_length=16)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    date_of_birth = models.CharField(max_length=16, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    candidate_page = models.URLField(blank=True, null=True)
    raised_by = models.ForeignKey('PoliticalParty', blank=True, null=True)
    photo = models.ImageField(upload_to='profile_images',
                              blank=True, null=True)
    term_of_office = models.CharField(max_length=32, blank=True, null=True)

    office_address = models.TextField(blank=True, null=True)
    constituency = models.CharField(max_length=128, blank=True, null=True)
    party_candidate = models.BooleanField(default=True)
    groups = models.ManyToManyField('Group', through='GroupMembership',
                                    related_name='members')

    biography = models.TextField(blank=True, null=True)

    @property
    def full_name(self):
        return u' '.join([self.first_name, self.last_name])

    def __unicode__(self):
        return self.full_name

    @property
    def fractions(self):
        return self.groups.filter(type=Group.TYPE_FRACTION)

    @property
    def fraction(self):
        ''' Current parliamentarian's fraction. '''
        if getattr(self, '_fraction'):
            return self._fraction[0].group
        else:
            membership = GroupMembership.objects.filter(
                member=self,
                group__type=Group.TYPE_FRACTION,
                until=None
            )[:]

            if membership:
                self._fraction = membership
                return membership[0].group
            else:
                return None

    def get_statement_count(self):
        return self.statements.filter(as_chairperson=False).count()

    def get_long_statement_count(self):
        return self.statements.filter(as_chairperson=False).\
            filter(word_count__gte=50).count()

    def get_long_statement_percentage(self):
        statements = self.get_statement_count()
        long_statements = self.get_long_statement_count()
        return (float(long_statements) / statements * 100
                if statements else 0.0)

    def get_discussion_contribution_percentage(self):
        all_discussions = StenogramTopic.objects.count()
        contributed_discusions = StenogramStatement.objects.\
            filter(speaker=self, as_chairperson=False).\
            aggregate(topics=models.Count('topic_id',
                                          distinct=True))
        return (float(contributed_discusions['topics'])
                / all_discussions * 100.0) if all_discussions else 0.0

    @property
    def votes(self):
        # Avoiding circular imports
        from manoseimas.votings.models import get_mp_votes
        return get_mp_votes(self.source_id)

    def get_vote_percentage(self):
        from manoseimas.votings.models import get_total_votes
        votes = sum(self.votes.values()) if self.votes else 0
        total_votes = get_total_votes()
        vote_percentage = float(votes) / total_votes * 100.0
        return vote_percentage

    @property
    def all_statements(self):
        return self.statements.all()


class PoliticalParty(CrawledItem):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Group(CrawledItem):
    TYPE_GROUP = 'group'
    TYPE_COMMITTEE = 'committee'
    TYPE_COMMISSION = 'commission'
    TYPE_FRACTION = 'fraction'
    TYPE_PARLIAMENT = 'parliament'

    GROUP_TYPES = (
        (TYPE_GROUP, _('Group')),
        (TYPE_COMMITTEE, _('Committee')),
        (TYPE_COMMISSION, _('Commission')),
        (TYPE_FRACTION, _('Fraction')),
        (TYPE_PARLIAMENT, _('Parliament')),
    )

    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from='name')
    type = models.CharField(max_length=64,
                            choices=GROUP_TYPES)
    displayed = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='fraction_logos',
                             blank=True, null=True)

    class Meta:
        unique_together = (('name', 'type'))

    def __unicode__(self):
        return u'{} ({})'.format(self.name, self.type)

    @property
    def active_members(self):
        return self.members.filter(groupmembership__until=None)

    @reify
    def active_member_count(self):
        return self.active_members.count()

    def get_avg_statement_count(self):
        agg = self.active_members.annotate(
            models.Count('statements')
        ).aggregate(
            avg_statements=models.Avg('statements__count')
        )
        return agg['avg_statements']

    def get_avg_long_statement_count(self):
        agg = self.active_members.filter(
            statements__word_count__gte=50
        ).annotate(
            models.Count('statements')
        ).aggregate(
            avg_statements=models.Avg('statements__count')
        )
        return agg['avg_statements']

    def get_avg_vote_percentage(self):
        total_percentage = 0.0
        for member in self.active_members:
            total_percentage += member.get_vote_percentage()
        return total_percentage / self.active_members.count()


class GroupMembership(CrawledItem):
    member = models.ForeignKey(ParliamentMember,
                               related_name='groupmembership')
    group = models.ForeignKey(Group)
    position = models.CharField(max_length=128)
    since = models.DateField(blank=True, null=True)
    until = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u'{} - {} ({})'.format(self.group.name,
                                      self.member.full_name,
                                      self.position)


class Stenogram(CrawledItem):
    source_id = models.CharField(max_length=16, db_index=True)
    date = models.DateField()
    sitting_no = models.IntegerField()
    sitting_name = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'{} Nr. {}'.format(self.date, self.sitting_no)


class StenogramTopic(CrawledItem):
    stenogram = models.ForeignKey(Stenogram, related_name='topics')
    title = models.TextField()
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return self.title[:160]


class StenogramStatement(CrawledItem):
    topic = models.ForeignKey(StenogramTopic, related_name='statements')
    speaker = models.ForeignKey(ParliamentMember, related_name='statements',
                                blank=True, null=True)
    speaker_name = models.CharField(max_length=64)
    as_chairperson = models.BooleanField(default=False)
    text = models.TextField()
    word_count = models.PositiveIntegerField(default=0)

    def get_speaker_name(self):
        return self.speaker.full_name if self.speaker else self.speaker_name

    def __unicode__(self):
        return u'{}: {}'.format(self.get_speaker_name(), self.text[:160])


class Voting(models.Model):
    stenogram_topic = models.ForeignKey(StenogramTopic, related_name='votings')
    node = NodeForeignKey()
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('stenogram_topic', 'node')


def percentile_property(attr):
    def inner_fn(self):
        total = self.__class__.objects.count()
        return int((total - getattr(self, attr) + 1.0)
                   / total * 100 + 0.5)
    return property(inner_fn)


class Ranking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    votes_rank = models.IntegerField(default=0)
    statement_count_rank = models.IntegerField(default=0)
    long_statement_count_rank = models.IntegerField(default=0)
    discusion_contribution_percentage_rank = models.IntegerField(default=0)

    class Meta:
        abstract = True

    votes_percentile = percentile_property(
        'votes_rank')
    statement_count_percentile = percentile_property(
        'statement_count_rank')
    long_statement_count_percentile = percentile_property(
        'long_statement_count_rank')
    discusion_contribution_percentage_percentile = percentile_property(
        'discusion_contribution_percentage_rank')


class MPRanking(Ranking):
    target = models.OneToOneField(ParliamentMember,
                                  related_name='ranking')


class GroupRanking(Ranking):
    target = models.OneToOneField(Group,
                                  related_name='ranking')
