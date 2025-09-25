from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Book(models.Model):
    """Book model for the library system"""
    title = models.CharField(max_length=200, verbose_name="Title")
    author = models.CharField(max_length=100, verbose_name="Author")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    total_copies = models.PositiveIntegerField(default=1, verbose_name="Total Copies")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Available Copies")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ['title', 'author']

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def is_available(self):
        """Check if book has available copies"""
        return self.available_copies > 0

    def loan_count(self):
        """Get total number of times this book has been loaned"""
        return self.bookloan_set.count()


class BookLoan(models.Model):
    """BookLoan model representing a book loan transaction"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    # Core fields
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE,
        verbose_name="Book"
    )
    
    # Date fields
    loan_date = models.DateField(
        default=timezone.now,
        verbose_name="Loan Date"
    )
    due_date = models.DateField(
        verbose_name="Due Date",
        help_text="Date when the book should be returned"
    )
    return_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Return Date"
    )
    
    # Status and additional info
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Additional notes about this loan"
    )
    fine_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        verbose_name="Fine Amount"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Book Loan"
        verbose_name_plural = "Book Loans"
        ordering = ['-created_at']
        # Prevent user from having multiple active loans of the same book
        unique_together = [['user', 'book', 'status']]

    def __str__(self):
        return f"{self.book.title} loaned to {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        """Override save to set default due date and handle status changes"""
        # Set default due date to 2 weeks from loan date if not provided
        if not self.due_date and self.loan_date:
            if isinstance(self.loan_date, str):
                from django.utils.dateparse import parse_date
                loan_date = parse_date(self.loan_date)
            else:
                loan_date = self.loan_date
            self.due_date = loan_date + timedelta(days=14)
        
        # Auto-set return date when status changes to returned
        if self.status == 'returned' and not self.return_date:
            self.return_date = timezone.now().date()
        
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if the loan is overdue"""
        if self.status != 'active':
            return False
        return timezone.now().date() > self.due_date

    @property
    def days_overdue(self):
        """Calculate how many days overdue the loan is"""
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days

    @property
    def loan_duration(self):
        """Calculate loan duration in days"""
        if self.return_date:
            return (self.return_date - self.loan_date).days
        return (timezone.now().date() - self.loan_date).days

    def calculate_fine(self, daily_rate=0.50):
        """Calculate fine for overdue books"""
        if self.is_overdue:
            return self.days_overdue * daily_rate
        return 0.00

    def extend_due_date(self, days=14):
        """Extend the due date by specified days (default 14)"""
        self.due_date = self.due_date + timedelta(days=days)
        self.save()

    def mark_returned(self):
        """Mark the book as returned and update availability"""
        self.status = 'returned'
        self.return_date = timezone.now().date()
        self.save()
        
        # Increase book availability
        self.book.available_copies += 1
        self.book.save()

    @classmethod
    def get_overdue_loans(cls):
        """Get all overdue loans"""
        today = timezone.now().date()
        return cls.objects.filter(
            status='active',
            due_date__lt=today
        )

    @classmethod
    def get_user_active_loans(cls, user):
        """Get all active loans for a user"""
        return cls.objects.filter(
            user=user,
            status='active'
        )

    @classmethod
    def get_monthly_stats(cls, year=None, month=None):
        """Get loan statistics for a specific month"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
            
        return cls.objects.filter(
            loan_date__year=year,
            loan_date__month=month
        ).aggregate(
            total_loans=models.Count('id'),
            returned_count=models.Count('id', filter=models.Q(status='returned')),
            active_count=models.Count('id', filter=models.Q(status='borrowed')),
            overdue_count=models.Count('id', filter=models.Q(status='overdue'))
        )
