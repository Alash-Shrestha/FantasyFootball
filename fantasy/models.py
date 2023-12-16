from django.db import models
from django.contrib.auth import get_user_model
from core.models import DateModel
from django.db.models import Sum
from django.urls import reverse

User = get_user_model()

class MatchWeek(DateModel):
    week = models.IntegerField(default=1)
    sync_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.week)
    
    class Meta:
        ordering= ('-created_at',)
    
    @classmethod
    def get_active_week(cls):
        return cls.objects.first()


class Team(DateModel):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='teams/logo/', blank=True, null=True)

    def __str__(self):
        return self.name


class Player(DateModel):
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


    def __str__(self):
        return f"{self.name} ({self.team.name})"


class FantasyTeam(DateModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name='fantasyteam', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    players = models.ManyToManyField(Player, blank=True)
    active_week = models.ForeignKey(MatchWeek, null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.name} - {self.user.full_name}"

    def get_absolute_url(self):
        return reverse('fantasy:my-team-overall', kwargs={
            'pk': self.pk
        })
    
    def player_and_points(self):
        if not self.active_week:
            return {}

        team_players = self.players.all()
        print('total players: ',team_players)

        match_scores = MatchScore.objects.filter(
            match__week=self.active_week,
            player__in=team_players
        )

        player_points = match_scores.values(
            'player__name'
        ).annotate(
            total_points=Sum('score')
        ).order_by('player__name')

        # Convert to a dictionary or a suitable format
        player_points_dict = {item['player__name']: item['total_points'] for item in player_points}
        print('point dict: ',player_points_dict)

        return player_points_dict
    
    class Meta:
        ordering = ('-points',)

class Match(DateModel):
    week = models.ForeignKey(MatchWeek, null=True, blank=True, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name='home_team', on_delete=models.DO_NOTHING)
    away_team = models.ForeignKey(Team, related_name='away_team', on_delete=models.DO_NOTHING)
    home_team_score = models.IntegerField(default=0)
    away_team_score = models.IntegerField(default=0)
    scorers = models.ManyToManyField(Player, related_name='scorers')
    assists = models.ManyToManyField(Player, related_name='assists')


    def __str__(self):
        return f"{self.home_team} {self.home_team_score} - {self.away_team_score} {self.away_team}"


class MatchScore(DateModel):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)


    def __str__(self):
        return f"Match: {self.match.pk} Player: {self.player} Score: {self.score}"


class MatchPointMapper(DateModel):
    score_point = models.IntegerField(default=3)
    assist_point = models.IntegerField(default=2)

    def __str__(self):
        return f"score: {self.score_point} assist: {self.assist_point}"
    
    def save(self, *args, **kwargs):
        existing_instances_count = MatchPointMapper.objects.count()

        if existing_instances_count > 0 and self.pk is None:
            raise ValueError("Only one instance of MatchPointMapper is allowed.")

        super().save(*args, **kwargs)



class Article(DateModel):
    title = models.CharField(max_length=300)
    description = models.TextField()
    image = models.ImageField(upload_to='news/images/', null=True, blank=True)

    def __str__(self):
        return self.title
    
    @property
    def title_photo(self):
        if self.image:
            return self.image.url
        return 'https://assets.gopromotional.co.uk/images/article-placeholder.jpg'
    
    def get_absolute_url(self):
        return reverse('fantasy:article-detail', 
                       kwargs={
                           'pk':self.pk
                       })
    
    