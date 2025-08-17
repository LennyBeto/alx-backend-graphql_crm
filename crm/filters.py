import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    """
    A filter set for the Customer model, allowing filtering by
    name, email, and phone number pattern.
    """
    # Case-insensitive partial match for name
    name = django_filters.CharFilter(lookup_expr="icontains")

    # Case-insensitive partial match for email
    email = django_filters.CharFilter(lookup_expr="icontains")

    # Custom filter to match phone numbers with a specific pattern
    phone_pattern = django_filters.CharFilter(
        method="filter_by_phone_pattern",
        label="Phone number starts with a specific pattern"
    )

    def filter_by_phone_pattern(self, queryset, name, value):
        """
        Custom method to filter customers by a phone number pattern
        using a regular expression.
        """
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = ["name", "email"]
        
        
class ProductFilter(django_filters.FilterSet):
    """
    A filter set for the Product model, allowing filtering by
    name, price range, and stock range.
    """
    # Case-insensitive partial match for name
    name = django_filters.CharFilter(lookup_expr="icontains")

    # Price range filter
    price_gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    
    # Stock range filter
    stock_gte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock_lte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["name", "price", "stock"]


class OrderFilter(django_filters.FilterSet):
    """
    A filter set for the Order model, allowing filtering by
    customer name, product name, total amount, and order date.
    """
    # Filter orders by customer name using a related field lookup
    customer_name = django_filters.CharFilter(
        field_name="customer__name",
        lookup_expr="icontains"
    )
    
    # Filter orders by product name using a related field lookup
    product_name = django_filters.CharFilter(
        field_name="products__name",
        lookup_expr="icontains"
    )

    # Filter orders by total amount range
    total_amount_gte = django_filters.NumberFilter(
        field_name="total_amount",
        lookup_expr="gte"
    )
    total_amount_lte = django_filters.NumberFilter(
        field_name="total_amount",
        lookup_expr="lte"
    )
    
    # Filter orders by a specific product ID
    product_id = django_filters.UUIDFilter(field_name="products__id")

    class Meta:
        model = Order
        fields = ["customer_name", "product_name", "total_amount"]
