from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import StudyGroup, Resource, Message, StudySession
from .forms import StudyGroupForm, ResourceForm, MessageForm, StudySessionForm
from django.utils import timezone
from datetime import datetime
from django.conf import settings

def home(request):
    """Home page with featured study groups"""
    featured_groups = StudyGroup.objects.filter(is_private=False).annotate(
        member_count=Count('members')
    )[:6]
    return render(request, 'groups/home.html', {'featured_groups': featured_groups})

@login_required
def dashboard(request):
    """User dashboard showing their groups"""
    my_groups = request.user.joined_groups.all()
    created_groups = request.user.created_groups.all()
    return render(request, 'groups/dashboard.html', {
        'my_groups': my_groups,
        'created_groups': created_groups
    })

def browse_groups(request):
    """Browse all public study groups"""
    query = request.GET.get('q', '')
    subject = request.GET.get('subject', '')
    
    groups = StudyGroup.objects.filter(is_private=False).annotate(
        member_count=Count('members')
    )
    
    if query:
        groups = groups.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(subject__icontains=query)
        )
    
    if subject:
        groups = groups.filter(subject__icontains=subject)
    
    subjects = StudyGroup.objects.values_list('subject', flat=True).distinct()
    
    return render(request, 'groups/browse.html', {
        'groups': groups,
        'subjects': subjects,
        'query': query,
        'selected_subject': subject
    })

@login_required
def create_group(request):
    """Create a new study group"""
    if request.method == 'POST':
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, 'Study group created successfully!')
            return redirect('group_detail', pk=group.pk)
    else:
        form = StudyGroupForm()
    return render(request, 'groups/create_group.html', {'form': form})

@login_required
def group_detail(request, pk):
    """Study group detail page"""
    group = get_object_or_404(StudyGroup, pk=pk)
    is_member = request.user in group.members.all()
    
    if not is_member and group.is_private:
        messages.error(request, 'This is a private group.')
        return redirect('browse_groups')
    
    resources = group.resources.all()
    # Fetch initial 50 messages for the first load
    chat_messages = group.messages.all().order_by('sent_at')[:50] 
    upcoming_sessions = group.sessions.filter(scheduled_time__gte=timezone.now())
    
    message_form = MessageForm()
    resource_form = ResourceForm()
    session_form = StudySessionForm()
    
    return render(request, 'groups/group_detail.html', {
        'group': group,
        'is_member': is_member,
        'resources': resources,
        'messages': chat_messages,
        'upcoming_sessions': upcoming_sessions,
        'message_form': message_form,
        'resource_form': resource_form,
        'session_form': session_form,
    })

@login_required
def join_group(request, pk):
    """Join a study group"""
    group = get_object_or_404(StudyGroup, pk=pk)
    
    if group.members.count() >= group.max_members:
        messages.error(request, 'This group is full.')
    elif request.user in group.members.all():
        messages.info(request, 'You are already a member.')
    else:
        group.members.add(request.user)
        messages.success(request, f'You joined {group.name}!')
    
    return redirect('group_detail', pk=pk)

@login_required
def leave_group(request, pk):
    """Leave a study group"""
    group = get_object_or_404(StudyGroup, pk=pk)
    
    if request.user == group.created_by:
        messages.error(request, 'Group creator cannot leave. Delete the group instead.')
    elif request.user not in group.members.all():
        messages.error(request, 'You are not a member.')
    else:
        group.members.remove(request.user)
        messages.success(request, f'You left {group.name}.')
        return redirect('dashboard')
    
    return redirect('group_detail', pk=pk)

@login_required
def add_resource(request, pk):
    """Add a resource to a study group"""
    group = get_object_or_404(StudyGroup, pk=pk)
    
    if request.user not in group.members.all():
        messages.error(request, 'You must be a member to add resources.')
        return redirect('group_detail', pk=pk)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.study_group = group
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource added successfully!')
    
    return redirect('group_detail', pk=pk)

@login_required
def send_message(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    if request.user not in group.members.all():
        return JsonResponse({'error': 'Not a member'}, status=403)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            msg = Message.objects.create(
                study_group=group,
                sender=request.user,
                content=content
            )
            # Use standardized JSON format for consistency with get_messages
            return JsonResponse({
                'success': True,
                'message': {
                    'sender': msg.sender.username,
                    'content': msg.content,
                    # Localized time for display
                    'sent_at_display': timezone.localtime(msg.sent_at).strftime("%I:%M %p"),
                    # ISO format for subsequent requests
                    'sent_at_iso': msg.sent_at.isoformat(),
                    'is_own_message': True # It's always the user's own message when sending
                }
            })

    return JsonResponse({'error': 'Invalid'}, status=400)


@login_required
def get_messages(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    if request.user not in group.members.all():
        return JsonResponse({'error': 'Not a member'}, status=403)

    last_message_time_str = request.GET.get('last_message_time')
    
    messages_query = group.messages.all()
    
    if last_message_time_str:
        try:
            # Filter messages sent after the client's last message time
            messages_query = messages_query.filter(sent_at__gt=last_message_time_str)
        except ValueError:
            # If parsing fails, proceed without filtering (shouldn't happen with ISO format)
            pass
            
    # Always order by time and limit to a reasonable number
    messages_query = messages_query.order_by("sent_at")[:50] 

    data = [{
        "sender": msg.sender.username,
        "content": msg.content,
        "sent_at_display": timezone.localtime(msg.sent_at).strftime("%I:%M %p"),
        "sent_at_iso": msg.sent_at.isoformat(),
        "is_own_message": msg.sender == request.user 
    } for msg in messages_query]

    return JsonResponse({"messages": data})


@login_required
def add_session(request, pk):
    """Add a study session to the calendar"""
    group = get_object_or_404(StudyGroup, pk=pk)
    
    if request.user not in group.members.all():
        messages.error(request, 'You must be a member to schedule sessions.')
        return redirect('group_detail', pk=pk)
    
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.study_group = group
            session.created_by = request.user
            session.save()
            messages.success(request, 'Study session scheduled!')
    
    return redirect('group_detail', pk=pk)