from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets,mixins,generics
from rest_framework.viewsets import GenericViewSet,ViewSetMixin
from rest_framework.pagination import PageNumberPagination
from web import models
from web.serializers import course_serializers
from web.auth import auth
from web.utils.response import BaseResponse


class CourseView(ViewSetMixin, APIView):

    # authentication_classes = [auth.LuffyAuth,]
    def list(self, request, *args, **kwargs):
        ret = BaseResponse()
        try:
            queryset = models.Course.objects.all()
            serializer = course_serializers.CourseSerializer(instance=queryset, many=True)
            ret.data = serializer .data
        except Exception as e:
            ret.code = 1001
            ret.error = "发生错误"

        return Response(ret.dict)

    def retrieve(self, request, *args, **kwargs):
        ret = {'code': 1000, 'data': None}
        try:
            pk = kwargs.get('pk')
            queryset = models.CourseDetail.objects.filter(id=pk).first()
            serializer = course_serializers.CourseDetailSerializer(instance=queryset, many=False)
            ret['data'] = serializer.data
        except Exception as e:
            ret['code'] = 1001
            ret['error'] = "单条数据发生错误"
        return Response(ret)


class TeacherView(ViewSetMixin, APIView):

    # 获取导师列表
    def list(self, request, *args, **kwargs):
        ret = {'code': 1000, 'data': None}

        try:
            queryset = models.Teacher.objects.all()
            serializer = course_serializers.TeacherSerializer(instance=queryset, many=True)
            ret['data'] = serializer.data
        except Exception as e:
            ret['code'] = 1001
            ret['error'] = "发生错误"
        return Response(ret)


class ScholarshipView(generics.ListAPIView):
    queryset = models.Scholarship.objects.all()
    serializer_class = course_serializers.ScholarshipSerializer

    # def get(self, request, *args, **kwargs):
    #     ret = {'code': 1000, 'data': None}
    #
    #     return self.list(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        ret = {'code': 1000, 'data': serializer.data}
        return Response(ret)


class DegreeCourse(generics.ListAPIView):
    queryset = models.DegreeCourse.objects.all()
    serializer_class = course_serializers.DegreeCourseSerializer

    # def get(self, request, *args, **kwargs):
    #     ret = {'code': 1000, 'data': None}
    #     # print(models.DegreeCourse.objects.all().teachers.all())
    #     return self.list(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        ret = {'code': 1000, 'data': serializer.data}
        return Response(ret)


class OftenAskedQuestion(generics.ListAPIView):
    queryset = models.OftenAskedQuestion.objects.all()
    serializer_class = course_serializers.OftenAskedQuestionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        ret = {'code': 1000, 'data': serializer.data}
        return Response(ret)


class CourseOutLine(generics.ListAPIView):
    queryset = models.CourseOutline.objects.all()
    serializer_class = course_serializers.CourseOutlineSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)  # , context={'request': request} 默认加上
        ret = {'code': 1000, 'data': serializer.data}
        return Response(ret)


class CourseChapter(generics.ListAPIView):
    queryset = models.CourseChapter.objects.all()
    serializer_class = course_serializers.CourseChapterSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)  # , context={'request': request} 默认加上
        ret = {'code': 1000, 'data': serializer.data}
        return Response(ret)




