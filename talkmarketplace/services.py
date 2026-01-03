from django.db import transaction
from django.db.models import Avg
from .models import MarketPlaceProduct, TakaProduct

def update_marketplace_product_rating(product, user, new_rating):
    """
    Handles both creating a new rating and updating an existing one.
    Also recalculates Bayesian rating.
    """
    with transaction.atomic():
        
        # Get existing review if exists
        review = product.marketplace_reviews.filter(user=user).first()

        if review:
            # User is updating rating
            old_rating = review.rating
            review.rating = new_rating
            review.save()

            # Update product aggregates
            product.total_rating = product.total_rating - old_rating + new_rating

        else:
            # First time rating
            product.marketplace_reviews.create(
                product=product,
                user=user,
                rating=new_rating
            )
            product.total_rating += new_rating
            product.review_count += 1

        # Compute global average rating across all products (C)
        global_avg = MarketPlaceProduct.objects.aggregate(
            avg=Avg('total_rating')
        )['avg'] or 0

        # Minimum number of reviews before normal average becomes significant
        m = 20  # you can tune this

        # Update Bayesian average
        product.bayesian_rating = product.compute_bayesian_rating(global_avg, m)

        product.save()


def update_taka_product_rating(product, user, new_rating):
    """
    Handles both creating a new rating and updating an existing one.
    Also recalculates Bayesian rating.
    """
    with transaction.atomic():
        
        # Get existing review if exists
        review = product.taka_reviews.filter(user=user).first()

        if review:
            # User is updating rating
            old_rating = review.rating
            review.rating = new_rating
            review.save()

            # Update product aggregates
            product.total_rating = product.total_rating - old_rating + new_rating

        else:
            # First time rating
            product.taka_reviews.create(
                product=product,
                user=user,
                rating=new_rating
            )
            product.total_rating += new_rating
            product.review_count += 1

        # Compute global average rating across all products (C)
        global_avg = MarketPlaceProduct.objects.aggregate(
            avg=Avg('total_rating')
        )['avg'] or 0

        # Minimum number of reviews before normal average becomes significant
        m = 20  # you can tune this

        # Update Bayesian average
        product.bayesian_rating = product.compute_bayesian_rating(global_avg, m)

        product.save()
