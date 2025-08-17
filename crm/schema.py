import graphene
import re
import django_filters
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# === Object Types ===
# These classes define the GraphQL types based on your Django models.

class CustomerType(DjangoObjectType):
    """ GraphQL type for the Customer model. """
    class Meta:
        model = Customer
        filter_fields = ["name", "email", "phone"]
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    """ GraphQL type for the Product model. """
    class Meta:
        model = Product
        filter_fields = ["name", "price", "stock"]
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    """ GraphQL type for the Order model. """
    class Meta:
        model = Order
        filter_fields = ["total_amount", "order_date"]
        interfaces = (graphene.relay.Node,)


# === Inputs for Mutations ===
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)


# === Mutations ===
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input=None):
        name = input.name
        email = input.email
        phone = input.phone

        try:
            validate_email(email)
        except ValidationError:
            raise Exception("Invalid email address format.")

        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")

        if phone and not re.match(r"^\+?\d{9,15}$", phone):
            raise Exception("Invalid phone number format. Must be +999999999 up to 15 digits.")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        
        return CreateCustomer(customer=customer, message="Customer created successfully!")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        created_customers = []
        validation_errors = []

        for customer_data in input:
            try:
                name = customer_data.get('name')
                email = customer_data.get('email')
                phone = customer_data.get('phone')

                if not name:
                    raise ValidationError("Name is required.")
                if not email:
                    raise ValidationError("Email is required.")
                
                try:
                    validate_email(email)
                except ValidationError:
                    raise ValidationError(f"Invalid email address format for {email}.")

                if Customer.objects.filter(email=email).exists():
                    raise ValidationError(f"Email '{email}' already exists.")
                
                if phone and not re.match(r"^\+?\d{9,15}$", phone):
                    raise ValidationError(f"Invalid phone number format for '{phone}'.")

                customer = Customer.objects.create(**customer_data)
                created_customers.append(customer)

            except ValidationError as e:
                validation_errors.append(f"Validation error for {customer_data.get('email', 'unknown email')}: {e.message}")
            
        return BulkCreateCustomers(customers=created_customers, errors=validation_errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input=None):
        name = input.name
        price = input.price
        stock = input.stock

        if price <= 0:
            raise Exception("Price must be a positive number.")
        if stock is not None and stock < 0:
            raise Exception("Stock cannot be a negative number.")

        product = Product.objects.create(name=name, price=price, stock=stock or 0)
        
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    
    @staticmethod
    def mutate(root, info, input=None):
        customer_id = input.customer_id
        product_ids = input.product_ids
        
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer with the given ID does not exist.")

        if not product_ids:
            raise Exception("An order must contain at least one product.")
        
        order = Order(customer=customer)
        
        order.calculate_total_amount(product_ids)
        order.save()
        
        products = Product.objects.filter(pk__in=product_ids)
        order.products.set(products)
        
        return CreateOrder(order=order)


# === Query and Mutation Classes ===

class Query(graphene.ObjectType):
    """
    This class defines all the available queries for your GraphQL API.
    It uses DjangoFilterConnectionField to enable filtering and pagination.
    """
    # Filterable queries
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter,
        order_by=graphene.String()
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter,
        order_by=graphene.String()
    )

    # Resolve methods for ordering
    def resolve_all_products(self, info, **kwargs):
        queryset = Product.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            return queryset.order_by(order_by)
        return queryset

    def resolve_all_orders(self, info, **kwargs):
        queryset = Order.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            return queryset.order_by(order_by)
        return queryset


class Mutation(graphene.ObjectType):
    """
    This class brings together all your defined mutation classes.
    """
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
