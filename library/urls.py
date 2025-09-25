from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import BookLoanViewSet, BookViewSet, DashboardStatsView

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'book-loans', BookLoanViewSet, basename='bookloan')
router.register(r'books', BookViewSet, basename='book')

app_name = 'api'

urlpatterns = [
    # API Authentication
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Dashboard stats
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    
    # Loan statistics (for compatibility with Vue component)
    path('loan-statistics/', BookLoanViewSet.as_view({'get': 'statistics'}), name='loan_statistics'),
    
    # ViewSet routes (includes all CRUD + custom actions)
    path('', include(router.urls)),
]

"""
API Endpoints Available:

Authentication:
- POST /api/auth/token/ - Get auth token

Dashboard:
- GET /api/dashboard/stats/ - Get dashboard statistics

Book Loans:
- GET /api/book-loans/ - List all loans (with filtering/search)
- POST /api/book-loans/ - Create new loan
- GET /api/book-loans/{id}/ - Get specific loan
- PUT /api/book-loans/{id}/ - Update loan (full)
- PATCH /api/book-loans/{id}/ - Update loan (partial)
- DELETE /api/book-loans/{id}/ - Delete loan

Book Loan Actions:
- GET /api/book-loans/overdue/ - Get overdue loans
- GET /api/book-loans/statistics/ - Get loan statistics
- GET /api/book-loans/user_loans/?user_id=X - Get loans for specific user
- POST /api/book-loans/{id}/return_book/ - Mark book as returned
- POST /api/book-loans/{id}/renew_loan/ - Renew loan (extend due date)

Books:
- GET /api/books/ - List all books (read-only)
- GET /api/books/{id}/ - Get specific book
- GET /api/books/available/ - Get available books

Query Parameters for Filtering:
- status: Filter by loan status (borrowed, returned)
- user: Filter by user ID
- user__username: Filter by username
- search: Search in user names, book titles, authors, notes
- ordering: Order by loan_date, due_date, return_date, created_at

Examples:
- GET /api/book-loans/?status=borrowed - Get active loans
- GET /api/book-loans/?search=Harry Potter - Search loans
- GET /api/book-loans/?ordering=-due_date - Order by due date (newest first)
- GET /api/book-loans/?user__username=john - Get loans for user 'john'
"""
