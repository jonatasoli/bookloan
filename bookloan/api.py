"""
Django REST Framework Configuration for BookLoan API
"""

from datetime import timedelta

# Django REST Framework Settings
REST_FRAMEWORK = {
    # Default authentication classes
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # For browsable API
    ],
    
    # Default permission classes
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Rendering
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # For development
    ],
    
    # Throttling (rate limiting)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    
    # Exception handling
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # Date/Time formatting
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
}

# CORS Settings (for Vue.js frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Vue dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Alternative Vue dev server
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# API Documentation Settings (if using drf-spectacular)
SPECTACULAR_SETTINGS = {
    'TITLE': 'BookLoan Management API',
    'DESCRIPTION': 'API for managing library book loans',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# Custom pagination classes
CUSTOM_PAGINATION = {
    'BOOK_LOANS_PAGE_SIZE': 25,
    'BOOKS_PAGE_SIZE': 50,
    'MAX_PAGE_SIZE': 100,
}

# API Rate Limiting Settings
API_THROTTLING = {
    'BURST_RATE': '60/min',
    'SUSTAINED_RATE': '1000/hour',
    'ADMIN_RATE': '5000/hour',
}

# Token Authentication Settings
TOKEN_AUTH = {
    'TOKEN_TTL': timedelta(days=30),  # Token expires after 30 days
    'AUTO_REFRESH': True,
    'REFRESH_THRESHOLD': timedelta(days=7),  # Refresh if less than 7 days left
}

# API Response Formats
API_RESPONSE_FORMATS = {
    'SUCCESS_FORMAT': {
        'success': True,
        'data': None,
        'message': None,
    },
    'ERROR_FORMAT': {
        'success': False,
        'error': None,
        'message': None,
        'details': None,
    }
}

# File Upload Settings for API
API_FILE_UPLOAD = {
    'MAX_UPLOAD_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_EXTENSIONS': ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
}

# Logging for API
API_LOGGING = {
    'LOG_REQUESTS': True,
    'LOG_RESPONSES': True,
    'LOG_ERRORS': True,
    'LOG_PERFORMANCE': True,
}

# Cache settings for API
API_CACHE = {
    'DEFAULT_TIMEOUT': 300,  # 5 minutes
    'STATISTICS_TIMEOUT': 900,  # 15 minutes
    'BOOK_LIST_TIMEOUT': 3600,  # 1 hour
}

# Search configuration
API_SEARCH = {
    'MIN_SEARCH_LENGTH': 2,
    'MAX_SEARCH_RESULTS': 100,
    'SEARCH_FIELDS': {
        'books': ['title', 'author', 'isbn'],
        'loans': ['user__username', 'user__first_name', 'user__last_name', 'book__title'],
        'users': ['username', 'first_name', 'last_name', 'email'],
    }
}
