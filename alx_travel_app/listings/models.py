from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Listing(models.Model):
    """
    Model representing a property listing available for booking.
    """
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('condo', 'Condominium'),
        ('cabin', 'Cabin'),
        ('studio', 'Studio'),
    ]
    
    listing_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the listing"
    )
    host = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='listings',
        help_text="Host who owns this listing"
    )
    title = models.CharField(
        max_length=200,
        help_text="Title of the listing"
    )
    description = models.TextField(
        help_text="Detailed description of the property"
    )
    location = models.CharField(
        max_length=100,
        help_text="Location of the property"
    )
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price per night in USD"
    )
    bedrooms = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of bedrooms"
    )
    bathrooms = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of bathrooms"
    )
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of guests"
    )
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='apartment',
        help_text="Type of property"
    )
    amenities = models.TextField(
        blank=True,
        help_text="Comma-separated list of amenities"
    )
    available = models.BooleanField(
        default=True,
        help_text="Whether the listing is currently available for booking"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the listing was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the listing was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['property_type']),
            models.Index(fields=['available']),
        ]

    def __str__(self):
        return f"{self.title} - {self.location}"

    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_amenities_list(self):
        """Return amenities as a list."""
        if self.amenities:
            return [amenity.strip() for amenity in self.amenities.split(',')]
        return []


class Booking(models.Model):
    """
    Model representing a booking made by a guest for a listing.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]

    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the booking"
    )
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Guest who made the booking"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Listing being booked"
    )
    check_in_date = models.DateField(
        help_text="Check-in date"
    )
    check_out_date = models.DateField(
        help_text="Check-out date"
    )
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of guests for this booking"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Total price for the booking"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    special_requests = models.TextField(
        blank=True,
        help_text="Special requests from the guest"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the booking was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the booking was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in_date']),
            models.Index(fields=['check_out_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Booking {self.booking_id} - {self.listing.title}"

    def clean(self):
        """Custom validation for booking dates and guest capacity."""
        from django.core.exceptions import ValidationError
        
        if self.check_in_date and self.check_out_date:
            if self.check_out_date <= self.check_in_date:
                raise ValidationError("Check-out date must be after check-in date.")
            
            if self.check_in_date < timezone.now().date():
                raise ValidationError("Check-in date cannot be in the past.")
        
        if self.listing and self.number_of_guests > self.listing.max_guests:
            raise ValidationError(
                f"Number of guests ({self.number_of_guests}) exceeds listing capacity ({self.listing.max_guests})."
            )

    def save(self, *args, **kwargs):
        """Override save to perform validation and calculate total price."""
        self.clean()
        
        # Calculate total price if not set
        if not self.total_price and self.listing and self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            self.total_price = self.listing.price_per_night * nights
        
        super().save(*args, **kwargs)

    @property
    def duration_nights(self):
        """Calculate the number of nights for this booking."""
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0


class Review(models.Model):
    """
    Model representing a review left by a guest for a listing.
    """
    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the review"
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        help_text="Booking this review is associated with"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Listing being reviewed"
    )
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Guest who wrote the review"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(
        help_text="Review comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the review was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the review was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Review by {self.guest.username} for {self.listing.title} - {self.rating} stars"

    def clean(self):
        """Custom validation to ensure review integrity."""
        from django.core.exceptions import ValidationError
        
        if self.booking and self.listing and self.booking.listing != self.listing:
            raise ValidationError("Review listing must match the booking listing.")
        
        if self.booking and self.guest and self.booking.guest != self.guest:
            raise ValidationError("Review guest must match the booking guest.")
        
        if self.booking and self.booking.status != 'completed':
            raise ValidationError("Reviews can only be created for completed bookings.")

    def save(self, *args, **kwargs):
        """Override save to perform validation."""
        self.clean()
        super().save(*args, **kwargs)