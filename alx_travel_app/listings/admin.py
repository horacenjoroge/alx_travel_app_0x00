from django.contrib import admin
from django.utils.html import format_html
from .models import Listing, Booking, Review


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Admin interface for Listing model.
    """
    list_display = [
        'title', 'host', 'location', 'property_type', 
        'price_per_night', 'bedrooms', 'bathrooms', 
        'max_guests', 'available', 'created_at'
    ]
    list_filter = [
        'property_type', 'available', 'bedrooms', 
        'bathrooms', 'created_at', 'location'
    ]
    search_fields = ['title', 'description', 'location', 'host__username']
    readonly_fields = ['listing_id', 'created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin interface for Booking model.
    """
    list_display = [
        'booking_id', 'guest', 'listing', 
        'check_in_date', 'check_out_date',
        'number_of_guests', 'total_price', 'status', 
        'created_at'
    ]
    list_filter = [
        'status', 'check_in_date', 'check_out_date', 
        'created_at'
    ]
    search_fields = [
        'booking_id', 'guest__username', 
        'listing__title'
    ]
    readonly_fields = [
        'booking_id', 'total_price', 
        'created_at', 'updated_at'
    ]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface for Review model.
    """
    list_display = [
        'review_id', 'guest', 'listing', 
        'rating', 'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = [
        'comment', 'guest__username', 'listing__title'
    ]
    readonly_fields = [
        'review_id', 'booking', 'listing', 'guest', 
        'created_at', 'updated_at'
    ]
