from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from .models import (
    Product,
    MarketPlaceProduct,
    TakaProduct,
    SavedItem,
    Service
)
from .serializers import (
    MarketPlaceProductSerializer, 
    TakaProductSerializer,
    SavedItemsSerializer,
    ServiceSerializer
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, status
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from utils.helpers import custom_response
from drf_spectacular.utils import extend_schema

tag_names = {
    "marketplace": "Marketplace",
    "taka": "Taka",
    "services": "Services",
    "inventory": "Inventory",
}

class SaveItemView(GenericAPIView):
    """
        Handles users item savings
    """
    serializer_class = SavedItemsSerializer
    permission_classes = [IsAuthenticated]
    @extend_schema(tags=[tag_names["inventory"]], operation_id="Save an item for later")

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        user = request.user
        try:
            product = get_object_or_404(Product, id=product_id)
            instance, created = SavedItem.objects.get_or_create(user=user)
            if created:
                instance.save_item(product=product_id)
            return Response(custom_response(
                status_mthd=status.HTTP_201_CREATED,
                status="success",
                mssg="Item added successfully",
                data=str(e)
            ))
        except Exception as e:
            return Response(custom_response(
                status_mthd=status.HTTP_400_BAD_REQUEST,
                status="error",
                mssg="Failed to save item",
                data=str(e)
            ), status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(custom_response(
                status_mthd=status.HTTP_404_NOT_FOUND,
                status="error",
                mssg="Product not found",
                data=None
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
            return Response(
                custom_response(
                    status_mthd=status.HTTP_400_BAD_REQUEST,
                    status="error",
                    mssg="Failed to create product",
                    data=str(e)
                ),
                status=status.HTTP_400_BAD_REQUEST
            )



class ListMarketPlaceProductsView(ListAPIView):
    """Lists all products with pagination and filtering."""
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
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

class MarketPlaceProductDetailView(GenericAPIView):
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
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
                data=serializer.data
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
    permission_classes = [IsAuthenticated]
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
                data=serializer.data
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
                data=serializer.data
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
                data=serializer.data
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
                data=serializer.data
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
