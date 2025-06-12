from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import logout

User = get_user_model()

@login_required
@require_POST
def delete_user(request):
    """
    View to handle user account deletion with confirmation.
    """
    if request.method == 'POST':
        user = request.user
        logout(request)  # Logout before deletion to avoid issues
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')  # Replace 'home' with your actual home URL name