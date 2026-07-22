from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Q
from .forms import UserProfileForm
import json
from django.db.models import Count
from .models import Task, Notification
import requests

def send_sms(api_key, app_id, sender_id, message, phone):
    url = "https://comms.umeskiasoftwares.com/api/v1/sms/send"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "api_key": api_key,
        "app_id": app_id,
        "sender_id": sender_id,
        "message": message,
        "phone": phone
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Landing Page - Redirect to Dashboard
def landing_page(request):
    return render(request, 'task_tracker/landing.html')

# Dashboard View
def dashboard(request):
    user_role = request.session.get("user_role")
    if not user_role:
        return redirect("landing")
    if user_role == "Manager":
        return redirect("manager_dashboard")
    else:
        return redirect("team_dashboard")
    return render(request, "task_tracker/dashboard.html")

# Set User Role (Manager or Team Member)

def set_role(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            role = data.get("role")

            # validate role
            if role not in ["Manager", "Team Member"]:
                return JsonResponse({"success": False, "error": "Invalid role"})

            # store role in session
            request.session["user_role"] = role

            return JsonResponse({
                "success": True,
                "redirect_url": "/login/"
            })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid data format"})

    return JsonResponse({"success": False, "error": "Invalid role selection"})
# Login Page View
def login_page(request):
    if not user_role:
        return render(request, 'task_tracker/landing.html')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if (user_role == "Manager" and user.is_staff) or (user_role == "Team Member" and not user.is_staff):
                login(request, user)
            else:
                messages.error(request, "Invalid role selection for this account.")
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "task_tracker/login.html", {"user_role": user_role})

# Logout User and Redirect to Landing Page
def logout_user(request):
    logout(request)
    request.session.pop("user_role", None)
    return render(request, 'task_tracker/landing.html')

# Manager Dashboard View
@login_required
def manager_dashboard(request):
    tasks = Task.objects.all().order_by('-deadline')
    team_members = User.objects.filter(is_staff=False)
    today = now().date()

    completed_tasks = tasks.filter(status="Completed").count()
    pending_tasks = tasks.exclude(status="Completed").count()
    total_team_members = team_members.count()

    return render(request, "task_tracker/manager_dashboard.html", {
        "tasks": tasks,
        "team_members": team_members,
        "today": today,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "total_team_members": total_team_members
    })

# Team Dashboard - Show Assigned Tasks and Overdue Notifications
@login_required
def team_dashboard(request):
    check_overdue_tasks(request.user)
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'task_tracker/team_dashboard.html', {'tasks': tasks})

# Task Management Views
@login_required
def tasks_view(request):
    return render(request, 'task_tracker/tasks.html')

@login_required
def reports(request):
    return render(request, 'task_tracker/reports.html')

@login_required
def settings_view(request):
    return render(request, 'task_tracker/settings.html')

# Assign Task to Team Member
@login_required
def assign_task(request):
    if request.method == "POST":
        task_name = request.POST.get("task_name")
        assigned_to_id = request.POST.get("assigned_to")
        deadline = request.POST.get("deadline")

        if not task_name or not assigned_to_id or not deadline:
            return HttpResponseBadRequest("Missing required fields")

        try:
            assigned_to = User.objects.get(id=assigned_to_id)
            task = Task.objects.create(name=task_name, assigned_to=assigned_to, deadline=deadline)

            # Send SMS to the assigned team member
            message = f"You have been assigned a new task: {task.name}. Deadline: {task.deadline}"
            api_key = "b3ed71d7ab8953200754854cd2be053f"
            app_id = "UMSC310357"
            sender_id = "UMS_SMS"
            phone = assigned_to.userprofile.phone_number

            response = send_sms(api_key, app_id, sender_id, message, phone)
            print(response)

        except User.DoesNotExist:
            return HttpResponseBadRequest("Invalid Team Member Selected")

    team_members = User.objects.filter(is_staff=False)
    return render(request, "task_tracker/manager_dashboard.html", {"team_members": team_members})

# Mark Task as Complete
@login_required
def mark_task_complete(request, task_id):
    task = Task.objects.get(id=task_id)
    task.status = "Completed"
    task.save()

# Update Task Status
@login_required
def update_task_status(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        new_status = request.POST.get("new_status")

        try:
            task = Task.objects.get(id=task_id, assigned_to=request.user)
            task.status = new_status
            task.save()
            return JsonResponse({"success": True})
        except Task.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})

# View Notifications
@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "partials/notifications_list.html", {"notifications": notifications})

# Mark Notifications as Read
@login_required
def mark_notifications_as_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Check Overdue Tasks and Send Notifications
def check_overdue_tasks(user):
    """Checks if a user's tasks are overdue or nearing their deadline and sends notifications."""
    overdue_tasks = Task.objects.filter(
        Q(status="Pending") | Q(status="In Progress"),
        assigned_to=user
    )

    today_datetime = now()  # Get the current datetime
    today_date = today_datetime.date()  # Convert to date object

    for task in overdue_tasks:
        task_deadline_date = task.deadline.date() if isinstance(task.deadline, datetime) else task.deadline

        # Check if the task is nearing its deadline (1 day before)
        if (task_deadline_date - today_date).days == 1:
            if not Notification.objects.filter(user=user, task=task, message=f"Your task '{task.name}' is nearing its deadline!").exists():
                Notification.objects.create(
                    user=user,
                    message=f"Your task '{task.name}' is nearing its deadline!",
                    task=task  # Assuming you have a task field in Notification model
                )
                message = f"Your task '{task.name}' is nearing its deadline!"
                phone = user.userprofile.phone_number
                api_key = "b3ed71d7ab8953200754854cd2be053f"
                app_id = "UMSC310357"
                sender_id = "UMS_SMS"
                send_sms(api_key, app_id, sender_id, message, phone)

        # Check if the task is overdue
        elif task_deadline_date < today_date:
            if not Notification.objects.filter(user=user, task=task, message=f"Your task '{task.name}' is overdue!").exists():
                Notification.objects.create(
                    user=user,
                    message=f"Your task '{task.name}' is overdue!",
                    task=task
                )
                message = f"Your task '{task.name}' is overdue!"
                phone = user.userprofile.phone_number
                api_key = "b3ed71d7ab8953200754854cd2be053f"
                app_id = "UMSC310357"
                sender_id = "UMS_SMS"
                send_sms(api_key, app_id, sender_id, message, phone)

@login_required
def update_phone_number(request):
    profile = request.user.userprofile  # Get the logged-in user's profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)  # Initialize the form with current data
        if form.is_valid():
            form.save()  # Save the updated profile
            return redirect('profile')  # Redirect to the user profile page (or another page if preferred)
    else:
        form = UserProfileForm(instance=profile)  # Initialize form with profile data for GET request

    return render(request, 'task_tracker/update_phone_number.html', {'form': form})  # Form rendering

# User Profile View (Show and Edit Profile)
@login_required
def user_profile(request):
    profile = request.user.userprofile  # Get the current user's profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)  # Initialize the form with current profile data
        if form.is_valid():
            form.save()  # Save the form (i.e., update the profile)
            return redirect('user_profile')  # Redirect back to the profile page after saving
    else:
        form = UserProfileForm(instance=profile)  # Initialize the form for GET requests with existing data
    
    return render(request, 'task_tracker/user_profile.html', {'form': form, 'profile': profile})  # Render the form with profile data

@login_required
def reports_data_api(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    queryset = Task.objects.all()

    if start_date and end_date:
        queryset = queryset.filter(deadline__range=[start_date, end_date])

    task_status_data = queryset.values('status').annotate(count=Count('id'))
    team_performance_data = queryset.values('assigned_to__username').annotate(count=Count('id'))
    overdue_data = queryset.filter(deadline__lt=now(), status__in=['Pending', 'In Progress'])

    return JsonResponse({
        'task_status': list(task_status_data),
        'team_performance': list(team_performance_data),
        'overdue_tasks': overdue_data.count(),
    })
