# listings/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Listing(models.Model):
        """
        Model representing a property listing available for booking.
        """
        listing_id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False,
            db_index=True,
            verbose_name=_('Listing ID')
        )
        # Foreign Key to the User model (host of the property)
        host = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='listings',
            verbose_name=_('Host')
        )
        title = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('Title'))
        description = models.TextField(null=False, blank=False, verbose_name=_('Description'))
        address = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('Address'))
        city = models.CharField(max_length=100, null=False, blank=False, verbose_name=_('City'))
        country = models.CharField(max_length=100, null=False, blank=False, verbose_name=_('Country'))
        price_per_night = models.DecimalField(
            max_digits=10, decimal_places=2, null=False, blank=False, verbose_name=_('Price Per Night')
        )
        # Example for property type (ENUM)
        PROPERTY_TYPE_CHOICES = [
            ('room', 'Room'),
            ('mansion', 'Mansion'),
            ('countryside', 'Countryside'),
            ('cabin', 'Cabin'),
            ('apartment', 'Apartment'),
            ('villa', 'Villa'),
        ]
        property_type = models.CharField(
            max_length=20,
            choices=PROPERTY_TYPE_CHOICES,
            default='room',
            null=False,
            blank=False,
            verbose_name=_('Property Type')
        )
        num_bedrooms = models.IntegerField(null=False, blank=False, verbose_name=_('Number of Bedrooms'))
        num_bathrooms = models.IntegerField(null=False, blank=False, verbose_name=_('Number of Bathrooms'))
        max_guests = models.IntegerField(null=False, blank=False, verbose_name=_('Maximum Guests'))
        amenities = models.TextField(blank=True, verbose_name=_('Amenities')) # Store as comma-separated string or JSON
        created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
        updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

        class Meta:
            """Meta options for the Listing model."""
            verbose_name = _('Listing')
            verbose_name_plural = _('Listings')
            db_table = 'listings'

        def __str__(self):
            """String representation of the Listing model."""
            return self.title
class Booking(models.Model):
        """
        Model representing a booking made by a user for a specific listing.
        """
        booking_id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False,
            db_index=True,
            verbose_name=_('Booking ID')
        )
        # Foreign Key to the Listing model
        property = models.ForeignKey(
            Listing,
            on_delete=models.CASCADE,
            related_name='bookings',
            verbose_name=_('Property')
        )
        # Foreign Key to the User model (the user making the booking)
        user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='bookings',
            verbose_name=_('User')
        )
        check_in_date = models.DateField(null=False, blank=False, verbose_name=_('Check-in Date'))
        check_out_date = models.DateField(null=False, blank=False, verbose_name=_('Check-out Date'))
        total_price = models.DecimalField(
            max_digits=10, decimal_places=2, null=False, blank=False, verbose_name=_('Total Price')
        )
        # Status choices
        STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('canceled', 'Canceled'),
        ]
        status = models.CharField(
            max_length=10,
            choices=STATUS_CHOICES,
            default='pending',
            null=False,
            blank=False,
            verbose_name=_('Status')
        )
        booked_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Booked At'))

        class Meta:
            """Meta options for the Booking model."""
            verbose_name = _('Booking')
            verbose_name_plural = _('Bookings')
            db_table = 'bookings'


        def __str__(self):
            """String representation of the Booking model."""
            return f"Booking {self.booking_id} for {self.property.title} by {self.user.email}"

class Review(models.Model):
        """
        Model representing a review given by a user for a specific listing.
        """
        review_id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False,
            db_index=True,
            verbose_name=_('Review ID')
        )
        # Foreign Key to the Listing model
        property = models.ForeignKey(
            Listing,
            on_delete=models.CASCADE,
            related_name='reviews',
            verbose_name=_('Property')
        )

        user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='reviews',
            verbose_name=_('User')
        )
        rating = models.IntegerField(
            choices=[(i, str(i)) for i in range(1, 6)],
            null=False,
            blank=False,
            verbose_name=_('Rating')
        )
        comment = models.TextField(blank=True, verbose_name=_('Comment'))
        created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

        class Meta:
            """Meta options for the Review model."""
            verbose_name = _('Review')
            verbose_name_plural = _('Reviews')
            db_table = 'reviews'

            unique_together = ('property', 'user')

        def __str__(self):
            """String representation of the Review model."""
            return f"Review for {self.property.title} by {self.user.email} - {self.rating} stars"
