from rest_framework import mixins, viewsets

class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class ListCreateViewSet(mixins.CreateModelMixin, ListViewSet):
    pass
