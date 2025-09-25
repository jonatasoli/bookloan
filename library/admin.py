from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from core.models import Book, BookLoan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Django Admin configuration for Book model"""
    list_display = ['title', 'author', 'isbn', 'total_copies', 'available_copies', 'is_available']
    list_filter = ['author', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn')
        }),
        ('Inventory', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_available(self, obj):
        """Display availability status with color coding"""
        if obj.available_copies > 0:
            return format_html(
                '<span style="color: green;">✓ Available ({})</span>',
                obj.available_copies
            )
        else:
            return format_html('<span style="color: red;">✗ Not Available</span>')
    is_available.short_description = 'Available'


@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    """Django Admin configuration for BookLoan model"""
    list_display = [
        'book', 'user', 'status', 'loan_date', 'due_date', 
        'return_date', 'is_overdue_display', 'days_overdue_display'
    ]
    list_filter = ['status', 'loan_date', 'due_date', 'book__author']
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'book__title', 'book__author'
    ]
    date_hierarchy = 'loan_date'
    readonly_fields = ['created_at', 'updated_at', 'loan_duration_display']
    raw_id_fields = ['user', 'book']

    fieldsets = (
        ('Loan Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('loan_date', 'due_date', 'return_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'fine_amount')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'loan_duration_display'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue_display(self, obj):
        """Display overdue status with color coding"""
        if obj.status == 'borrowed' and obj.is_overdue:
            return format_html('<span style="color: red;">⚠ OVERDUE</span>')
        elif obj.status == 'borrowed':
            return format_html('<span style="color: green;">✓ On Time</span>')
        else:
            return format_html('<span style="color: gray;">-</span>')
    is_overdue_display.short_description = 'Status'

    def days_overdue_display(self, obj):
        """Display days overdue"""
        if obj.days_overdue > 0:
            return format_html(
                '<span style="color: red;">{} days</span>',
                obj.days_overdue
            )
        return '-'
    days_overdue_display.short_description = 'Days Overdue'

    def loan_duration_display(self, obj):
        """Display loan duration"""
        return f"{obj.loan_duration} days"
    loan_duration_display.short_description = 'Loan Duration'

    actions = ['mark_as_returned', 'extend_due_date']

    def mark_as_returned(self, request, queryset):
        """Admin action to mark selected loans as returned"""
        count = 0
        for loan in queryset:
            if loan.status == 'borrowed':
                loan.mark_returned()
                count += 1
        
        self.message_user(request, f'{count} loans marked as returned.')
    mark_as_returned.short_description = 'Mark selected loans as returned'

    def extend_due_date(self, request, queryset):
        """Admin action to extend due date by 14 days"""
        count = 0
        for loan in queryset:
            if loan.status == 'borrowed':
                loan.extend_due_date()
                count += 1
        
        self.message_user(request, f'{count} loans extended by 14 days.')
    extend_due_date.short_description = 'Extend due date by 14 days'

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user', 'book')

    # Custom filters
    def get_list_filter(self, request):
        """Dynamic list filters"""
        filters = list(self.list_filter)
        
        # Add overdue filter
        class OverdueFilter(admin.SimpleListFilter):
            title = 'overdue status'
            parameter_name = 'overdue'

            def lookups(self, request, model_admin):
                return (
                    ('yes', 'Overdue'),
                    ('no', 'Not Overdue'),
                )

            def queryset(self, request, queryset):
                today = timezone.now().date()
                if self.value() == 'yes':
                    return queryset.filter(status='borrowed', due_date__lt=today)
                if self.value() == 'no':
                    return queryset.filter(status='borrowed', due_date__gte=today)
                return queryset

        filters.append(OverdueFilter)
        return filters
