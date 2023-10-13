from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from clubs import helpers
from clubs import forms
from clubs.models import User, Club, Membership, Tournament, Co_oped, Group, Participant, Grouping, TournamentMatch

@helpers.view_login_prohibited
def home(request):
 return render(request, 'home.html')

@helpers.view_login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = forms.UserSignUpForm(data = request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_page')
    else:
        form = forms.UserSignUpForm()

    return render(request, 'sign_up.html', {'form' : form})

@helpers.view_login_prohibited
def log_in(request):
    next_url = ''

    if request.method == 'POST':
        next_url = request.POST.get('next') or 'user_page'
        form = forms.LogInForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email = email, password = password)

            if user is not None:
                login(request, user)
                redirect_url = next_url or 'user_page'
                return redirect(redirect_url)

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next_url = request.GET.get('next') or ''

    form = forms.LogInForm()
    return render(request, 'log_in.html', {'form' : form, 'next' : next_url})

@login_required
def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def user_page(request):
    memberships = Membership.objects.filter(member = request.user)
    return render(request, 'user_page.html', {'memberships' : memberships})

@login_required
def create_club(request):
    if request.method == 'POST':
        club_form = forms.ClubCreationForm(data = request.POST, prefix = 'club_form')
        ownership_form = forms.MembershipOwnerSignUpForm(data = request.POST, prefix = 'ownership_form')

        if (club_form.is_valid() and ownership_form.is_valid()):
            club = club_form.save()
            ownership_form.save(request.user, club)
            return redirect(reverse('club_page', kwargs = {'club_id' : club.id}))
    else:
        club_form = forms.ClubCreationForm(prefix = 'club_form')
        ownership_form = forms.MembershipOwnerSignUpForm(prefix = 'ownership_form')

    memberships = Membership.objects.filter(member = request.user)
    return render(request, 'create_club.html', {'memberships' : memberships, 'club_form' : club_form, 'ownership_form' : ownership_form})

@login_required
def membership_sign_up(request):
    if request.method == 'POST':
        form = forms.MembershipSignUpForm(data = request.POST, user = request.user)

        if form.is_valid():
            form.save()
            return redirect('user_page')
    else:
        form = forms.MembershipSignUpForm(user = request.user)

    memberships = Membership.objects.filter(member = request.user)
    return render(request, 'membership_sign_up.html', {'memberships' : memberships, 'form' : form})

@login_required
@helpers.view_club_requirements
def club_page(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    memberships = Membership.objects.filter(member = request.user)
    club_and_owner_membership = Membership.objects.get(club = club, member_type = Membership.MemberTypes.CLUB_OWNER)
    tournaments = Tournament.objects.filter(participant__won = True, is_active = False)
    return render(request, 'club_page.html', {'membership' : membership, 'memberships' : memberships, 'club_and_owner_membership' : club_and_owner_membership, 'tournaments' : tournaments})

@login_required
@helpers.view_club_requirements
def member_list(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if (membership.is_applicant() == False):
        if (membership.is_member()):
            membership_list = Membership.objects.filter(club = club, member__is_admin = False, member_type = Membership.MemberTypes.MEMBER)
        else:
            membership_list = Membership.objects.filter(club = club, member__is_admin = False)

        memberships = Membership.objects.filter(member = request.user)
        return render(request, 'member_list.html', {'membership' : membership, 'memberships' : memberships, 'membership_list' : membership_list})
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_user_and_club_requirements
def show_member(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    user = User.objects.get(id = user_id)
    member_membership = Membership.objects.get(club = club, member = user)

    if (membership.is_applicant() == False):
        if (user.is_staff == False):
            memberships = Membership.objects.filter(member = request.user)
            return render(request, 'show_member.html', {'membership' : membership, 'memberships' : memberships, 'member_membership': member_membership})
        else:
            return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_user_and_club_requirements
def decline_application(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    user = User.objects.get(id = user_id)
    member_membership = Membership.objects.get(club = club, member = user)

    if (membership.is_applicant() == False):
        if (user.is_staff == False and (member_membership.is_member() or membership.is_member() == False)):
            if (member_membership.is_applicant() and membership.is_member() == False):
                member_membership.delete()
                return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))

            return redirect(reverse('show_member', kwargs = {'user_id' : user_id, 'club_id' : club_id}))
        else:
            return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_user_and_club_requirements
def set_member(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    user = User.objects.get(id = user_id)
    member_membership = Membership.objects.get(club = club, member = user)

    if (membership.is_applicant() == False):
        if (user.is_staff == False and (member_membership.is_member() or membership.is_member() == False)):
            if (member_membership.is_applicant() and membership.is_member() == False):
                member_membership.member_type = Membership.MemberTypes.MEMBER
                member_membership.save()
            elif (member_membership.is_officer() and membership.is_club_owner()):
                member_membership.member_type = Membership.MemberTypes.MEMBER
                member_membership.save()

            return redirect(reverse('show_member', kwargs = {'user_id' : user_id, 'club_id' : club_id}))
        else:
            return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_user_and_club_requirements
def set_officer(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    user = User.objects.get(id = user_id)
    member_membership = Membership.objects.get(club = club, member = user)

    if (membership.is_applicant() == False):
        if (user.is_staff == False and (member_membership.is_member() or membership.is_member() == False)):
            if (member_membership.is_member() and membership.is_club_owner()):
                member_membership.member_type = Membership.MemberTypes.OFFICER
                member_membership.save()

            return redirect(reverse('show_member', kwargs = {'user_id' : user_id, 'club_id' : club_id}))
        else:
            return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_user_and_club_requirements
def set_owner(request, user_id, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)
    user = User.objects.get(id = user_id)
    member_membership = Membership.objects.get(club = club, member = user)

    if (membership.is_applicant() == False):
        if (user.is_staff == False and membership.is_member() == False):
            if (member_membership.is_officer() and membership.is_club_owner()):
                member_membership.member_type = Membership.MemberTypes.CLUB_OWNER
                member_membership.save()
                membership.member_type = Membership.MemberTypes.OFFICER
                membership.save()

            return redirect(reverse('show_member', kwargs = {'user_id' : user_id, 'club_id' : club_id}))
        else:
            return redirect(reverse('member_list', kwargs = {'club_id' : club_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_club_requirements
def application_edit(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if (membership.is_applicant()):
        if request.method == 'POST':
            form = forms.ApplicationEditForm(instance = membership, data = request.POST)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, "Profile updated!")
                return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))
        else:
            form = forms.ApplicationEditForm(instance = membership)

        memberships = Membership.objects.filter(member = request.user)
        return render(request, 'application_edit.html', {'membership' : membership, 'memberships' : memberships, 'form': form})
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_club_requirements
def create_tournament(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if(membership.is_applicant() == False and membership.is_member() == False):
        if request.method == 'POST':
            form = forms.TournamentCreationForm(data = request.POST)

            if form.is_valid():
                tournament = form.save(club, membership)
                messages.add_message(request, messages.SUCCESS, 'Tournament created.')
                return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament.id}))
        else:
            form = forms.TournamentCreationForm()

        memberships = Membership.objects.filter(member = request.user)
        return render(request, 'create_tournament.html', {'membership' : membership, 'memberships' : memberships, 'form' : form})
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_club_requirements
def joinable_tournaments(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if (membership.is_applicant() == False):
        memberships = Membership.objects.filter(member = request.user)
        tournaments = Tournament.objects.filter(club = club, is_active = True)
        tournaments = tournaments.exclude(participant__member = membership)
        tournaments = tournaments.exclude(organiser = membership)
        tournaments = tournaments.exclude(co_oped__co_organiser = membership)
        temp = tournaments

        for tournament in temp:
            if ((tournament.total_participants_limit <= tournament.total_participants()) or tournament.passed_deadline()):
                tournaments = tournaments.exclude(id = tournament.id)

        return render(request, 'joinable_tournaments.html', {'membership' : membership, 'memberships' : memberships, 'tournaments' : tournaments})
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_tournament_requirements
def participate_in_tournament(request, club_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)

    if (membership.is_applicant() == False):
        if helpers.check_membership_in_tournament(membership, tournament) or (tournament.total_participants_limit <= tournament.total_participants()) or tournament.passed_deadline():
            return redirect(reverse('joinable_tournaments', kwargs = {'club_id' : club_id}))
        else:
            Participant.objects.create(tournament = tournament, member = membership)
            return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_club_requirements
def member_tournaments(request, club_id):
    club = Club.objects.get(id = club_id)
    membership = Membership.objects.get(club = club, member = request.user)

    if (membership.is_applicant() == False):
        memberships = Membership.objects.filter(member = request.user)
        tournaments = Tournament.objects.filter(club = club, participant__member = membership)
        tournaments = tournaments.union(Tournament.objects.filter(club = club, organiser = membership))
        tournaments = tournaments.union(membership.co_oped_tournamets.filter(club = club))
        return render(request, 'member_tournaments.html', {'membership' : membership, 'memberships' : memberships, 'tournaments' : tournaments})
    else:
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_tournament_requirements
def tournament_page(request, club_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)
    memberships = Membership.objects.filter(member = request.user)

    if (helpers.check_membership_in_tournament(membership, tournament)):
        if tournament.is_active:
            try:
                participant = Participant.objects.get(tournament = tournament, member = membership)
            except ObjectDoesNotExist:
                groups = Group.objects.filter(tournament = tournament, is_active = True)
                return render(request, 'tournament_page.html', {
                        'membership' : membership,
                        'memberships': memberships,
                        'tournament' : tournament,
                        'groups' : groups
                    }
                )
            else:
                groups = Group.objects.filter(tournament = tournament, is_active = True)
                return render(request, 'tournament_page.html', {
                        'membership' : membership,
                        'memberships': memberships,
                        'tournament' : tournament,
                        'groups' : groups,
                        'participant' : participant
                    }
                )
        else:
            try:
                winner = Participant.objects.get(tournament = tournament, won = True)
            except ObjectDoesNotExist:
                return render(request, 'ended_tournament_page.html', {'membership' : membership, 'memberships': memberships, 'tournament' : tournament})
            else:
                return render(request, 'ended_tournament_page.html', {'membership' : membership, 'memberships': memberships, 'tournament' : tournament, 'winner' : winner})

    return redirect(reverse('member_tournaments', kwargs = {'club_id' : club_id}))

@login_required
@helpers.view_tournament_requirements
def available_officers_for_tournament(request, club_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)

    if ((tournament.organiser == membership) and tournament.is_active):
        membership_list = Membership.objects.filter(club = club, member_type = Membership.MemberTypes.OFFICER)
        membership_list = membership_list.exclude(co_oped__tournament = tournament)
        membership_list = membership_list.exclude(created_tournaments__organiser = membership)
        membership_list = membership_list.exclude(participant__tournament = tournament)
        memberships = Membership.objects.filter(member = request.user)

        return render(request, 'available_officers_for_tournament.html', {
                'membership' : membership,
                'memberships' : memberships,
                'tournament' : tournament,
                'membership_list' : membership_list
            }
        )
    else:
        return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))

@login_required
@helpers.view_membership_and_tournament_requirements
def add_co_organiser(request, club_id, membership_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)
    member_membership = Membership.objects.get(id = membership_id)

    if ((tournament.organiser == membership) and tournament.is_active):
        if (helpers.check_membership_in_tournament(member_membership, tournament) == False):
            Co_oped.objects.create(tournament = tournament, co_organiser = member_membership)

        return redirect(reverse('available_officers_for_tournament', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))
    else:
        return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))

@login_required
@helpers.view_tournament_requirements
def co_organiser_list(request, club_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)

    if ((tournament.organiser == membership) and tournament.is_active):
        co_organisers = Co_oped.objects.filter(tournament = tournament)
        memberships = Membership.objects.filter(member = request.user)

        return render(request, 'co_organiser_list.html', {
                'membership' : membership,
                'memberships' : memberships,
                'tournament' : tournament,
                'co_organisers' : co_organisers
            }
        )
    else:
        return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))

@login_required
@helpers.view_membership_and_tournament_requirements
def remove_co_organiser(request, club_id, membership_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)
    member_membership = Membership.objects.get(id = membership_id)

    if (tournament.organiser == membership):
        if helpers.check_membership_in_tournament(member_membership, tournament):
            Co_oped.objects.get(tournament = tournament, co_organiser = member_membership).delete()

        return redirect(reverse('co_organiser_list', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))
    else:
        return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))

@login_required
@helpers.view_tournament_requirements
def leave_tournament(request, club_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)

    if (membership in tournament.co_organisers.all()):
        Co_oped.objects.get(tournament = tournament, co_organiser = membership).delete()
        return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

    try:
        participant = Participant.objects.get(tournament = tournament, member = membership)
    except ObjectDoesNotExist:
        pass
    else:
        if (tournament.passed_deadline() == False):
            Participant.objects.get(tournament = tournament, member = membership).delete()
            return redirect(reverse('club_page', kwargs = {'club_id' : club_id}))

    return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))

@login_required
@helpers.view_tournament_requirements
def create_matches(request, club_id, tournament_id):
    tournament = Tournament.objects.get(id = tournament_id)
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)

    if (((membership == tournament.organiser) or (membership in tournament.co_organisers.all())) and tournament.is_active and (not TournamentMatch.objects.filter(tournament = tournament, conclusion__isnull = True)) and tournament.passed_deadline()):
        groups = Group.objects.filter(tournament = tournament, is_active = True)

        for group in groups:
            groupings = group.grouping_set.all()
            groupings = groupings.exclude(id = groupings[0].id)

            if (group.total_participants_limit >= 4):
                groupings = groupings.exclude(id = groupings[0].id)

            for grouping in groupings:
                participant = grouping.participant
                participant.eliminated = True
                participant.save()

            group.is_active = False
            group.save()

        participants = Participant.objects.filter(tournament = tournament, eliminated = False)
        counter = 1

        if participants.count() >= 32:
            while participants.count() > 1:
                group = Group.objects.create(tournament = tournament, type = Group.Types.GROUP, number = counter, total_participants_limit = 6)
                participants = helpers.create_groupings_for_group(tournament, group, participants)
                counter = counter + 1
        elif participants.count() >= 16:
            while participants.count() > 1:
                group = Group.objects.create(tournament = tournament, type = Group.Types.GROUP, number = counter, total_participants_limit = 4)
                participants = helpers.create_groupings_for_group(tournament, group, participants)
                counter = counter + 1
        elif participants.count() >= 8:
            while participants.count() > 1:
                group = Group.objects.create(tournament = tournament, type = Group.Types.QUARTER_FINAL, number = counter, total_participants_limit = 2)
                participants = helpers.create_groupings_for_group(tournament, group, participants)
                counter = counter + 1
        elif participants.count() >= 4:
            while participants.count() > 1:
                group = Group.objects.create(tournament = tournament, type = Group.Types.SEMI_FINAL, number = counter, total_participants_limit = 2)
                participants = helpers.create_groupings_for_group(tournament, group, participants)
                counter = counter + 1
        elif participants.count() >= 2:
            while participants.count() > 1:
                group = Group.objects.create(tournament = tournament, type = Group.Types.FINAL, number = None, total_participants_limit = 2)
                participants = helpers.create_groupings_for_group(tournament, group, participants)

        groups = Group.objects.filter(tournament = tournament, is_active = True)

        if groups:
            for group in groups:
                groupings = group.grouping_set.all()
                counter1 = 0

                while counter1 < (groupings.count() - 1):
                    counter2 = counter1 + 1

                    while counter2 < groupings.count():
                        TournamentMatch.objects.create(tournament = tournament, group = group, player1 = groupings[counter1], player2 = groupings[counter2])
                        counter2 = counter2 + 1

                    counter1 = counter1 + 1
        else:
            try:
                participant = Participant.objects.get(tournament = tournament, eliminated = False)
            except ObjectDoesNotExist:
                pass
            else:
                participant.won = True
                participant.eliminated = True
                participant.save()

            tournament.is_active = False
            tournament.save()

    return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))

@login_required
@helpers.view_tournament_match_and_tournament_requirements
def set_tournament_match(request, club_id, tournament_id, tournament_match_id):
    tournament_match = TournamentMatch.objects.get(id = tournament_match_id)
    tournament = tournament_match.tournament
    club = tournament.club
    membership = Membership.objects.get(club = club, member = request.user)
    memberships = Membership.objects.filter(member = request.user)

    if ((membership == tournament.organiser) or (membership in tournament.co_organisers.all())) and tournament.is_active and (tournament_match.concluded() == False):
        if request.method == 'POST':
            form = forms.SetTournamentMatchForm(instance = tournament_match, data = request.POST)

            if form.is_valid():
                form.save()
                return redirect(reverse('create_matches', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))
        else:
            form = forms.SetTournamentMatchForm(instance = tournament_match)

        return render(request, 'set_tournament_match.html', {'membership' : membership, 'memberships' : memberships, 'tournament' : tournament, 'form' : form, 'tournament_match' : tournament_match})

    return redirect(reverse('tournament_page', kwargs = {'club_id' : club_id, 'tournament_id' : tournament_id}))
