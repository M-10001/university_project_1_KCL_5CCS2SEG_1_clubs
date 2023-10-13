from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from libgravatar import Gravatar

class UserManager(BaseUserManager):

    def create_user(self, email, password = None):
        """
        Creates and saves a user with the given email,
        first_name, last_name, contact_details, bio,
        personal_statement, chess_experience_level,
        and password.
        """

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email = self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, password = None):
        """
        Creates and saves a superuser with the given email,
        first_name, last_name, contact_details, bio,
        personal_statement, chess_experience_level,
        and password.
        """

        user = self.create_user(
            email,
            password = password,
        )

        user.is_admin = True
        user.save(using = self._db)
        return user

class User(AbstractBaseUser):

    email = models.EmailField(
        verbose_name = 'email address',
        max_length = 255,
        unique = True,
    )

    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)
    clubs = models.ManyToManyField('Club', through = 'Membership')

    # The handler of certain methods for the user model, for example creating user and adding to database.
    objects = UserManager()

    # The primary field to be used to differentiate user.
    USERNAME_FIELD = 'email'

    # Fields prompted when creating superuser. Have default values in UserManager class for those not listed here.
    REQUIRED_FIELDS = []

    def gravatar(self, size=120):
       """Return a URL to the user's gravatar."""
       gravatar_object = Gravatar(self.email)
       gravatar_url = gravatar_object.get_image(size=size, default='mp')
       return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Club(models.Model):

    name = models.CharField(max_length = 50, blank = False, unique = True)
    location = models.CharField(max_length = 100, blank = False)
    description = models.CharField(max_length = 500, blank = False)

    def total_members(self):
        """Return total members in club."""
        return self.user_set.count()

    def __str__(self):
        return self.name

class Membership(models.Model):

    # Used against chess_experience_level to check what level of chess experience, or to set chess_experience_level.
    class MemberChessExperienceLevels(models.IntegerChoices):

        BEGINNER = 0, 'Beginner'
        INTERMEDIATE = 1, 'Intermediate'
        EXPERT = 2, 'Expert'
        MASTER = 3, 'Master'

    # Used against member_type to check what level of membership to the club, or to set member_type.
    class MemberTypes(models.IntegerChoices):

        APPLICANT = 0, 'Applicant'
        MEMBER = 1, 'Member'
        OFFICER = 2, 'Officer'
        CLUB_OWNER = 3, 'Club owner'

    club = models.ForeignKey(Club, on_delete = models.CASCADE, blank = False)
    member = models.ForeignKey(User, on_delete = models.CASCADE, blank = False)
    member_first_name = models.CharField(max_length = 50, blank = False)
    member_last_name = models.CharField(max_length = 50, blank = False)
    member_contact_details = models.CharField(max_length = 100, blank = False)
    member_personal_statement = models.CharField(max_length = 200, blank = True)
    member_bio = models.CharField(max_length = 500, blank = True)

    # The chess chess experience level of the member in this membership according to ChessExperienceLevels.
    member_chess_experience_level = models.IntegerField(
        blank = False,
        choices = MemberChessExperienceLevels.choices
    )

    # The type of member in this membership according to MemberTypes.
    member_type = models.IntegerField(
        blank = False,
        choices = MemberTypes.choices
    )

    def member_full_name(self):
        """Return full name of member."""
        return self.member_first_name + ' ' + self.member_last_name

    def member_chess_experience_level_label(self):
        """Return chess_experience_level as label."""
        for member_chess_experience_level_tuple in Membership.MemberChessExperienceLevels.choices:
            if (self.member_chess_experience_level in member_chess_experience_level_tuple):
                return member_chess_experience_level_tuple[1]

    def member_type_label(self):
        """Return member_type as label."""
        for member_type_tuple in Membership.MemberTypes.choices:
            if (self.member_type in member_type_tuple):
                return member_type_tuple[1]

    def is_applicant(self):
        """Checks if member type is applicant."""
        return (self.member_type == Membership.MemberTypes.APPLICANT)

    def is_member(self):
        """Checks if member type is member."""
        return (self.member_type == Membership.MemberTypes.MEMBER)

    def is_officer(self):
        """Checks if member type is officer."""
        return (self.member_type == Membership.MemberTypes.OFFICER)

    def is_club_owner(self):
        """Checks if member type is club owner."""
        return (self.member_type == Membership.MemberTypes.CLUB_OWNER)

    class Meta:

        unique_together = [['club', 'member']]

class Tournament(models.Model):

    club = models.ForeignKey('Club', on_delete = models.CASCADE, blank = False)
    organiser = models.ForeignKey('Membership', on_delete = models.CASCADE, blank = False, related_name = 'created_tournaments')
    co_organisers = models.ManyToManyField('Membership', through = 'Co_oped', related_name = 'co_oped_tournamets')
    is_active = models.BooleanField(blank = False, default = True)
    name = models.CharField(max_length = 50, blank = False)
    description = models.CharField(max_length = 200, blank = False)
    deadline = models.DateTimeField(blank = False)

    total_participants_limit = models.IntegerField(
        blank = False,
        validators = [
            MinValueValidator(
                limit_value = 2,
                message = 'Total number of participants, can not be lower than 2.'
            ),
            MaxValueValidator(
                limit_value = 96,
                message = 'Total number of participants, can not be greater than 96.'
            )
        ]
    )

    def passed_deadline(self):
        """Checks if deadline is passed."""
        return self.deadline < timezone.now()

    def get_winner(self):
        """Return winner of tournament."""
        return self.participant_set.filter(won = True)

    def total_participants(self):
        """Returns total number of participants in tournament."""
        return self.participant_set.count()

    def _validation_check(self):
        """Validation for fields."""
        if self.club != self.organiser.club:
            raise ValidationError('Club has to be same as club of organiser.')
        if self.organiser.member_type == Membership.MemberTypes.APPLICANT:
            raise ValidationError('Organiser can not be of member type applicant.')

    def save(self, *args, **kwargs):
        """Save object."""
        self._validation_check()
        super().save(*args, **kwargs)

class Co_oped(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete = models.CASCADE, blank = False)
    co_organiser = models.ForeignKey('Membership', on_delete = models.CASCADE, blank = False)

    class Meta:

        unique_together = [['tournament', 'co_organiser']]

    def _validation_check(self):
        """Validation for fields."""
        if self.tournament.club != self.co_organiser.club:
            raise ValidationError('Club of tournament must be same as club of co_organiser.')
        if self.tournament.organiser == self.co_organiser:
            raise ValidationError('Organiser of tournament must not be co_organiser of tournament.')
        if self.co_organiser.member_type == Membership.MemberTypes.APPLICANT:
            raise ValidationError('Co-organiser can not be of member type applicant.')

    def save(self, *args, **kwargs):
        """Save object."""
        self._validation_check()
        super().save(*args, **kwargs)


class Group(models.Model):

    # Used against type to check type of group, or to set group_type.
    class Types(models.IntegerChoices):

        GROUP = 0, 'Group'
        QUARTER_FINAL = 1, 'Quarter final'
        SEMI_FINAL = 2, 'Semi final'
        FINAL = 3, 'Final'

    tournament = models.ForeignKey('Tournament', on_delete = models.CASCADE, blank = False)
    is_active = models.BooleanField(blank = False, default = True)

    # The type of group in this tournament match according to GroupTypes.
    type = models.IntegerField(
        blank = False,
        choices = Types.choices
    )

    number = models.IntegerField(
        null = True,
        blank = True,
        default = None,
        validators = [
            MinValueValidator(
                limit_value = 1,
                message = 'Group number, can not be lower than 1.'
            )
        ]
    )

    total_participants_limit = models.IntegerField(
        blank = False,
        validators = [
            MinValueValidator(
                limit_value = 2,
                message = 'Total number of group participants, can not be lower than 2.'
            )
        ]
    )

    def type_label(self):
        """Return type as label."""
        for type_tuple in Group.Types.choices:
            if (self.type in type_tuple):
                return type_tuple[1]

    def has_active_matches(self):
        """Return if this group has active matches."""
        if TournamentMatch.objects.filter(group = self, conclusion__isnull = True):
            return True
        else:
            return False

    class Meta:

        ordering = ['number']

    def _validation_check(self):
        """Validation for fields."""
        if self.number and self.type == Group.Types.FINAL:
            raise ValidationError('Null can only be provided for number, when and only when type is Types.FINAL.')
        if (not self.number) and (self.type != Group.Types.FINAL):
            raise ValidationError('Null can only be provided for number, when and only when type is Types.FINAL.')

    def save(self, *args, **kwargs):
        """Save object."""
        self._validation_check()
        super().save(*args, **kwargs)

class Participant(models.Model):

    tournament = models.ForeignKey('Tournament', on_delete = models.CASCADE, blank = False)
    member = models.ForeignKey('Membership', on_delete = models.CASCADE, blank = False)
    eliminated = models.BooleanField(blank = False, default = False)
    won = models.BooleanField(blank = False, default = False)

    class Meta:

        unique_together = [['tournament', 'member']]

    def _validation_check(self):
        """Validation for fields."""
        if self.tournament.club != self.member.club:
            raise ValidationError('Club of tournament has to be same as club of member.')
        if self.member.member_type == Membership.MemberTypes.APPLICANT:
            raise ValidationError('Member can not be of member type applicant.')
        if (self.won == True) and Participant.objects.filter(tournament = self.tournament, won = True):
            raise ValidationError('Can not have more than one winner.')

    def save(self, *args, **kwargs):
        """Save object."""
        self._validation_check()
        super().save(*args, **kwargs)

class Grouping(models.Model):

    group = models.ForeignKey('Group', on_delete = models.CASCADE, blank = False)
    participant = models.ForeignKey('Participant', on_delete = models.CASCADE, blank = False)
    points_in_group = models.FloatField(blank = False, default = 0)

    class Meta:

        unique_together = [['group', 'participant']]
        ordering = ['points_in_group']

    def _validation_check(self):
        """Validation for fields."""
        if self.group.tournament != self.participant.tournament:
            raise ValidationError('Tournament of group has to be same as tournament of participant.')
        if ((not self.id) and (self.group.total_participants_limit <= Grouping.objects.filter(group = self.group).count())):
            raise ValidationError('Can not create more groupings than group total participants limit.')

    def save(self, *args, **kwargs):
        """Save object."""
        self._validation_check()
        super().save(*args, **kwargs)

class TournamentMatch(models.Model):

    # Used against conslusion to check type of conclusion, or to set conclusion.
    class ConclusionTypes(models.IntegerChoices):

        DRAW = 0, 'Draw'
        PLAYER_1_WINS = 1, 'Player 1 wins'
        PLAYER_2_WINS = 2, 'Player 2 wins'

    tournament = models.ForeignKey('Tournament', on_delete = models.CASCADE, blank = False)
    group = models.ForeignKey('Group', on_delete = models.CASCADE, blank = False)
    player1 = models.ForeignKey('Grouping', on_delete = models.CASCADE, blank = False, related_name = 'match_as_player1')
    player2 = models.ForeignKey('Grouping', on_delete = models.CASCADE, blank = False, related_name = 'match_as_player2')

    # The type of conclusion in this tournament match according to ConlcusionTypes.
    conclusion = models.IntegerField(
        null = True,
        blank = False,
        choices = ConclusionTypes.choices,
        default = None
    )

    def conclusion_label(self):
        """Return conclusion as label."""
        for conclusion_tuple in TournamentMatch.ConclusionTypes.choices:
            if (self.conclusion in conclusion_tuple):
                return conclusion_tuple[1]

    def concluded(self):
        """Return if match concluded."""
        return self.conclusion != None

    class Meta:

        unique_together = [['group', 'player1', 'player2']]

    def _validation_check(self):
        """Validation for fields."""
        if self.group != self.player1.group:
            raise ValidationError('Group has to be same as group of player1.')
        if self.group != self.player2.group:
            raise ValidationError('Group has to be same as group of player2.')
        try:
            tournament_match = TournamentMatch.objects.get(group = self.group, player1 = self.player2, player2 = self.player1)
        except ObjectDoesNotExist:
            pass
        else:
            raise ValidationError('Players must not face each other more than once when in same group.')

    def save(self, *args, **kwargs):
        """Save object."""
        self._validation_check()
        super().save(*args, **kwargs)
