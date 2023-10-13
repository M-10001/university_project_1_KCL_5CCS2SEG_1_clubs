from django.utils import timezone
from django import forms
from django.core.validators import RegexValidator
from clubs.models import User, Club, Membership, Tournament, TournamentMatch
from django.contrib.auth import authenticate

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
        return user

class UserSignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['email',]

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )

    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""

        super().save(commit=False)

        user = User.objects.create_user(
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password')
        )

        return user

class ClubCreationForm(forms.ModelForm):
    """Enables creation of clubs."""

    class Meta:
        """Form options"""

        model = Club
        fields = ['name', 'location', 'description']
        widgets = {'location' : forms.Textarea(), 'description' : forms.Textarea()}
        labels = {'name' : 'Club name', 'location' : 'Club location', 'description' : 'Club description'}

class MembershipOwnerSignUpForm(forms.ModelForm):
    """Enables registered users, not part of the clubs, to become owners of the clubs."""

    class Meta:
        """Form options."""

        model = Membership
        fields = ['member_first_name', 'member_last_name', 'member_contact_details', 'member_personal_statement', 'member_bio', 'member_chess_experience_level']
        widgets = { 'member_personal_statement': forms.Textarea(), 'member_bio': forms.Textarea()}
        labels = {'member_first_name':'First name', 'member_last_name':'Last name', 'member_contact_details':'Contact details',
        'member_personal_statement':'Personal Statement', 'member_bio':'Biography', 'member_chess_experience_level':'Chess Experience Level'}

    def save(self, user, club):
        """Create new membership."""

        super().save(commit=False)

        membership = Membership.objects.create(
            club = club,
            member = user,
            member_first_name=self.cleaned_data.get('member_first_name'),
            member_last_name=self.cleaned_data.get('member_last_name'),
            member_contact_details=self.cleaned_data.get('member_contact_details'),
            member_personal_statement=self.cleaned_data.get('member_personal_statement'),
            member_bio=self.cleaned_data.get('member_bio'),
            member_chess_experience_level=self.cleaned_data.get('member_chess_experience_level'),
            member_type = Membership.MemberTypes.CLUB_OWNER
        )

        return membership

class MembershipSignUpForm(forms.ModelForm):
    """Enables registered users to sign up to become club members."""

    club = forms.ModelChoiceField(queryset = None, to_field_name = 'name', label = 'Clubs')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['club'].queryset = Club.objects.exclude(membership__member = self.user)

    class Meta:
        """Form options."""

        model = Membership
        fields = ['member_first_name', 'member_last_name', 'member_contact_details', 'member_personal_statement', 'member_bio', 'member_chess_experience_level']
        widgets = { 'member_personal_statement': forms.Textarea(), 'member_bio': forms.Textarea()}
        labels = {'member_first_name':'First name', 'member_last_name':'Last name', 'member_contact_details':'Contact details',
        'member_personal_statement':'Personal Statement', 'member_bio':'Biography', 'member_chess_experience_level':'Chess Experience Level'}

    def save(self):
        """Create new membership."""

        super().save(commit=False)

        membership = Membership.objects.create(
            club = self.cleaned_data.get('club'),
            member = self.user,
            member_first_name=self.cleaned_data.get('member_first_name'),
            member_last_name=self.cleaned_data.get('member_last_name'),
            member_contact_details=self.cleaned_data.get('member_contact_details'),
            member_personal_statement=self.cleaned_data.get('member_personal_statement'),
            member_bio=self.cleaned_data.get('member_bio'),
            member_chess_experience_level=self.cleaned_data.get('member_chess_experience_level'),
            member_type = Membership.MemberTypes.APPLICANT
        )

        return membership

class ApplicationEditForm(forms.ModelForm):
    """Form to update user personal information."""

    class Meta:
        """Form options."""

        model = Membership
        fields = ['member_first_name', 'member_last_name', 'member_contact_details', 'member_personal_statement', 'member_bio', 'member_chess_experience_level']
        widgets = { 'member_personal_statement': forms.Textarea(),'member_bio': forms.Textarea()}
        labels = {'member_first_name':'First name', 'member_last_name':'Last name', 'member_contact_details':'Contact details',
        'member_personal_statement':'Personal Statement', 'member_bio':'Biography', 'member_chess_experience_level':'Chess Experience Level'}

class TournamentCreationForm(forms.ModelForm):
    """Enables officers and club owners to create tournaments."""

    class Meta:
        """Form options."""

        model = Tournament
        fields = ['name', 'description', 'deadline', 'total_participants_limit']
        widgets = {'description' : forms.Textarea()}
        labels = {'deadline' : 'Deadline(UTC+0) Format[YYYY-MM-DD HH:MM(:SS.)]'}

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        deadline = self.cleaned_data.get('deadline')

        if (deadline and deadline <= timezone.now()):
            self.add_error('deadline', 'Dealine can not be lesser than now.')

    def save(self, club, membership):
        """Create new tournament."""

        super().save(commit = False)

        tournament = Tournament.objects.create(
            club = club,
            organiser = membership,
            name = self.cleaned_data.get('name'),
            description = self.cleaned_data.get('description'),
            deadline = self.cleaned_data.get('deadline'),
            total_participants_limit = self.cleaned_data.get('total_participants_limit')
        )

        return tournament

class SetTournamentMatchForm(forms.ModelForm):
    """Enables setting of end of tournament match."""

    class Meta:
        """Form options."""

        model = TournamentMatch
        fields = ['conclusion',]

    def save(self):
        """Save tournament match."""

        super().save(commit = False)
        conclusion = self.cleaned_data.get('conclusion')
        tournament_match = self.instance

        if (conclusion == TournamentMatch.ConclusionTypes.DRAW):
            player1_addition = 0.5
            player2_addition = 0.5
        elif (conclusion == TournamentMatch.ConclusionTypes.PLAYER_1_WINS):
            player1_addition = 1
            player2_addition = 0
        else:
            player1_addition = 0
            player2_addition = 1

        player1 = tournament_match.player1
        player2 = tournament_match.player2
        player1.points_in_group = tournament_match.player1.points_in_group + player1_addition
        player2.points_in_group = tournament_match.player2.points_in_group + player2_addition
        player1.save()
        player2.save()
        tournament_match.conclusion = conclusion
        tournament_match.save()
        return tournament_match
