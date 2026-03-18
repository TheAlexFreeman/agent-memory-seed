---
source: external-research
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: low
---

# Django + React via Django REST Framework

Covers the Django side of the React/Django stack. React-side patterns are out of scope here.

## Architecture patterns

### Decoupled (most common for React)
Django serves only JSON API. React is a completely separate app (separate repo, separate deploy, served from CDN or Node server). Django handles: authentication, business logic, data, file serving.

### Hybrid (HTMX or partial SPA)
Django serves some HTML (admin, landing pages, simple forms), React components embedded in specific pages via Django template script tags. Less common with modern React tooling.

### Monorepo (single deploy)
`collectstatic` serves the React build from Django's static files. Django handles all routing, React renders within a single HTML template. Simpler to deploy (one Heroku dyno, one Docker container), but tighter coupling.

---

## DRF essentials

```python
# Installation:
pip install djangorestframework

# settings.py:
INSTALLED_APPS = [..., "rest_framework"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}
```

## Serializers

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    order_count = serializers.IntegerField(read_only=True)  # from annotation

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "order_count", "created_at"]
        read_only_fields = ["created_at"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

# Nested serializers:
class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "items", "total", "status"]

# Write-specific serializer (separate from read):
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["user_id", "items"]

    def validate(self, data):
        # Cross-field validation
        ...
        return data

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order
```

## ViewSets

```python
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "user_id"]
    search_fields = ["user__email", "items__product__name"]
    ordering_fields = ["created_at", "total"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).select_related("user").prefetch_related("items__product").annotate(
            item_count=Count("items")
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Router:
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")
urlpatterns = router.urls
```

## Authentication: JWT (djangorestframework-simplejwt)

```python
pip install djangorestframework-simplejwt

# settings.py:
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": SECRET_KEY,  # or dedicated key
}

# urls.py:
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
]
```

On the React side: store the access token in memory (not localStorage), refresh token in httpOnly cookie. Never store JWT in localStorage (XSS risk).

## CORS

```python
pip install django-cors-headers

INSTALLED_APPS = [..., "corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", ...]

# Development:
CORS_ALLOW_ALL_ORIGINS = True

# Production:
CORS_ALLOWED_ORIGINS = [
    "https://app.mysite.com",
]
CORS_ALLOW_CREDENTIALS = True  # required if using cookies for refresh token
```

## API versioning

```python
# URL versioning (clearest):
urlpatterns = [
    path("api/v1/", include("myapp.api.v1.urls")),
    path("api/v2/", include("myapp.api.v2.urls")),
]

# Or via DRF:
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "ALLOWED_VERSIONS": ["v1", "v2"],
}
```

## Performance: optimizing for React frontends

```python
# 1. Use annotations to avoid N+1 on computed fields:
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return Product.objects.annotate(
            avg_rating=Avg("reviews__rating"),
            review_count=Count("reviews"),
        ).prefetch_related("images", "tags")

# 2. Selective field serialization (drf-flex-fields or manual):
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

# 3. Response caching for public endpoints:
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 5), name="list")
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    ...
```

## File uploads

```python
class DocumentUploadView(generics.CreateAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

# Serializer:
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "file", "uploaded_at"]

    def validate_file(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File too large.")
        return value
```

For large files: use pre-signed S3 URLs (upload directly from browser to S3, then notify Django with the S3 key).

## Custom actions on ViewSets

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class OrderViewSet(viewsets.ModelViewSet):
    ...

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != "pending":
            return Response({"error": "Cannot cancel."}, status=400)
        order.status = "cancelled"
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        qs = self.get_queryset().filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        return Response(self.get_serializer(qs, many=True).data)
```

Generates URLs: `POST /orders/{pk}/cancel/` and `GET /orders/recent/`.

## Error handling

```python
# Custom exception handler:
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": True,
            "detail": response.data,
            "status_code": response.status_code,
        }
    return response

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "myapp.utils.custom_exception_handler",
}
```

Last updated: 2026-03-18
