from rest_framework import serializers
from .models import Item, ItemImage

# Serializer for individual images
class ItemImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)  

    class Meta:
        model = ItemImage
        fields = ["image"]

# Serializer for full item with all images
class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True)  # nested serializer

    class Meta:
        model = Item
        fields = ["id", "title", "startPrice", "endPrice", "description", "images", "category"]

# Serializer for item with only the first image
class ItemSingleImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ["id", "title", "startPrice", "endPrice", "description", "image", "category"]

    def get_image(self, obj):
        # safer alternative to avoid ORDER BY in Djongo
        images = obj.images.all()
        if images:
            first_image = images[0]  # no ORDER BY, just takes the first related object
            request = self.context.get("request")
            return (
                request.build_absolute_uri(first_image.image.url)
                if request
                else first_image.image.url
            )
        return None

