from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from .models import Item, UserItem, Categories
from .serializers import ItemSerializer, UserItemSerializer, CateSerializer

class CateViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CateSerializer

    @action(detail=True)
    def items(self, request, *args, **kwargs):
        cate = self.get_object()
        serializer = ItemSerializer(cate.items.all(), many=True)
        return Response(serializer.data)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['POST'])
    def purchase(self, request, *args, **kwargs):
        item = self.get_object()
        user = request.user
        if item.price > user.point:
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        user.point -= item.price
        user.save()
        try:
            user_item = UserItem.objects.get(user=user, item=item)
        except UserItem.DoesNotExist:
            user_item = UserItem(user=user, item=item)
        user_item.count += 1
        user_item.save()

        serializer = UserItemSerializer(user.items.all(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='purchase')
    @transaction.atomic()
    def purchase_items(selfs, request, *args, **kwargs):
        items = request.data['items']
        user = request.user

        sid = transaction.savepoint()
        for i in items:
            item = Item.objects.get(id=i['item_id'])
            count = int(i['count'])

            if item.price * count > user.point:
                transaction.savepoint_rollback(sid)
                return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
            user.point -= item.price
            user.save()
            try:
                user_item = UserItem.objects.get(user=user, item=item)
            except UserItem.DoesNotExist:
                user_item = UserItem(user=user, item=item)
            user_item.count += count
            user_item.save()
        transaction.savepoint_commit(sid)
        serializer = UserItemSerializer(user.items.all(), many=True)
        return Response(serializer.data)
