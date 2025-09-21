from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model to include in nested serializations.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    """
    guest = UserSerializer(read_only=True)
    guest_name = serializers.CharField(source='guest.username', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'booking', 'listing', 'guest', 'guest_name',
            'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'guest', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model.
    """
    host = UserSerializer(read_only=True)
    host_name = serializers.CharField(source='host.username', read_only=True)
    amenities_list = serializers.ReadOnlyField(source='get_amenities_list')
    average_rating = serializers.ReadOnlyField()
    reviews_count = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'host', 'host_name', 'title', 'description',
            'location', 'price_per_night', 'bedrooms', 'bathrooms',
            'max_guests', 'property_type', 'amenities', 'amenities_list',
            'available', 'average_rating', 'reviews_count', 'reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'listing_id', 'host', 'average_rating', 'reviews_count',
            'created_at', 'updated_at'
        ]

    def get_reviews_count(self, obj):
        """Get the number of reviews for this listing."""
        return obj.reviews.count()


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    """
    guest = UserSerializer(read_only=True)
    guest_name = serializers.CharField(source='guest.username', read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    duration_nights = serializers.ReadOnlyField()
    review = ReviewSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'guest', 'guest_name', 'listing', 'listing_title',
            'check_in_date', 'check_out_date', 'number_of_guests',
            'total_price', 'status', 'special_requests', 'duration_nights',
            'review', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'booking_id', 'guest', 'total_price', 'duration_nights',
            'created_at', 'updated_at'
        ]