from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Group, Message


def home(request):
	groups = Group.objects.all()
	return render(request, 'home.html', {'groups':groups})


@login_required
def new_group(request):
	user = request.user
	new_group = Group.objects.create()
	new_group.members.add(user)
	new_group.save()
	Message.objects.create(author=user, group=new_group, content=f"User '{user.username}' created the room.")
	return redirect('home')


@login_required
def join_group(request, uuid):
	user = request.user
	group = Group.objects.get(uuid=uuid)
	group.members.add(user)
	group.save()
	Message.objects.create(author=user, group=group, content=f"User '{user.username}' joined the room.")
	return redirect('home')


@login_required
def leave_group(request, uuid):
	user = request.user
	group = Group.objects.get(uuid=uuid)
	group.members.remove(user)
	group.save()
	Message.objects.create(author=user, group=group, content=f"User '{user.username}' left the room.")
	return redirect('home')


@login_required
def open_chat(request, uuid):
	group = Group.objects.get(uuid=uuid)
	if request.user not in group.members.all():
		return HttpResponseForbidden('Not a member. Try another group.')
	messages = group.message_set.all()
	sorted_messages = sorted(messages, key=lambda x: x.timestamp)
	return render(request, 'chat.html', context={'messages':sorted_messages, 'uuid': uuid})


@login_required
def remove_group(request, uuid):
	u = request.user
	Group.objects.get(uuid=uuid).delete()
	return redirect('home')
