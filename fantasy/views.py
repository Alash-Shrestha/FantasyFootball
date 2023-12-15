from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Match, MatchPointMapper, MatchWeek, MatchScore

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

        for player in victory_team.player_set.all():
            self.update_fantasy_team_points(player, 1)
            self.update_match_score(match, player, 1)

        for scorer in match.scorers.all():
            self.update_fantasy_team_points(scorer, point_mapper.score_point)
            self.update_match_score(match, scorer, point_mapper.score_point)

        for assistant in match.assists.all():
            self.update_fantasy_team_points(assistant, point_mapper.assist_point)
            self.update_match_score(match, assistant, point_mapper.assist_point)

    def update_fantasy_team_points(self, player, points):
        for fantasy_team in player.fantasyteam_set.all():
            fantasy_team.points += points
            fantasy_team.save()

    def update_match_score(self, match, player, points):
        match_score, created = MatchScore.objects.get_or_create(match=match, player=player)
        match_score.score += points
        match_score.save()
