from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Item, ItemImage
from .serializers import ItemSerializer, ItemSingleImageSerializer
from rest_framework.pagination import PageNumberPagination
import os
from django.conf import settings

class ItemPagination(PageNumberPagination):
    page_size = 12


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_item(request):
    try:
        # create item
        item = Item.objects.create(
            title=request.data.get("title"),
            startPrice=request.data.get("startPrice"),
            endPrice=request.data.get("endPrice"),
            description=request.data.get("description"),
            category=request.data.get("category")
        )

        # handle multiple images
        uploaded_images = request.FILES.getlist("images")
        if len(uploaded_images) > 6:
            return Response({"error": "Cannot upload more than 5 images"}, status=status.HTTP_400_BAD_REQUEST)

        for image_file in uploaded_images:
            ItemImage.objects.create(item=item, image=image_file)

        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def get_items(request):
    items = Item.objects.all()
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_item(request, item_id):
    try:
        # Get the item
        item = Item.objects.get(id=item_id)

        # Delete related images from disk
        images = ItemImage.objects.filter(item=item)  # Djongo-safe queryset
        for img in images:
            try:
                if img.image and os.path.isfile(img.image.path):
                    os.remove(img.image.path)
            except Exception as e:
                print(f"Error deleting image file: {e}")

        # Delete images from DB in bulk
        images.delete()

        # Delete the item itself
        item.delete()

        return Response({"message": "Item and images deleted successfully"}, status=status.HTTP_200_OK)

    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT", "PATCH"])
@parser_classes([MultiPartParser, FormParser])
def update_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)

        # update fields
        item.title = request.data.get("title", item.title)
        item.description = request.data.get("description", item.description)
        item.startPrice = request.data.get("startPrice", item.startPrice)
        item.endPrice = request.data.get("endPrice", item.endPrice)
        item.save()

        # delete old images if replace_images flag is true
        if request.data.get("replace_images", "false").lower() == "true":
            for img in item.images.all():
                if img.image and os.path.isfile(img.image.path):
                    os.remove(img.image.path)
                img.delete()

        # handle new images
        uploaded_images = request.FILES.getlist("images")
        total_images_after_upload = item.images.count() + len(uploaded_images)
        if total_images_after_upload > 6:
            return Response({"error": "Total images cannot exceed 5"}, status=status.HTTP_400_BAD_REQUEST)

        for image_file in uploaded_images:
            ItemImage.objects.create(item=item, image=image_file)

        return Response(ItemSerializer(item).data, status=status.HTTP_200_OK)

    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_items_single_image(request):
    items = Item.objects.all()
    paginator = ItemPagination()
    paginated_items = paginator.paginate_queryset(items, request)
    serializer = ItemSingleImageSerializer(paginated_items, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_item_by_id(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        serializer = ItemSerializer(item, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
