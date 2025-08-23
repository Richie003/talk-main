from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from utils.models import ModelUtilsMixin
# from utils.custom_enums import ProductSize, ProductTags, StockId
from polymorphic.models import PolymorphicModel

def marketplace_image_upload_path(instance, filename):
    return f"products/marketplace/imgs/{instance.product.user.talk_id}/{slugify(instance.name)}-{filename}"

def taka_image_upload_path(instance, filename):
    return f"products/taka/imgs/{instance.product.user.talk_id}/{slugify(instance.name)}-{filename}"

def marketplace_video_upload_path(instance, filename):
    return f"products/marketplace/vids/{instance.product.user.talk_id}/{slugify(instance.name)}-{filename}"

def taka_video_upload_path(instance, filename):
    return f"products/taka/vids/{instance.product.user.talk_id}/{slugify(instance.name)}-{filename}"

class Product(ModelUtilsMixin, PolymorphicModel):
    """
    Base model for products in the marketplace.
    This model can be extended by other product models like MarketPlaceProduct and TakaProduct.
    """
    name = models.CharField(max_length=255, null=False)
    slug = models.SlugField(unique=True, null=False, blank=True)
    description = models.TextField(null=False)
    category = models.CharField(max_length=225, blank=True, default="None")
    tag = models.CharField(max_length=225, blank=True, default="None")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=False,  default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=False,  default=0.00)
    negotiable = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)


    # class Meta:
    #     abstract = True


class MarketPlaceProduct(Product):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, related_name='marketplace_products')
    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if eval(self.user.user_role)[0] != 'service providers':
            raise ValueError("Only service providers can create products.")
        if not self.slug and self.id:  # id exists
            self.slug = f"{slugify(self.name)}-{self.id}"
        super().save(*args, **kwargs)


    def product_profile(self):
            return {
                "id": self.id,
                "name": self.name,
                "slug": self.slug,
                "description": self.description,
                "category": self.category,
                "tag": self.tag,
                "price": str(self.price),
                "discount": str(self.discount),
                "images": self.get_images(),
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
    image = models.ImageField(upload_to=marketplace_image_upload_path, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class MarketPlaceProductVideo(ModelUtilsMixin):
    product = models.ForeignKey(MarketPlaceProduct, on_delete=models.CASCADE, related_name='marketplace_videos')
    video_path = models.FileField(upload_to=marketplace_video_upload_path, null=True, blank=True)
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
    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug and self.id:  # id exists
            self.slug = f"{slugify(self.name)}-{self.id}"
        super().save(*args, **kwargs)

    

    def product_profile(self):
            return {
                "id": self.id,
                "name": self.name,
                "slug": self.slug,
                "description": self.description,
                "tag": self.tag,
                "price": str(self.price),
                "discount": str(self.discount),
                "images": self.get_images(),
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
    image = models.ImageField(upload_to=taka_image_upload_path, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class TakaProductVideo(ModelUtilsMixin):
    product = models.ForeignKey(TakaProduct, on_delete=models.CASCADE, related_name='taka_videos')
    video_path = models.FileField(upload_to=taka_video_upload_path, null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Video for {self.product.name}"

class TakaReview(ModelUtilsMixin):
    product = models.ForeignKey(TakaProduct, on_delete=models.CASCADE, related_name='taka_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField(null=True, blank=True)

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
