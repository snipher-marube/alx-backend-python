from datetime import datetime

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