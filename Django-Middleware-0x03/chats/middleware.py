from datetime import datetime, time, timedelta
from collections import defaultdict
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
    
class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store IP addresses and their request timestamps
        self.ip_tracker = defaultdict(list)
        self.RATE_LIMIT = 5  # 5 messages
        self.TIME_WINDOW = 60  # 60 seconds (1 minute)

    def __call__(self, request):
        # Only process POST requests to chat endpoints
        if request.method == 'POST' and ('/chat/' in request.path or '/message/' in request.path):
            ip_address = self.get_client_ip(request)
            current_time = datetime.now()

            # Clean up old requests from the tracker
            self.cleanup_old_requests(current_time)

            # Check if IP has exceeded rate limit
            if self.is_rate_limited(ip_address, current_time):
                return HttpResponseForbidden(
                    "Rate limit exceeded: Maximum 5 messages per minute. Please wait."
                )

            # Track this request
            self.ip_tracker[ip_address].append(current_time)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get the client's IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def cleanup_old_requests(self, current_time):
        """Remove timestamps older than our time window"""
        cutoff_time = current_time - timedelta(seconds=self.TIME_WINDOW)
        for ip in list(self.ip_tracker.keys()):
            # Filter out old timestamps
            self.ip_tracker[ip] = [
                t for t in self.ip_tracker[ip] 
                if t > cutoff_time
            ]
            # Remove IP if no recent requests
            if not self.ip_tracker[ip]:
                del self.ip_tracker[ip]

    def is_rate_limited(self, ip_address, current_time):
        """Check if IP has exceeded rate limit"""
        requests_in_window = [
            t for t in self.ip_tracker.get(ip_address, []) 
            if t > current_time - timedelta(seconds=self.TIME_WINDOW)
        ]
        return len(requests_in_window) >= self.RATE_LIMIT


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define protected paths and required roles
        self.PROTECTED_PATHS = {
            '/admin/': ['admin'],
            '/moderate/': ['admin', 'moderator'],
            '/delete/': ['admin'],
        }

    def __call__(self, request):
        current_path = request.path
        
        # Check if current path is protected
        for protected_path, required_roles in self.PROTECTED_PATHS.items():
            if current_path.startswith(protected_path):
                if not request.user.is_authenticated:
                    return HttpResponseForbidden("Authentication required")
                
                if not self.has_required_role(request.user, required_roles):
                    return HttpResponseForbidden(
                        f"Access denied. Requires {', '.join(required_roles)} role"
                    )
                break

        return self.get_response(request)

    def has_required_role(self, user, required_roles):
        """Check if user has any of the required roles"""
        # Implementation for different role systems:
        
        # 1. For Django's built-in admin/staff:
        if 'admin' in required_roles and user.is_superuser:
            return True
        
        # 2. For custom role fields (adjust as needed):
        if hasattr(user, 'role') and user.role in required_roles:
            return True
            
       
            
        return False