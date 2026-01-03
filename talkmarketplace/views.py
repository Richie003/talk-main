from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    UpdateAPIView,
)
from .models import (
    Product,
    MarketPlaceProduct,
    TakaProduct,
    SavedProductItem,
    Service,
    MarketPlaceProductReview,
    TakaReview,
)
from .serializers import (
    MarketPlaceProductSerializer,
    MarketPlaceProductReviewSerializer,
    TakaProductSerializer,
    TakaProductReviewSerializer,
    SavedItemsSerializer,
    ServiceSerializer
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, status
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from utils.helpers import custom_response
from .services import update_marketplace_product_rating, update_taka_product_rating
from permissions.reviews import CanReviewProducts, CanViewProducts
from drf_spectacular.utils import extend_schema, extend_schema_view

tag_names = {
    "marketplace": "Marketplace",
    "taka": "Taka",
    "services": "Services",
    "inventory": "Inventory",
}

class SaveItemView(GenericAPIView):
    """
    Handles users saving product items for later.
    Prevents duplicates and ensures atomic operations.
    """
    serializer_class = SavedItemsSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=[tag_names["inventory"]],
        operation_id="Save an item for later",
        description="Saves one or more product items for the authenticated user."
    )
    def post(self, request, *args, **kwargs):
        product_ids = request.data.get("product", [])
        user = request.user

        if not isinstance(product_ids, list) or not product_ids:
            return Response(custom_response(
                status_mthd=status.HTTP_400_BAD_REQUEST,
                status="error",
                mssg="Invalid or empty product list.",
                data=None
            ))

        saved_items = []

        try:
            with transaction.atomic():
                for product_id in product_ids:
                    product = get_object_or_404(Product, id=str(product_id))
                    saved_item, created = SavedProductItem.objects.get_or_create(
                        user=user
                    )
                    if created:
                        saved_item.save_item(product.id)
                    saved_item.save_item(product.id)

            return Response(custom_response(
                status_mthd=status.HTTP_201_CREATED,
                status="success",
                mssg=f"Items saved successfully: {', '.join(saved_items) or 'No new items saved'}",
                data=SavedItemsSerializer(SavedProductItem.objects.filter(user=user), many=True).data
            ))

        except Exception as e:
            return Response(custom_response(
                status_mthd=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status="error",
                mssg=str(e),
                data=None
            ))

@extend_schema_view(
    get=extend_schema(
        tags=[tag_names["inventory"]],
        operation_id="Retrieve Saved Items",
        description="Fetch all items the authenticated user has saved for later."
    )
)
class GetSavedItemsView(ListAPIView):
    """
    Retrieve all items saved by the authenticated user.
    """
    serializer_class = SavedItemsSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        saved_items = SavedProductItem.objects.filter(user=user)
        serializer = self.get_serializer(saved_items, many=True)
        saved_items_details = []

        for i in saved_items:
            i.get_saved_item_details()
            saved_items_details.append(i.get_saved_item_details())

        return Response(custom_response(
            status_mthd=status.HTTP_200_OK,
            status="success",
            mssg="Saved items retrieved successfully",
            data=saved_items_details
        ))

class DeleteSavedItemView(GenericAPIView):
    """
        Deletes a saved product for the authenticated user
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=[tag_names["inventory"]], operation_id="Delete a saved item")
    def delete(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        user = request.user

        try:
            product = get_object_or_404(Product, id=product_id)
            saved_instance = SavedProductItem.objects.get(user=user)

            if saved_instance.is_item_saved(product):
                saved_instance.remove_item(product)
                return Response(custom_response(
                    status_mthd=status.HTTP_204_NO_CONTENT,
                    status="success",
                    mssg="Item removed from saved list"
                ), status=status.HTTP_204_NO_CONTENT)

            return Response(custom_response(
                status_mthd=status.HTTP_404_NOT_FOUND,
                status="error",
                mssg="Item was not in saved list"
            ), status=status.HTTP_404_NOT_FOUND)

        except SavedProductItem.DoesNotExist:
            return Response(custom_response(
                status_mthd=status.HTTP_404_NOT_FOUND,
                status="error",
                mssg="No saved items for user"
            ), status=status.HTTP_404_NOT_FOUND)

class MarketPlaceProductCreateView(GenericAPIView):
    serializer_class = MarketPlaceProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=[tag_names["marketplace"]], 
        operation_id="Create and upload a product"
    )
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            serializer = self.get_serializer(
                data=data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                custom_response(
                    status_mthd=status.HTTP_201_CREATED,
                    status="success",
                    mssg="Product created successfully",
                    data=serializer.data
                ),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"ERROR: {e}")
            return Response(
                custom_response(
                    status_mthd=status.HTTP_400_BAD_REQUEST,
                    status="error",
                    mssg="Failed to create product: " + str(e),
                    data={}
                ),
                status=status.HTTP_400_BAD_REQUEST
            )

class ListMarketPlaceProductsView(ListAPIView):
    """Lists all products with pagination and filtering."""
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated, CanViewProducts]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["marketplace"]], operation_id="Get all products")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [product.product_profile() for product in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )

        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No products found")

        data = [product.product_profile() for product in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )

class ProvidersMarketPlaceProductListView(GenericAPIView):
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["marketplace"]], operation_id="Get products of a service provider")
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        if not user_id:
            raise exceptions.NotAuthenticated("User not authenticated")

        queryset = MarketPlaceProduct.objects.filter(user=user_id)
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [product.product_profile() for product in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )

        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No products found")

        data = [product.product_profile() for product in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )

class GetProvidersMarketPlaceProductListView(GenericAPIView):
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["marketplace"]], operation_id="Get products of a service provider using their ID")
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        if not user_id:
            raise exceptions.NotAuthenticated("User's ID is required")

        queryset = MarketPlaceProduct.objects.filter(user=user_id)
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [product.product_profile() for product in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )

        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No products found")

        data = [product.product_profile() for product in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )

class MarketPlaceProductDetailView(GenericAPIView):
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated, CanViewProducts]
    lookup_field = 'slug'
    http_method_names = ['get']

    @extend_schema(tags=[tag_names["marketplace"]], operation_id="Get a product's details")
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        try:
            product = MarketPlaceProduct.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Product not found")

        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Product details retrieved successfully",
                data=product.product_profile()
            ),
            status=status.HTTP_200_OK
        )

class MarketPlaceProductUpdateView(UpdateAPIView):
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'slug'
    http_method_names = ['patch']

    @extend_schema(tags=[tag_names["marketplace"]], operation_id="Update a product")    
    def patch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        try:
            product = MarketPlaceProduct.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Product not found")

        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Product updated successfully",
                data=product.product_profile()
            ),
            status=status.HTTP_200_OK
        )

class MarketPlaceProductDeleteView(GenericAPIView):
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    http_method_names = ['delete']

    @extend_schema(tags=[tag_names["marketplace"]], operation_id="Delete a product")
    def delete(self, request, *args, **kwargs):
        id = kwargs.get('id')
        try:
            product = MarketPlaceProduct.objects.get(id=id)
            product.delete()
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Product not found")

        return Response(
            custom_response(
                status_mthd=status.HTTP_204_NO_CONTENT,
                status="success",
                mssg="Product deleted successfully"
            ),
            status=status.HTTP_204_NO_CONTENT
        )

class MarketPlaceProductReviewCreateView(GenericAPIView):
    serializer_class = MarketPlaceProductReviewSerializer
    permission_classes = [IsAuthenticated, CanReviewProducts]

    @extend_schema(
        tags=[tag_names["marketplace"]], 
        operation_id="Create and upload a product review"
    )

    def post(self, request):
        data = request.data
        product = get_object_or_404(MarketPlaceProduct, id=data.get("product"))
        rating = int(data.get("rating"))

        update_marketplace_product_rating(product, request.user, rating)

        return Response({
            "message": "Rating submitted",
            "average_rating": product.total_rating / product.review_count,
            "bayesian_rating": product.bayesian_rating,
            "review_count": product.review_count,
        })

#### ---- TAKA ---- ####
class TakaProductCreateView(GenericAPIView):
    serializer_class = TakaProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=[tag_names["taka"]], 
        operation_id="Create and upload a product"
    )
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            serializer = self.get_serializer(
                data=data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                custom_response(
                    status_mthd=status.HTTP_201_CREATED,
                    status="success",
                    mssg="Product created successfully",
                    data=serializer.data
                ),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                custom_response(
                    status_mthd=status.HTTP_400_BAD_REQUEST,
                    status="error",
                    mssg="Failed to create product",
                    data=str(e)
                ),
                status=status.HTTP_400_BAD_REQUEST
            )

class ListTakaProductsView(ListAPIView):
    """Lists all products with pagination and filtering."""
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated, CanViewProducts]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["taka"]], operation_id="Get all products")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [product.product_profile() for product in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )

        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No products found")

        data = [product.product_profile() for product in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )
class GetProvidersTakaProductListView(GenericAPIView):
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["taka"]], operation_id="Get products of a service provider using their ID")
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        if not user_id:
            raise exceptions.NotAuthenticated("User's ID is required")

        queryset = TakaProduct.objects.filter(user=user_id)
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [product.product_profile() for product in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )

        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No products found")

        data = [product.product_profile() for product in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )
class ProvidersTakaProductListView(GenericAPIView):
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["taka"]], operation_id="Get products of a service provider")
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        if not user_id:
            raise exceptions.NotAuthenticated("User not authenticated")

        queryset = TakaProduct.objects.filter(user=user_id)
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [product.product_profile() for product in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )

        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No products found")

        data = [product.product_profile() for product in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )

class TakaProductDetailView(GenericAPIView):
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    http_method_names = ['get']

    @extend_schema(tags=[tag_names["taka"]], operation_id="Get a product's details")
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        try:
            product = TakaProduct.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Product not found")

        serializer = self.get_serializer(product)

        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Product details retrieved successfully",
                data=product.product_profile()
            ),
            status=status.HTTP_200_OK
        )

class TakaProductUpdateView(UpdateAPIView):
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'slug'
    http_method_names = ['patch']

    @extend_schema(tags=[tag_names["taka"]], operation_id="Update a product")    
    def patch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        try:
            product = TakaProduct.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Product not found")

        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Product updated successfully",
                data=product.product_profile()
            ),
            status=status.HTTP_200_OK
        )

class TakaProductDeleteView(GenericAPIView):
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    http_method_names = ['delete']

    @extend_schema(tags=[tag_names["taka"]], operation_id="Delete a product")
    def delete(self, request, *args, **kwargs):
        id = kwargs.get('id')
        try:
            product = TakaProduct.objects.get(id=id)
            product.delete()
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Product not found")

        return Response(
            custom_response(
                status_mthd=status.HTTP_204_NO_CONTENT,
                status="success",
                mssg="Product deleted successfully",
                data = {}
            ),
            status=status.HTTP_204_NO_CONTENT
        )

class TakaProductReviewCreateView(GenericAPIView):
    serializer_class = TakaProductReviewSerializer
    permission_classes = [IsAuthenticated, CanReviewProducts]

    @extend_schema(
        tags=[tag_names["taka"]], 
        operation_id="Create and upload a product review"
    )

    def post(self, request):
        data = request.data
        product = get_object_or_404(TakaProduct, id=data.get("product"))
        rating = int(data.get("rating"))

        update_taka_product_rating(product, request.user, rating)

        return Response({
            "message": "Rating submitted",
            "average_rating": product.total_rating / product.review_count,
            "bayesian_rating": product.bayesian_rating,
            "review_count": product.review_count,
        })

#### ---- SERVICES ---- ####
class ServiceCreateView(GenericAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=[tag_names["services"]], 
        operation_id="Create and upload a service"
    )
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            serializer = self.get_serializer(
                data=data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                custom_response(
                    status_mthd=status.HTTP_201_CREATED,
                    status="success",
                    mssg="Service created successfully",
                    data=serializer.data
                ),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                custom_response(
                    status_mthd=status.HTTP_400_BAD_REQUEST,
                    status="error",
                    mssg="Failed to create service",
                    data=str(e)
                ),
                status=status.HTTP_400_BAD_REQUEST
            )

class ListServicesView(ListAPIView):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["services"]], operation_id="Get all services")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [service.service_profile() for service in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )

        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No products found")

        data = [service.service_profile() for service in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )

class ProvidersServicesListView(GenericAPIView):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @extend_schema(tags=[tag_names["services"]], operation_id="Get services of a service provider")
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        if not user_id:
            raise exceptions.NotAuthenticated("User not authenticated")
        
        queryset = Service.objects.filter(user=user_id)
        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [service.service_profile() for service in page]
            return self.get_paginated_response(
                custom_response(
                    status_mthd=status.HTTP_200_OK,
                    status="success",
                    mssg="Data retrieved successfully",
                    data=data
                )
            )
        
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            raise exceptions.NotFound("No service found")
        
        data = [service.service_profile() for service in queryset]
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Data retrieved successfully",
                data=data
            ),
            status=status.HTTP_200_OK
        )

class ServiceDetailView(GenericAPIView):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    http_method_names = ["get"]

    @extend_schema(tags=[tag_names["services"]], operation_id="Get a service details")
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        try:
            service = self.queryset.get(slug=slug)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Service not Found")
        
        serializer = self.get_serializer(service)
        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Service detail retrieved successfully",
                data=service.service_profile()
            ),
            status=status.HTTP_200_OK
        )

class ServiceUpdateView(UpdateAPIView):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "slug"
    http_method_names = ["patch"]

    @extend_schema(tags=[tag_names["services"]], operation_id="Update a service")
    def patch(self, request, *args, **kwargs):
        slug = kwargs.get("slug")
        try:
            service = self.queryset.get(slug=slug)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Service not found")
        
        serializer = self.get_serializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Service updated successfully",
                data=service.service_profile()
            ),
            status=status.HTTP_200_OK
        )
    
class ServiceDeleteView(GenericAPIView):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @extend_schema(tags=[tag_names["services"]], operation_id="Delete a service")
    def delete(self, request, *args, **kwargs):
        id = kwargs.get("id")
        try:
            service = self.queryset.get(id=id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Service not found")

        service.delete()
        return Response(
            custom_response(
                status_mthd=status.HTTP_204_NO_CONTENT,
                status="success",
                mssg="Service deleted successfully",
                data=None
            ),
            status=status.HTTP_204_NO_CONTENT
        )