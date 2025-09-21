import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from alx_travel_app.listings.models import Listing, Booking, Review


class Command(BaseCommand):
    """
    Management command to seed the database with sample data.
    """
    
    help = 'Seed the database with sample data for listings, bookings, and reviews'

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=50,
            help='Number of bookings to create (default: 50)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=30,
            help='Number of reviews to create (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        if options['clear']:
            self.clear_data()
        
        self.create_users()
        self.create_listings(options['listings'])
        self.create_bookings(options['bookings'])
        self.create_reviews(options['reviews'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded database with:\n"
                f"- {options['listings']} listings\n"
                f"- {options['bookings']} bookings\n"
                f"- {options['reviews']} reviews"
            )
        )

    def clear_data(self):
        """Clear existing data."""
        self.stdout.write("Clearing existing data...")
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS("Data cleared successfully."))

    def create_users(self):
        """Create sample users."""
        self.stdout.write("Creating users...")
        
        users_data = [
            {'username': 'john_host', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Smith'},
            {'username': 'sarah_host', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Johnson'},
            {'username': 'mike_host', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Wilson'},
            {'username': 'david_guest', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Davis'},
            {'username': 'emma_guest', 'email': 'emma@example.com', 'first_name': 'Emma', 'last_name': 'Taylor'},
            {'username': 'alex_guest', 'email': 'alex@example.com', 'first_name': 'Alex', 'last_name': 'Anderson'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()

    def create_listings(self, count):
        """Create sample listings."""
        self.stdout.write(f"Creating {count} listings...")
        
        hosts = User.objects.filter(username__contains='host')
        locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Miami, FL']
        property_types = ['apartment', 'house', 'villa', 'condo']
        
        for i in range(count):
            host = random.choice(hosts)
            
            Listing.objects.create(
                host=host,
                title=f"Beautiful {random.choice(['Cozy', 'Modern', 'Luxury'])} {random.choice(['Apartment', 'House', 'Villa'])} {i+1}",
                description="A wonderful place to stay with all modern amenities.",
                location=random.choice(locations),
                price_per_night=Decimal(str(random.randint(50, 300))),
                bedrooms=random.randint(1, 4),
                bathrooms=random.randint(1, 3),
                max_guests=random.randint(2, 8),
                property_type=random.choice(property_types),
                amenities="WiFi,Kitchen,Parking,Pool",
                available=True
            )

    def create_bookings(self, count):
        """Create sample bookings."""
        self.stdout.write(f"Creating {count} bookings...")
        
        guests = User.objects.filter(username__contains='guest')
        listings = list(Listing.objects.all())
        statuses = ['pending', 'confirmed', 'completed', 'canceled']
        
        for i in range(count):
            guest = random.choice(guests)
            listing = random.choice(listings)
            
            start_date = timezone.now().date() + timedelta(days=random.randint(1, 60))
            end_date = start_date + timedelta(days=random.randint(1, 7))
            nights = (end_date - start_date).days
            
            Booking.objects.create(
                guest=guest,
                listing=listing,
                check_in_date=start_date,
                check_out_date=end_date,
                number_of_guests=random.randint(1, listing.max_guests),
                total_price=listing.price_per_night * nights,
                status=random.choice(statuses)
            )

    def create_reviews(self, count):
        """Create sample reviews."""
        self.stdout.write(f"Creating {count} reviews...")
        
        completed_bookings = Booking.objects.filter(status='completed')
        if not completed_bookings:
            self.stdout.write("No completed bookings for reviews.")
            return
        
        comments = [
            "Great place to stay! Highly recommended.",
            "Clean and comfortable. Would book again.",
            "Amazing host and beautiful property.",
            "Perfect location and excellent amenities."
        ]
        
        for booking in completed_bookings[:count]:
            Review.objects.get_or_create(
                booking=booking,
                defaults={
                    'listing': booking.listing,
                    'guest': booking.guest,
                    'rating': random.randint(3, 5),
                    'comment': random.choice(comments)
                }
            )