from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.utils import timezone
from core.models import Book, BookLoan, Student
from .serializers import BookSerializer, BookLoanSerializer, StudentSerializer, BookLoanCreateSerializer

def admin_vue_app(request):
    """
    Serve the Vue.js admin interface in place of Django admin
    """
    return render(request, 'admin/vue_admin.html')

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.AllowAny]  # Para desenvolvimento

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Para desenvolvimento
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available books"""
        available_books = Book.objects.filter(available_copies__gt=0)
        serializer = self.get_serializer(available_books, many=True)
        return Response(serializer.data)

class BookLoanViewSet(viewsets.ModelViewSet):
    queryset = BookLoan.objects.all()
    serializer_class = BookLoanSerializer
    permission_classes = [permissions.AllowAny]  # Para desenvolvimento
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookLoanCreateSerializer
        return BookLoanSerializer
    
    def get_queryset(self):
        queryset = BookLoan.objects.all().select_related('book', 'student')
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Mark a book loan as returned"""
        loan = self.get_object()
        if loan.status == BookLoan.LoanStatus.RETURNED:
            return Response(
                {'error': 'Book already returned'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = BookLoan.LoanStatus.RETURNED
        loan.return_date = timezone.now().date()
        loan.save()
        
        # Increase available copies
        book = loan.book
        book.available_copies += 1
        book.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get loan statistics"""
        total_loans = BookLoan.objects.count()
        active_loans = BookLoan.objects.filter(status=BookLoan.LoanStatus.ACTIVE).count()
        overdue_loans = BookLoan.objects.filter(status=BookLoan.LoanStatus.OVERDUE).count()
        
        return Response({
            'totalLoans': total_loans,
            'activeLoans': active_loans,
            'overdueLoans': overdue_loans,
        })
