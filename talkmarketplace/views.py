from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from .models import (
    MarketPlaceProduct,
    TakaProduct
)
from .serializers import (
    MarketPlaceProductSerializer, 
    TakaProductSerializer,
    CategorySerializer
    )
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, status
from utils.helpers import custom_response
from drf_yasg.utils import swagger_auto_schema

tag_names = {
    "marketplace":"Marketplace",
    "taka":  "Taka"
    }

class MarketPlaceProductCreateView(GenericAPIView):
    serializer_class = MarketPlaceProductSerializer
    model = MarketPlaceProduct
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(tags=[tag_names["marketplace"]], operation_id="Create and upload a product")

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
        custom_response(
            status_mthd=status.HTTP_200_OK,
            status="success",
            mssg="Data retrieved successfully",
            data=serializer.data
        ),
        status=status.HTTP_200_OK
    )

class ListMarketPlaceProductsView(ListAPIView):
    """Lists all products with pagination and filtering."""
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @swagger_auto_schema(tags=[tag_names["marketplace"]], operation_id="Get all products")
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

    @swagger_auto_schema(tags=[tag_names["marketplace"]], operation_id="Get products of a service provider")
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        if not user_id:
            raise exceptions.NotAuthenticated("User not authenticated")

        queryset = MarketPlaceProduct.objects.filter(service_provider=user_id)
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


class MarketPlaceProductUpdateView(UpdateAPIView):
    serializer_class = MarketPlaceProductSerializer
    queryset = MarketPlaceProduct.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    http_method_names = ['patch']

    @swagger_auto_schema(tags=[tag_names["marketplace"]], operation_id="Update a product")    
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

    @swagger_auto_schema(tags=[tag_names["marketplace"]], operation_id="Delete a product")
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
    model = TakaProduct
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(tags=[tag_names["taka"]], operation_id="Create and upload a product")

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
        custom_response(
            status_mthd=status.HTTP_200_OK,
            status="success",
            mssg="Data retrieved successfully",
            data=serializer.data
        ),
        status=status.HTTP_200_OK
    )

class ListTakaProductsView(ListAPIView):
    """Lists all products with pagination and filtering."""
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @swagger_auto_schema(tags=[tag_names["taka"]], operation_id="Get all products")
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

    @swagger_auto_schema(tags=[tag_names["taka"]], operation_id="Get products of a service provider")
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        if not user_id:
            raise exceptions.NotAuthenticated("User not authenticated")

        queryset = TakaProduct.objects.filter(service_provider=user_id)
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


class TakaProductUpdateView(UpdateAPIView):
    serializer_class = TakaProductSerializer
    queryset = TakaProduct.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    http_method_names = ['patch']

    @swagger_auto_schema(tags=[tag_names["taka"]], operation_id="Update a product")    
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

    @swagger_auto_schema(tags=[tag_names["taka"]], operation_id="Delete a product")
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
                mssg="Product deleted successfully"
            ),
            status=status.HTTP_204_NO_CONTENT
        )