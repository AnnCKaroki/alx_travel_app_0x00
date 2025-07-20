 #!/usr/bin/env python3
"""
    Serializers for the listings application models.
    """

from rest_framework import serializers
from .models import Listing, Booking, Review # Import all models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
        """
        Serializer for the custom User model.
        Used to represent basic user information in related models.
        """
        class Meta:
            model = User
            fields = ('id', 'first_name', 'last_name', 'email')
            read_only_fields = ('id', 'email')


class ListingSerializer(serializers.ModelSerializer):
        """
        Serializer for the Listing model.
        Includes nested host information for read operations.
        """
        host = UserSerializer(read_only=True) # Nested serializer for host details
        # For creating/updating, you might want to accept host_id directly
        host_id = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(), write_only=True, source='host'
        )
        # Optional: Include reviews in the listing detail
        reviews = serializers.SerializerMethodField()

        class Meta:
            model = Listing
            fields = (
                'listing_id', 'host', 'host_id', 'title', 'description',
                'address', 'city', 'country', 'price_per_night',
                'property_type', 'num_bedrooms', 'num_bathrooms',
                'max_guests', 'amenities', 'created_at', 'updated_at',
                'reviews'
            )
            read_only_fields = ('listing_id', 'created_at', 'updated_at', 'host')
            extra_kwargs = {
                'host': {'read_only': True}, # Ensure host is read-only
                'host_id': {'write_only': True} # Ensure host_id is write-only
            }

        def get_reviews(self, obj):
            """
            Returns serialized reviews for the listing.
            """
            reviews = obj.reviews.all().order_by('-created_at')
            return ReviewSerializer(reviews, many=True).data


class BookingSerializer(serializers.ModelSerializer):
        """
        Serializer for the Booking model.
        Includes nested property and user information for read operations.
        """
        property = serializers.SerializerMethodField() # Custom representation of property
        user = UserSerializer(read_only=True) # Nested serializer for user details
        # For creating/updating, accept IDs directly
        property_id = serializers.PrimaryKeyRelatedField(
            queryset=Listing.objects.all(), write_only=True, source='property'
        )
        user_id = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(), write_only=True, source='user'
        )

        class Meta:
            model = Booking
            fields = (
                'booking_id', 'property', 'user', 'check_in_date',
                'check_out_date', 'total_price', 'status', 'booked_at',
                'property_id', 'user_id'
            )
            read_only_fields = ('booking_id', 'booked_at', 'property', 'user')
            extra_kwargs = {
                'property': {'read_only': True},
                'user': {'read_only': True},
                'property_id': {'write_only': True},
                'user_id': {'write_only': True},
            }

        def get_property(self, obj):
            """
            Returns a simplified representation of the associated property.
            """
            return {
                'listing_id': obj.property.listing_id,
                'title': obj.property.title,
                'city': obj.property.city,
                'country': obj.property.country,
                'price_per_night': obj.property.price_per_night
            }


class ReviewSerializer(serializers.ModelSerializer):
        """
        Serializer for the Review model.
        Includes nested user information for read operations.
        """
        user = UserSerializer(read_only=True)
        # For creating/updating, accept IDs directly
        property_id = serializers.PrimaryKeyRelatedField(
            queryset=Listing.objects.all(), write_only=True, source='property'
        )
        user_id = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(), write_only=True, source='user'
        )

        class Meta:
            model = Review
            fields = (
                'review_id', 'property', 'user', 'rating', 'comment',
                'created_at', 'property_id', 'user_id'
            )
            read_only_fields = ('review_id', 'created_at', 'property', 'user')
            extra_kwargs = {
                'property': {'read_only': True},
                'user': {'read_only': True},
                'property_id': {'write_only': True},
                'user_id': {'write_only': True},
            }
