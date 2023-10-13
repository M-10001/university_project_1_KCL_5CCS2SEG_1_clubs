"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name = 'home'),
    path('sign_up/', views.sign_up, name = 'sign_up'),
    path('log_in/', views.log_in, name = 'log_in'),
    path('log_out/', views.log_out, name = 'log_out'),
    path('user_page/', views.user_page, name = 'user_page'),
    path('create_club/', views.create_club, name = 'create_club'),
    path('membership_sign_up/', views.membership_sign_up, name = 'membership_sign_up'),
    path('club/<int:club_id>/', views.club_page, name = 'club_page'),
    path('members/<int:club_id>/', views.member_list, name = 'member_list'),
    path('member/<int:user_id>/<int:club_id>/', views.show_member, name = 'show_member'),
    path('decline_application/<int:user_id>/<int:club_id>/', views.decline_application, name = 'decline_application'),
    path('set_member/<int:user_id>/<int:club_id>/', views.set_member, name = 'set_member'),
    path('set_officer/<int:user_id>/<int:club_id>/', views.set_officer, name = 'set_officer'),
    path('set_owner/<int:user_id>/<int:club_id>/', views.set_owner, name = 'set_owner'),
    path('application_edit/<int:club_id>/', views.application_edit, name = 'application_edit'),
    path('create_tournament/<int:club_id>/', views.create_tournament, name = 'create_tournament'),
    path('joinable_tournaments/<int:club_id>/', views.joinable_tournaments, name = 'joinable_tournaments'),
    path('tournaments/<int:club_id>/', views.member_tournaments, name = 'member_tournaments'),
    path('participate_in_tournament/<int:club_id>/<int:tournament_id>/', views.participate_in_tournament, name = 'participate_in_tournament'),
    path('tournament/<int:club_id>/<int:tournament_id>/', views.tournament_page, name = 'tournament_page'),
    path('available_officers_for_tournament/<int:club_id>/<int:tournament_id>/', views.available_officers_for_tournament, name = 'available_officers_for_tournament'),
    path('add_co_organiser/<int:club_id>/<int:membership_id>/<int:tournament_id>/', views.add_co_organiser, name = 'add_co_organiser'),
    path('co_organisers/<int:club_id>/<int:tournament_id>/', views.co_organiser_list, name = 'co_organiser_list'),
    path('remove_co_organiser/<int:club_id>/<int:membership_id>/<int:tournament_id>/', views.remove_co_organiser, name = 'remove_co_organiser'),
    path('leave_tournament/<int:club_id>/<int:tournament_id>/', views.leave_tournament, name = 'leave_tournament'),
    path('create_matches/<int:club_id>/<int:tournament_id>/', views.create_matches, name = 'create_matches'),
    path('set_tournament_match/<int:club_id>/<int:tournament_id>/<int:tournament_match_id>/', views.set_tournament_match, name = 'set_tournament_match'),
]
