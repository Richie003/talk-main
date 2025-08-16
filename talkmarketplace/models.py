from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from utils.models import ModelUtilsMixin
# from utils.custom_enums import ProductSize, ProductTags, StockId
from polymorphic.models import PolymorphicModel

def primary_image_upload_path(instance, filename):
    return f"products/imgs/{instance.service_provider.talk_id}/{slugify(instance.name)}-{filename}"

def secondary_images_upload_path(instance, filename):
    return f"products/imgs/{instance.product.user.talk_id}/secondary/{slugify(instance.product.name)}-{filename}"

def product_video_upload_path(instance, filename):
    return f"products/vids/{instance.service_provider.talk_id}/{slugify(instance.name)}-{filename}"

class Product(ModelUtilsMixin, PolymorphicModel):
    """
    Base model for products in the marketplace.
    This model can be extended by other product models like MarketPlaceProduct and TakaProduct.
    """
    name = models.CharField(max_length=255, null=False)
    slug = models.SlugField(unique=True, null=False, blank=True)
    description = models.TextField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=False)
    address = models.CharField(max_length=255, null=False)
    negotiable = models.BooleanField(default=False)
    primary_image = models.ImageField(upload_to=primary_image_upload_path, null=True, blank=True)
    approved = models.BooleanField(default=False)


    # class Meta:
    #     abstract = True


class MarketPlaceProduct(Product):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, related_name='marketplace_products')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if eval(self.user.user_role)[0] != 'service providers':
            raise ValueError("Only service providers can create products.")
        if not self.slug:
            super().save(*args, **kwargs)
            self.slug = f"{slugify(self.name)}-{self.id}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    def product_profile(self):
            return {
                "id": self.id,
                "name": self.name,
                "slug": self.slug,
                "description": self.description,
                "category": self.category.name,
                "price": str(self.price),
                "primary_image": self.primary_image.url if self.primary_image else None,
                "extra_images": self.get_images(),
                "videos": self.get_videos(),
                "reviews": self.get_reviews(),
                "created_by": str(self.user.first_name) + " " + str(self.user.last_name),
                "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": self.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "approved": self.approved,
            }

    def get_absolute_url(self):
        return reverse('marketplace_product_detail', kwargs={'slug': self.slug})
    

    def get_images(self):
        return [image.image.url for image in self.marketplace_images.all() if image.image]

    def get_videos(self):
        return [video.video_path.url for video in self.marketplace_videos.all() if video.video_path]

    def get_reviews(self):
        return [review.comment for review in self.marketplace_reviews.all() if review.comment]

    def get_average_rating(self):
        if self.marketplace_reviews.exists():
            total_rating = sum(review.rating for review in self.marketplace_reviews.all())
            return total_rating / self.get_review_count()
        return 0

    def get_review_count(self):
        return self.marketplace_reviews.count()


class MarketPlaceProductImage(ModelUtilsMixin):
    product = models.ForeignKey(MarketPlaceProduct, on_delete=models.CASCADE, related_name='marketplace_images')
    image = models.ImageField(upload_to=secondary_images_upload_path, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class MarketPlaceProductVideo(ModelUtilsMixin):
    product = models.ForeignKey(MarketPlaceProduct, on_delete=models.CASCADE, related_name='marketplace_videos')
    video_path = models.FileField(upload_to=secondary_images_upload_path, null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Video for {self.product.name}"

class MarketPlaceProductReview(ModelUtilsMixin):
    product = models.ForeignKey(MarketPlaceProduct, on_delete=models.CASCADE, related_name='marketplace_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField(null=True, blank=True)

# Everything TAKA...

class TakaProduct(Product):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, related_name='taka_products')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=False)
    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)  # Save to generate ID
            self.slug = f"{slugify(self.name)}-{self.id}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)
    

    def product_profile(self):
            return {
                "id": self.id,
                "name": self.name,
                "slug": self.slug,
                "description": self.description,
                "category": self.category.name,
                "price": str(self.price),
                "primary_image": self.primary_image.url,
                "extra_images": self.get_images(),
                "videos": self.get_videos(),
                "reviews": self.get_reviews(),
                "created_by": str(self.user.first_name) + " " + str(self.user.last_name),
                "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": self.updated.strftime("%Y-%m-%d %H:%M:%S"),
                "approved": self.approved,
            }

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    

    def get_images(self):
        return [image.image.url for image in self.taka_images.all() if image.image]

    def get_videos(self):
        return [video.video_path.url for video in self.taka_videos.all() if video.video_path]

    def get_reviews(self):
        return [review.comment for review in self.taka_reviews.all() if review.comment]

    def get_average_rating(self):
        if self.taka_reviews.exists():
            total_rating = sum(review.rating for review in self.taka_reviews.all())
            return total_rating / self.get_review_count()
        return 0

    def get_review_count(self):
        return self.taka_reviews.count()

class TakaProductImage(ModelUtilsMixin):
    product = models.ForeignKey(TakaProduct, on_delete=models.CASCADE, related_name='taka_images')
    image = models.ImageField(upload_to=secondary_images_upload_path, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class TakaProductVideo(ModelUtilsMixin):
    product = models.ForeignKey(TakaProduct, on_delete=models.CASCADE, related_name='taka_videos')
    video_path = models.FileField(upload_to=secondary_images_upload_path, null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Video for {self.product.name}"

class TakaReview(ModelUtilsMixin):
    product = models.ForeignKey(TakaProduct, on_delete=models.CASCADE, related_name='taka_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField(null=True, blank=True)

class Category(ModelUtilsMixin):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.name)

class SavedItem(ModelUtilsMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, related_name='saved_items')

    def __str__(self):
        return f"{self.user.username}'s saved items"
    
    def save_item(self, product):
        self.product.add(product)
    
    def remove_item(self, product):
        self.product.remove(product)
    
    def get_saved_items(self):
        return self.product.all()

    def clear_saved_items(self):
        self.product.clear()
    
    def is_item_saved(self, product):
        return self.product.filter(id=product.id).exists()
    
    def get_user_saved_items(self):
        return self.product.filter(saved_items__user=self.user)

    def get_saved_item_count(self):
        return self.product.count()
    
    def get_saved_item_details(self):
        return [item.product_profile() for item in self.product.all()]
    
    def get_saved_item_by_id(self, product_id):
        return self.product.filter(id=product_id).first().product_profile() if self.product.filter(id=product_id).exists() else None
