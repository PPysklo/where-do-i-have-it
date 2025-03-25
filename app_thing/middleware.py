import threading

thread = threading.local()


class OwnerMiddleware:
    """
    Middleware to store the current user in thread-local storage.
    This allows the current user to be accessed globally within the application.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the given response function.

        Args:
            get_response: The next middleware or view to be called.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and store the current user in thread-local storage.

        Args:
            request: The HTTP request object.

        Returns:
            The HTTP response object.
        """
        # Store the current user in thread-local storage
        thread.user = request.user
        
        # Call the next middleware or view
        response = self.get_response(request)
        
        return response
