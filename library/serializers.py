from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Book, BookLoan


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'available_copies', 'total_copies']


class BookLoanSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    days_overdue = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BookLoan
        fields = [
            'id', 'user', 'user_id', 'book', 'book_id', 'loan_date', 
            'due_date', 'return_date', 'status', 'status_display', 
            'notes', 'fine_amount', 'days_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'loan_date']

    def get_days_overdue(self, obj):
        """Calculate days overdue for active loans"""
        return obj.days_overdue if hasattr(obj, 'days_overdue') else None

    def validate(self, data):
        """Custom validation for BookLoan"""
        book = Book.objects.get(id=data['book_id'])
        
        # Check if book is available for loan (only for new loans)
        if not self.instance:  # Creating new loan
            if book.available_copies <= 0:
                raise serializers.ValidationError("This book is not available for loan")
        
        # Check if user already has this book on loan
        user_id = data['user_id']
        existing_loan = BookLoan.objects.filter(
            user_id=user_id, 
            book_id=data['book_id'], 
            status='active'
        )
        
        if self.instance:
            existing_loan = existing_loan.exclude(id=self.instance.id)
            
        if existing_loan.exists():
            raise serializers.ValidationError("User already has this book on loan")
        
        return data

    def create(self, validated_data):
        """Create new BookLoan - availability is handled when loan is approved"""
        book_loan = BookLoan.objects.create(**validated_data)
        return book_loan

    def update(self, instance, validated_data):
        """Update BookLoan and handle book availability"""
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # Update the loan
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle book availability changes
        if old_status == 'active' and new_status == 'returned':
            # Book returned - increase available copies
            instance.book.available_copies += 1
            instance.book.save()
        elif old_status == 'returned' and new_status == 'active':
            # Book borrowed again - decrease available copies
            if instance.book.available_copies > 0:
                instance.book.available_copies -= 1
                instance.book.save()
        elif old_status == 'pending' and new_status == 'active':
            # Loan approved - decrease available copies
            if instance.book.available_copies > 0:
                instance.book.available_copies -= 1
                instance.book.save()
        
        return instance


class BookLoanCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating loans"""
    class Meta:
        model = BookLoan
        fields = ['user_id', 'book_id', 'due_date', 'notes']

    def validate(self, data):
        # Same validation as BookLoanSerializer
        book = Book.objects.get(id=data['book_id'])
        
        if book.available_copies <= 0:
            raise serializers.ValidationError("This book is not available for loan")
        
        existing_loan = BookLoan.objects.filter(
            user_id=data['user_id'], 
            book_id=data['book_id'], 
            status='active'
        )
        
        if existing_loan.exists():
            raise serializers.ValidationError("User already has this book on loan")
        
        return data
