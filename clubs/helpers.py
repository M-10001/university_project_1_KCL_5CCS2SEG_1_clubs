from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from clubs.models import User, Club, Membership, Tournament, Group, Participant, Grouping, TournamentMatch

def view_login_prohibited(function):
    def wrapper(request):
        if request.user.is_authenticated:
            return redirect(settings.USER_PAGE_URL)
        else:
            return function(request)

    return wrapper

def membership_check(request, club_id):
    try:
        club = Club.objects.get(id = club_id)
        membership = Membership.objects.get(club = club, member = request.user)
    except ObjectDoesNotExist:
        return False
    else:
        return True

def club_and_tournament_check(club_id, tournament_id):
    try:
        club = Club.objects.get(id = club_id)
        tournament = Tournament.objects.get(id = tournament_id, club = club)
    except ObjectDoesNotExist:
        return False
    else:
        return True

def view_club_requirements(function):
    def wrapper(request, club_id):
        if membership_check(request, club_id):
            return function(request, club_id)
        else:
            return redirect('user_page')
    return wrapper

def view_user_and_club_requirements(function):
    def wrapper(request, user_id, club_id):
        if membership_check(request, club_id):
            try:
                club = Club.objects.get(id = club_id)
                user = User.objects.get(id = user_id)
                member_membership = Membership.objects.get(club = club, member = user)
            except ObjectDoesNotExist:
                return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
            else:
                return function(request, user_id, club_id)
        else:
            return redirect('user_page')

    return wrapper

def view_tournament_requirements(function):
    def wrapper(request, club_id, tournament_id):
        if membership_check(request, club_id):
            if club_and_tournament_check(club_id, tournament_id):
                return function(request, club_id, tournament_id)
            else:
                return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))
        else:
            return redirect('user_page')

    return wrapper

def view_membership_and_tournament_requirements(function):
    def wrapper(request, club_id, membership_id, tournament_id):
        if membership_check(request, club_id):
            if club_and_tournament_check(club_id, tournament_id):
                try:
                    club = Club.objects.get(id = club_id)
                    member_membership = Membership.objects.get(id = membership_id, club = club)
                except ObjectDoesNotExist:
                    return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' :tournament_id}))
                else:
                    return function(request, club_id, membership_id, tournament_id)
            else:
                return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))
        else:
            return redirect('user_page')

    return wrapper

def view_tournament_match_and_tournament_requirements(function):
    def wrapper(request, club_id, tournament_id, tournament_match_id):
        if membership_check(request, club_id):
            if club_and_tournament_check(club_id, tournament_id):
                try:
                    tournament = Tournament.objects.get(id = tournament_id)
                    tournament_match = TournamentMatch.objects.get(id = tournament_match_id, tournament = tournament)
                except ObjectDoesNotExist:
                    return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))
                else:
                    return function(request, club_id, tournament_id, tournament_match_id)
            else:
                return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))
        else:
            return redirect('user_page')

    return wrapper

def check_membership_in_tournament(membership, tournament):
    try:
        participant = Participant.objects.get(tournament = tournament, member = membership)
    except ObjectDoesNotExist:
        return (membership == tournament.organiser) or (membership in tournament.co_organisers.all())
    else:
        return True

def create_groupings_for_group(tournament, group, participants):
    participant = participants[0]
    participants = participants.exclude(id = participant.id)
    matches_participated_limit = 0
    counter1 = 0

    while (counter1 < (group.total_participants_limit - 1)):
        counter2 = 0
        found = False

        while (found == False):
            tournament_matches = TournamentMatch.objects.filter(conclusion__isnull = False, tournament = tournament, player1__participant = participant, player2__participant = participants[counter2])
            tournament_matches = tournament_matches.union(TournamentMatch.objects.filter(conclusion__isnull = False, tournament = tournament, player1__participant = participants[counter2], player2__participant = participant))

            if (tournament_matches.count() == matches_participated_limit):
                found = True
                Grouping.objects.create(group = group, participant = participants[counter2])
                participants = participants.exclude(id = participants[counter2].id)
            else:
                if (counter2 == (participants.count() - 1)):
                    counter2 = 0
                    matches_participated_limit = matches_participated_limit + 1
                else:
                    counter2 = counter2 + 1

        counter1 = counter1 + 1

    Grouping.objects.create(group = group, participant = participant)
    return participants
