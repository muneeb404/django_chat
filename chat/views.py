from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatRoom


def home(request):
    username = request.session.get('username', '')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if not is_valid_username(username):
            return render(request, 'chat/home.html', {
                'rooms': ChatRoom.objects.all(),
                'error': 'Username must be 1-50 characters and contain only letters, numbers, spaces, underscores, or hyphens.',
                'username': username,
            })
        request.session['username'] = username
        if request.POST.get('action') == 'join':
            return redirect('room', slug=request.POST.get('slug', ''))

        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Room name is required.')
        elif len(name) > 100:
            messages.error(request, 'Room name must be 100 characters or fewer.')
        elif ChatRoom.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A room with that name already exists.')
        else:
            room = ChatRoom.objects.create(name=name)
            return redirect(room)
    return render(request, 'chat/home.html', {'rooms': ChatRoom.objects.all(), 'username': username})


def room(request, slug):
    if not request.session.get('username'):
        return redirect('home')
    chat_room = get_object_or_404(ChatRoom, slug=slug)
    return render(request, 'chat/room.html', {
        'room': chat_room,
        'username': request.session.get('username', ''),
        'room_messages': chat_room.messages.all(),
    })


def is_valid_username(username):
    return (
        1 <= len(username) <= 50
        and all(character.isalnum() or character in ' _-' for character in username)
    )
