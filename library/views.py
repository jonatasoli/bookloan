from django.utils import timezone
from django.db.models import Q, F
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta

from core.models import BookLoan, Book
from .serializers import (
    BookLoanSerializer, 
    BookLoanCreateSerializer, 
    BookSerializer, 
    UserSerializer
)


class BookLoanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing BookLoan entries
    Provides CRUD operations and additional features
    """
    serializer_class = BookLoanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filter options
    filterset_fields = ['status', 'user', 'book', 'user__username']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 
                    'book__title', 'book__author', 'notes']
    ordering_fields = ['loan_date', 'due_date', 'return_date', 'created_at']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        """Optimized queryset with related fields"""
        queryset = BookLoan.objects.select_related('user', 'book').all()
        
        # Add calculated field for overdue days
        today = timezone.now().date()
        queryset = queryset.extra(
            select={
                'days_overdue': f"""
                    CASE 
                        WHEN status = 'borrowed' AND due_date < '{today}' 
                        THEN (JULIANDAY('{today}') - JULIANDAY(due_date))
                        ELSE 0 
                    END
                """
            }
        )
        
        return queryset

    def get_serializer_class(self):
        """Use different serializer for create action"""
        if self.action == 'create':
            return BookLoanCreateSerializer
        return BookLoanSerializer

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue loans"""
        today = timezone.now().date()
        overdue_loans = self.get_queryset().filter(
            status='active',
            due_date__lt=today
        )
        
        serializer = self.get_serializer(overdue_loans, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get loan statistics"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        stats = {
            'totalLoans': queryset.count(),
            'activeLoans': queryset.filter(status='active').count(),
            'overdueLoans': queryset.filter(
                status='active',
                due_date__lt=today
            ).count(),
        }
        
        return Response(stats)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Mark a book as returned"""
        loan = self.get_object()
        
        if loan.status != 'active':
            return Response(
                {'error': 'This book is not currently on loan'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = 'returned'
        loan.return_date = timezone.now().date()
        loan.save()
        
        # Increase book availability
        loan.book.available_copies += 1
        loan.book.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def renew_loan(self, request, pk=None):
        """Renew a loan (extend due date)"""
        loan = self.get_object()
        
        if loan.status != 'active':
            return Response(
                {'error': 'Only active loans can be renewed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extend due date by 2 weeks
        loan.due_date = loan.due_date + timedelta(days=14)
        loan.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_loans(self, request):
        """Get loans for a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_loans = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(user_loans, many=True)
        return Response(serializer.data)


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Books (read-only for loan management)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'author', 'isbn']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get books available for loan"""
        available_books = self.queryset.filter(available_copies__gt=0)
        serializer = self.get_serializer(available_books, many=True)
        return Response(serializer.data)


# Additional API Views for dashboard data
from rest_framework.views import APIView
from django.contrib.auth.models import User


class DashboardStatsView(APIView):
    """
    Dashboard statistics view
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        this_month = today.replace(day=1)
        
        # Basic counts
        total_books = Book.objects.count()
        total_users = User.objects.filter(is_active=True).count()
        total_loans = BookLoan.objects.count()
        active_loans = BookLoan.objects.filter(status='active').count()
        
        # Overdue loans
        overdue_loans = BookLoan.objects.filter(
            status='active',
            due_date__lt=today
        ).count()
        
        # Recent activity
        recent_loans = BookLoan.objects.filter(
            loan_date__gte=this_month
        ).count()
        
        # Top borrowed books this month
        top_books = Book.objects.filter(
            bookloan__loan_date__gte=this_month
        ).annotate(
            loan_count=Count('bookloan')
        ).order_by('-loan_count')[:5]
        
        # Most active users this month
        top_users = User.objects.filter(
            bookloan__loan_date__gte=this_month
        ).annotate(
            loan_count=Count('bookloan')
        ).order_by('-loan_count')[:5]
        
        stats = {
            'totals': {
                'books': total_books,
                'users': total_users,
                'loans': total_loans,
                'active_loans': active_loans,
                'overdue_loans': overdue_loans,
            },
            'this_month': {
                'new_loans': recent_loans,
            },
            'top_books': [
                {
                    'title': book.title,
                    'author': book.author,
                    'loan_count': book.loan_count
                } for book in top_books
            ],
            'top_users': [
                {
                    'username': user.username,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'loan_count': user.loan_count
                } for user in top_users
            ]
        }
        
        return Response(stats)


# Import Count for the stats view
from django.db.models import Count
