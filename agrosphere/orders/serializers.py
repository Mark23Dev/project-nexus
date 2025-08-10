from rest_framework import serializers
from .models import Order, OrderItem, Product
from products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price_at_purchase', 'total_price']
        read_only_fields = ['id', 'price_at_purchase', 'total_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Delay import to avoid circular imports
        from products.models import Product
        self.fields['product_id'].queryset = Product.objects.filter(available=True)

    def get_total_price(self, obj):
        return obj.total_price()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)  # email or username

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'shipping_address', 'billing_address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data.get('quantity', 1)

            # Take a snapshot of price at purchase time
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )

        order.update_total_price()
        return order

    def update(self, instance, validated_data):
        # Disallow status and total_price updates here; status changes via separate workflow
        items_data = validated_data.pop('items', None)
        if items_data:
            instance.items.all().delete()  # simple approach; or do smarter diff update

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data.get('quantity', 1)

                OrderItem.objects.create(
                    order=instance,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )

        # Update addresses if provided
        instance.shipping_address = validated_data.get('shipping_address', instance.shipping_address)
        instance.billing_address = validated_data.get('billing_address', instance.billing_address)

        instance.save()
        instance.update_total_price()
        return instance
