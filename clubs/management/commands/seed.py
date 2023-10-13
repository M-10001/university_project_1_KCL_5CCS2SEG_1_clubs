from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from faker import Faker
import random
from clubs.models import User, Club, Membership

class Command(BaseCommand):
    """The database seeder."""

    PASSWORD = "Password123"
    APPLICANT_COUNT_PER_CLUB = 5
    CLUB_COUNT = 6
    MEMBER_COUNT_PER_CLUB = 20
    OFFICER_COUNT_PER_CLUB = 5

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_specific_clubs()
        self.create_user_Jebediah_and_memberships()
        self.create_user_Valentina_and_memberships()
        self.create_user_Billie_and_memberships()
        print()
        self.seed_clubs()
        print()
        self.club_list = list(Club.objects.all())
        for club in self.club_list:
            print()
            print(f'Seeding {club.name} Users')
            self.seed_owner(club = club)
            print()
            self.seed_applicants(club = club)
            print()
            self.seed_members(club = club)
            print()
            self.seed_officers(club = club)
            print()

        print()
        print('User and Clubs seeding complete.')

    def _create_applicant(self, club):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name,last_name)
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        member_type = Membership.MemberTypes.APPLICANT
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = club,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = member_type
        )

    def _create_club(self):
        name = self.faker.first_name()
        Club.objects.create(
            name = self._club_name(name),
            location = self.faker.address(),
            description = self.faker.text(max_nb_chars=500)
        )

    def _create_owner(self,club):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name,last_name)
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        member_type = Membership.MemberTypes.CLUB_OWNER
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = club,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = member_type
        )

    def _create_member(self,club):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name,last_name)
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        member_type = Membership.MemberTypes.MEMBER
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = club,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = member_type
        )

    def _create_officer(self,club):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name,last_name)
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        member_type = Membership.MemberTypes.OFFICER
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = club,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = member_type
        )

    def create_specific_applicant(self):
        first_name = "Yoyo"
        last_name = "Ma"
        email = "yoyo@example.org"
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = self.club_Kerbal,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = Membership.MemberTypes.APPLICANT
        )

    def create_user_Jebediah_and_memberships(self):
        first_name = "Jebediah"
        last_name = "Kerman"
        email = "jeb@example.org"
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = self.club_Kerbal,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = Membership.MemberTypes.MEMBER
        )
        Membership.objects.create(
            club = self.club_Alpha,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = Membership.MemberTypes.OFFICER
        )


    def create_user_Valentina_and_memberships(self):
        first_name = "Valentina"
        last_name = "Kerman"
        email = "val@example.org"
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = self.club_Kerbal,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = Membership.MemberTypes.MEMBER
        )
        Membership.objects.create(
            club = self.club_Beta,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = Membership.MemberTypes.CLUB_OWNER
        )

    def create_user_Billie_and_memberships(self):
        first_name = "Billie"
        last_name = "Kerman"
        email = "billie@example.org"
        contact_details = self._contact_details()
        chess_experience_level = random.randint(0,3)
        personal_statement = self.faker.text(max_nb_chars=200)
        bio = self.faker.text(max_nb_chars=500)
        user = User.objects.create_user(
            email=email,
            password=Command.PASSWORD
        )
        Membership.objects.create(
            club = self.club_Kerbal,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = Membership.MemberTypes.MEMBER
        )
        Membership.objects.create(
            club = self.club_Omega,
            member = user,
            member_first_name = first_name,
            member_last_name = last_name,
            member_contact_details = contact_details,
            member_personal_statement = personal_statement,
            member_bio = bio,
            member_chess_experience_level = chess_experience_level,
            member_type = Membership.MemberTypes.MEMBER
        )

    def create_specific_clubs(self):
        self.club_Kerbal = Club.objects.create(
            name = "Kerbal Chess Club",
            location = self.faker.address(),
            description = self.faker.text(max_nb_chars=500)
        )
        self.club_Alpha = Club.objects.create(
            name = "Alpha Chess Club",
            location = self.faker.address(),
            description = self.faker.text(max_nb_chars=500)
        )
        self.club_Beta = Club.objects.create(
            name = "Beta Chess Club",
            location = self.faker.address(),
            description = self.faker.text(max_nb_chars=500)
        )
        self.club_Omega = Club.objects.create(
            name = "Omega Chess Club",
            location = self.faker.address(),
            description = self.faker.text(max_nb_chars=500)
        )

    def _contact_details(self):
        return f'+44 {self.faker.msisdn()[3:]}'

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _club_name(self, name):
        name = f'{name} Chess Club'
        return name

    def seed_clubs(self):
        club_count = Club.objects.all().count()
        seed_try = club_count
        print(f'Clubs seeded: {club_count}',  end='\r')
        while seed_try < Command.CLUB_COUNT:
            try:
                club = self._create_club()
                club_count += 1
                print(f'Clubs seeded: {club_count}',  end='\r')
            except (IntegrityError):
                continue
            seed_try += 1

    def seed_applicants(self,club):
        member_type = Membership.MemberTypes.APPLICANT
        applicant_count = Membership.objects.filter(club = club, member_type = member_type).count()
        seed_try = applicant_count
        print(f'{club.name} Applicants seeded: {applicant_count}',  end='\r')
        while seed_try < Command.APPLICANT_COUNT_PER_CLUB:
            try:
                self._create_applicant(club)
                applicant_count += 1
                print(f'{club.name} Applicants seeded: {applicant_count}',  end='\r')
            except (IntegrityError):
                continue
            seed_try += 1

    def seed_officers(self,club):
        member_type = Membership.MemberTypes.OFFICER
        officer_count = Membership.objects.filter(club = club, member_type = member_type).count()
        seed_try = officer_count
        print(f'{club.name} Officers seeded: {officer_count}',  end='\r')
        while seed_try < Command.OFFICER_COUNT_PER_CLUB:
            try:
                self._create_officer(club)
                officer_count += 1
                print(f'{club.name} Officers seeded: {officer_count}',  end='\r')
            except (IntegrityError):
                continue
            seed_try += 1

    def seed_members(self,club):
        member_type = Membership.MemberTypes.MEMBER
        member_count = Membership.objects.filter(club = club, member_type = member_type).count()
        seed_try = member_count
        print(f'{club.name} Members seeded: {member_count}',  end='\r')
        while seed_try < Command.MEMBER_COUNT_PER_CLUB:
            try:
                self._create_member(club)
                member_count += 1
                print(f'{club.name} Members seeded: {member_count}',  end='\r')
            except (IntegrityError):
                continue
            seed_try += 1

    def seed_owner(self,club):
        member_type = Membership.MemberTypes.CLUB_OWNER
        owner_count = Membership.objects.filter(club = club, member_type = member_type).count()
        seed_try = owner_count
        print(f'{club.name} Owner seeded: {owner_count}',  end='\r')
        while seed_try < 1:
            try:
                self._create_owner(club)
                owner_count += 1
                print(f'{club.name} Owner seeded: {owner_count}',  end='\r')
            except (IntegrityError):
                continue
            seed_try += 1
