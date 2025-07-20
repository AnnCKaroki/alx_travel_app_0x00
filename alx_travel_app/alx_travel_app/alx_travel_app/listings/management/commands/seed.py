    #!/usr/bin/env python3
"""
    Django management command to seed the database with sample data for listings,
    users, bookings, and reviews.
    """

import random
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review

User = get_user_model()

class Command(BaseCommand):
        """
        Management command to seed the database with sample data.
        """
        help = 'Seeds the database with sample listings, users, bookings, and reviews.'

        def add_arguments(self, parser):
            """
            Adds arguments to the command-line parser.
            """
            parser.add_argument(
                '--clear',
                action='store_true',
                help='Clear existing data before seeding.',
            )
            parser.add_argument(
                '--num_users',
                type=int,
                default=5,
                help='Number of sample users to create.',
            )
            parser.add_argument(
                '--num_listings_per_host',
                type=int,
                default=3,
                help='Number of sample listings per host.',
            )
            parser.add_argument(
                '--num_bookings_per_listing',
                type=int,
                default=2,
                help='Number of sample bookings per listing.',
            )
            parser.add_argument(
                '--num_reviews_per_listing',
                type=int,
                default=1,
                help='Number of sample reviews per listing.',
            )

        def handle(self, *args, **options):
            """
            Handles the execution of the seed command.
            """
            self.stdout.write(self.style.NOTICE("Starting database seeding..."))

            if options['clear']:
                self.stdout.write(self.style.WARNING("Clearing existing data..."))
                Review.objects.all().delete()
                Booking.objects.all().delete()
                Listing.objects.all().delete()
                User.objects.filter(is_superuser=False).delete() # Only delete non-superusers
                self.stdout.write(self.style.SUCCESS("Existing data cleared."))

            num_users = options['num_users']
            num_listings_per_host = options['num_listings_per_host']
            num_bookings_per_listing = options['num_bookings_per_listing']
            num_reviews_per_listing = options['num_reviews_per_listing']

            # Create sample users (some hosts, some guests)
            self.stdout.write(self.style.NOTICE(f"Creating {num_users} sample users..."))
            users = []
            for i in range(num_users):
                email = f"user{i}@example.com"
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(
                        username=f"user{i}",
                        email=email,
                        password="password123",
                        first_name=f"First{i}",
                        last_name=f"Last{i}",
                        role=random.choice(['guest', 'host'])
                    )
                    users.append(user)
                    self.stdout.write(self.style.SUCCESS(f"Created user: {user.email} ({user.role})"))
                else:
                    users.append(User.objects.get(email=email))
                    self.stdout.write(self.style.WARNING(f"User {email} already exists, skipping creation."))

            hosts = [u for u in users if u.role == 'host']
            guests = [u for u in users if u.role == 'guest']

            if not hosts:
                self.stdout.write(self.style.WARNING("No hosts created. Creating at least one host for listings."))
                host = User.objects.create_user(
                    username="auto_host",
                    email="auto_host@example.com",
                    password="password123",
                    first_name="Auto",
                    last_name="Host",
                    role="host"
                )
                hosts.append(host)
                users.append(host) # Add to general users list too

            # Create sample listings
            self.stdout.write(self.style.NOTICE("Creating sample listings..."))
            listings = []
            for host in hosts:
                for i in range(num_listings_per_host):
                    listing = Listing.objects.create(
                        host=host,
                        title=f"{host.first_name}'s {random.choice(['Cozy Room', 'Spacious Mansion', 'Rustic Cabin'])} {i+1}",
                        description=f"A beautiful {random.choice(['place', 'villa', 'apartment'])} in {random.choice(['New York', 'London', 'Paris', 'Tokyo', 'Sydney'])}.",
                        address=f"{random.randint(1, 100)} Main St",
                        city=random.choice(['New York', 'London', 'Paris', 'Tokyo', 'Sydney']),
                        country=random.choice(['USA', 'UK', 'France', 'Japan', 'Australia']),
                        price_per_night=random.uniform(50.00, 500.00),
                        property_type=random.choice([choice[0] for choice in Listing.PROPERTY_TYPE_CHOICES]),
                        num_bedrooms=random.randint(1, 5),
                        num_bathrooms=random.randint(1, 3),
                        max_guests=random.randint(1, 10),
                        amenities=random.choice(["WiFi, Pool", "Gym, Kitchen", "Parking, Balcony", "Pet-Friendly"]),
                    )
                    listings.append(listing)
                    self.stdout.write(self.style.SUCCESS(f"Created listing: {listing.title} by {host.email}"))

            # Create sample bookings
            self.stdout.write(self.style.NOTICE("Creating sample bookings..."))
            for listing in listings:
                for i in range(num_bookings_per_listing):
                    if guests:
                        guest = random.choice(guests)
                        check_in = timezone.now().date() + timedelta(days=random.randint(1, 30))
                        check_out = check_in + timedelta(days=random.randint(2, 7))
                        total_price = listing.price_per_night * (check_out - check_in).days
                        booking = Booking.objects.create(
                            property=listing,
                            user=guest,
                            check_in_date=check_in,
                            check_out_date=check_out,
                            total_price=total_price,
                            status=random.choice(['pending', 'confirmed', 'canceled'])
                        )
                        self.stdout.write(self.style.SUCCESS(f"Created booking for {listing.title} by {guest.email}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"No guest users available to create booking for {listing.title}"))

            # Create sample reviews
            self.stdout.write(self.style.NOTICE("Creating sample reviews..."))
            for listing in listings:
                for i in range(num_reviews_per_listing):
                    if guests:
                        reviewer = random.choice(guests)
                        # Ensure a user doesn't review the same property multiple times
                        if not Review.objects.filter(property=listing, user=reviewer).exists():
                            review = Review.objects.create(
                                property=listing,
                                user=reviewer,
                                rating=random.randint(1, 5),
                                comment=random.choice([
                                    "Great place!", "Highly recommended.", "Clean and cozy.",
                                    "Had a wonderful stay.", "Excellent value."
                                ])
                            )
                            self.stdout.write(self.style.SUCCESS(f"Created review for {listing.title} by {reviewer.email}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"User {reviewer.email} already reviewed {listing.title}, skipping."))
                    else:
                        self.stdout.write(self.style.WARNING(f"No guest users available to create review for {listing.title}"))


            self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
