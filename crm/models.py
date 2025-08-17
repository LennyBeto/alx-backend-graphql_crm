import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# A custom validator for phone numbers
phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class Customer(models.Model):
    """
    Represents a customer in the CRM system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=17,
        validators=[phone_regex],
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Product(models.Model):
    """
    Represents a product available in the store.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Order(models.Model):
    """
    Represents an order made by a customer.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, related_name="orders", on_delete=models.CASCADE
    )
    products = models.ManyToManyField(Product, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.name}"

    def calculate_total_amount(self, product_ids):
        """
        Calculates the total amount of the order based on the prices
        of the selected products.
        """
        total = 0.00
        for product_id in product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                total += float(product.price)
            except Product.DoesNotExist:
                raise ValidationError(f"Product with ID {product_id} does not exist.")
        self.total_amount = total

    class Meta:
        ordering = ["-order_date"]
