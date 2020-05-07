from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from app import mySerializer
from app import models
from django.db.models import Q
from rest_framework import status
from app.search_class import search_class


# Create your views here.

class myPageNumberPagination(PageNumberPagination):
    def __init__(self, page_size):
        self.page_size = page_size


class newsListAPI(ModelViewSet):
    queryset = models.NewsTable.objects.all()
    serializer_class = mySerializer.NewsTableSerializerList
    pagination_class = myPageNumberPagination
    page_size = None

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class(self.page_size)
        return self._paginator

    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        if page_size:
            self.page_size = page_size
        else:
            self.page_size = 10

        args = []
        title = request.GET.get('title')
        if title:
            args.append(Q(title__contains=title))
        keyword = request.GET.get('keyword')
        if keyword:
            args.append(Q(keyword__contains=keyword))
        author = request.GET.get('author')
        if author:
            args.append(Q(author__contains=author))
        start_time = request.GET.get('start_time')
        if start_time:
            args.append(Q(get_time__gte=start_time))
        end_time = request.GET.get('end_time')
        if end_time:
            args.append(Q(get_time__lte=end_time))
        sort = request.GET.get('sort')
        if sort:
            queryset = self.filter_queryset(self.get_queryset()).order_by(sort)
        else:
            queryset = self.filter_queryset(self.get_queryset()).order_by('id')
        queryset = queryset.filter(*args)
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        # else:
        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200, "msg": "请求成功", "count": queryset.count(), "datas": serializer.data})


class newsInfoAPI(ModelViewSet):
    queryset = models.NewsTable.objects.all()
    serializer_class = mySerializer.NewsTableSerializer
    pagination_class = PageNumberPagination

    # 查一条
    def get(self, request, *args, **kwargs):
        id = request.GET.get('id')
        obj = self.get_queryset().filter(id=id).first()
        serializer = self.get_serializer(obj)
        return Response({'code': 200, 'msg': '请求成功', 'datas': serializer.data})

    # 创建
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({'code': 200, 'msg': '添加成功'}, status=status.HTTP_201_CREATED, headers=headers)

    # 更新
    def partial_update(self, request, *args, **kwargs):
        id = request.data.get('id')
        obj = self.get_queryset().filter(id=id).first()
        ser_obj = self.get_serializer(instance=obj, data=request.data, partial=True)
        if ser_obj.is_valid():
            ser_obj.save()
        return Response({'code': 200, 'msg': '更新成功'})

    # 删除
    def destroy(self, request, *args, **kwargs):
        ids = request.data.get('ids')
        obj = self.get_queryset().filter(id__in=ids)
        if obj:
            obj.delete()
            return Response({'code': 200, 'msg': '删除成功'})
        else:
            return Response({'code': 400, 'msg': '无删除对象'})


class searchAPI(ModelViewSet):
    queryset = models.NewsTable.objects.all()
    serializer_class = mySerializer.NewsTableSerializerList
    pagination_class = myPageNumberPagination
    page_size = None
    flag = [False]

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class(self.page_size)
        return self._paginator

    # 得到搜索结果
    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        if page_size:
            self.page_size = page_size
        else:
            self.page_size = 10

        args = []
        get_time = request.GET.get('get_time')
        args.append(Q(get_time=str(get_time)))
        queryset = self.filter_queryset(self.get_queryset()).order_by('id')
        queryset = queryset.filter(*args)
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        # else:
        serializer = self.get_serializer(queryset, many=True)
        return Response({'count': queryset.count(), 'datas': serializer.data,'flag':self.flag[0]})

    # 开始搜索
    def start(self, request, *args, **kwargs):
        keys_list = request.data.get('keys_list')
        search_engines = request.data.get('search_engines')
        page_count = request.data.get('page_count')
        get_time = request.data.get('get_time')
        self.flag[0] = True
        self.sc = search_class(keys_list=keys_list, search_engines=search_engines, page_count=page_count,
                               get_time=get_time, flag=self.flag)
        self.sc.start()
        return Response({'code': 200, 'msg': '搜索已开启'}, status=status.HTTP_201_CREATED)

    # 关闭搜索
    def end(self, request, *args, **kwargs):
        self.flag[0] = False
        return Response({'code': 200, 'msg': '搜索已关闭', 'flag': self.flag[0]})
