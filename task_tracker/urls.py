from django.urls import path
from . import views  # ✅ Avoids circular import

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('team_dashboard/', views.team_dashboard, name='team_dashboard'),

    # Tasks
    path('tasks/', views.tasks_view, name='tasks'),
    path('assign_task/', views.assign_task, name='assign_task'),
    path('mark_task_complete/<int:task_id>/', views.mark_task_complete, name='mark_task_complete'),
    path("update-task-status/", views.update_task_status, name="update_task_status"),

    # Reports & Settings
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings_view, name='settings'),

    # Notifications
    path("notifications/", views.notifications, name="notifications"),
    path("mark_notifications_as_read/", views.mark_notifications_as_read, name="mark_notifications_as_read"),

    # Role Management
    path('set_role/', views.set_role, name='set_role'),
    path('user-profile/', views.user_profile, name='user_profile'),
      path('reports/', views.reports, name='reports'),
    path('api/reports/data/', views.reports_data_api, name='reports_data_api'),
]
