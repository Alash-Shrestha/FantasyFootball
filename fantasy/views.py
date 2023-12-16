from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Match, MatchPointMapper, MatchWeek, MatchScore, FantasyTeam, Article, Player
from django.views.generic import DetailView, ListView, CreateView
from core.mixins import CustomLoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
import json
from django.http import HttpResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from django.contrib.auth import get_user_model

User = get_user_model()

class SyncMatchPointsView(View):

    def get(self, request, *args, **kwargs):
        point_mapper = MatchPointMapper.objects.first()

        if not point_mapper:
            return JsonResponse({'error': 'MatchPointMapper configuration not found'}, status=500)
        
        active_week = MatchWeek.get_active_week()
        if active_week.sync_status:
            return JsonResponse({'error': 'The data is already synced for this week.'}, status=403)

        matches = Match.objects.filter(week=active_week)
        for match in matches:
            self.process_match(match, point_mapper)

        active_week.sync_status = True
        active_week.save()

        return JsonResponse({'message': 'Match points synced successfully'})


    def process_match(self, match, point_mapper):
        victory_team = match.home_team if match.home_team_score > match.away_team_score else match.away_team
        processed_players = set()

        for player in victory_team.player_set.all():
            self.update_fantasy_team_points(player, 1)
            self.update_match_score(match, player, 1)

        for scorer in match.scorers.all():
            self.update_fantasy_team_points(scorer, point_mapper.score_point)
            self.update_match_score(match, scorer, point_mapper.score_point)
            processed_players.add(scorer)

        for assistant in match.assists.all():
            self.update_fantasy_team_points(assistant, point_mapper.assist_point)
            self.update_match_score(match, assistant, point_mapper.assist_point)
            processed_players.add(assistant)

        all_players = set(match.home_team.player_set.all()) | set(match.away_team.player_set.all())
        zero_point_players = all_players - processed_players
        for player in zero_point_players:
            self.update_match_score(match, player, 0)

    def update_fantasy_team_points(self, player, points):
        for fantasy_team in player.fantasyteam_set.all():
            fantasy_team.points += points
            fantasy_team.save()

    def update_match_score(self, match, player, points):
        match_score, created = MatchScore.objects.get_or_create(match=match, player=player)
        match_score.score += points
        match_score.save()



class MyTeamView(CustomLoginRequiredMixin, DetailView):
    model = FantasyTeam
    template_name = 'fantasy/points.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        active_week = self.get_object().active_week.week
        context['game_weeks'] = MatchWeek.objects.filter(week__gte=active_week)

        # Get the selected game week from the request or use the active week
        selected_week_id = self.request.GET.get('gw')
        if selected_week_id:
            selected_week = MatchWeek.objects.get(pk=selected_week_id)
        else:
            selected_week = self.object.active_week
        context['selected_week_id'] = selected_week_id

        context['player_and_points'] = self.get_player_points(selected_week)
        return context

    def get_player_points(self, week):
        team_players = self.object.players.all()

        if week:
            match_scores = MatchScore.objects.filter(
                match__week=week,
                player__in=team_players
            )
        else:
            # Sum the scores from the active week onwards
            match_scores = MatchScore.objects.filter(
                match__week__gte=self.object.active_week,
                player__in=team_players
            )

        player_points = match_scores.values(
            'player__name'
        ).annotate(
            total_points=Sum('score')
        ).order_by('player__name')

        return {item['player__name']: item['total_points'] for item in player_points}


class LeaderBoard(ListView):
    model = FantasyTeam
    template_name = 'fantasy/leaderboard.html'

    def get_queryset(self) -> QuerySet[Any]:
        print(super().get_queryset())
        print('all')
        if not self.request.user.is_authenticated:
            return super().get_queryset().filter(deleted_at=None)[:5]
        else:
            return super().get_queryset().filter(deleted_at=None)[:25]
        

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'fantasy/article.html'


class CreateFantasyTeam(CustomLoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        context = {
            'players': Player.objects.all()
        }
        return render(request, 'fantasy/create_team.html', context)
    
    def post(self, request, *args, **kwargs):
        if self.request.user.fantasyteam.all():
            messages.error(self.request, 'You already have a team and cannot create another.')
            redirect_url = reverse('fantasy:my-team-overall', kwargs={'pk': self.request.user.fantasyteam.first().pk})
            return JsonResponse({
                'error': 'You already have a team and cannot create another.',
                'redirect_url': redirect_url
            })
        data = json.loads(self.request.body)
        if data['teamName'] and data['players']:
            obj = FantasyTeam.objects.create(
                name= data['teamName'],
                user = self.request.user,
                active_week = MatchWeek.get_active_week()
            )

            for player in data['players']:
                obj.players.add(Player.objects.get(pk=player))

            messages.success(self.request, 'Your team was created successfully.')
            redirect_url = reverse('fantasy:my-team-overall', kwargs={'pk': obj.pk})
            return JsonResponse({
                'message': 'Your team was created successfully.',
                'redirect_url': redirect_url
            })
        raise PermissionDenied