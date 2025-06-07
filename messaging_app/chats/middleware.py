from datetime import datetime, time
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get the user information
        user = "Anonymous"
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username
        
        # Log the request information
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        
        # Write to the log file
        with open("requests.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Process the request
        response = self.get_response(request)
        
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Define restricted hours (9 PM to 6 AM)
        current_time = time.fromisoformat(time.now().time().isoformat())
        start_time = time(21, 0)  # 9 PM
        end_time = time(6, 0)    # 6 AM
        
        # Check if current time is within restricted hours
        if (current_time >= start_time) or (current_time <= end_time):
            # Check if the request is for a chat-related path
            if request.path.startswith('/chat/') or request.path.startswith('/messaging/'):
                return HttpResponseForbidden(
                    "Messaging is unavailable between 9 PM and 6 AM. Please try again later."
                )
        
        # If not restricted time or not chat path, process normally
        response = self.get_response(request)
        return response