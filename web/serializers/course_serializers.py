from rest_framework import serializers
from web import models


class CourseSerializer(serializers.ModelSerializer):
    level = serializers.CharField(source='get_level_display')

    degree_course = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id','name','course_img','level', 'degree_course']
        # fields = "__all__"

    def get_degree_course(self, obj):

        return '%s' % str(obj.degree_course)


class CourseDetailSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.name')
    class Meta:
        model = models.CourseDetail
        fields = ['id','hours','course_slogan','video_brief_link', 'course']
        # fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Teacher
        fields = "__all__"


class ScholarshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Scholarship
        fields = "__all__"


class DegreeCourseSerializer(serializers.ModelSerializer):

    # 获取讲师列表
    teachers = serializers.SerializerMethodField()

    class Meta:
        model = models.DegreeCourse
        # fields = ['teachers']
        fields = "__all__"

    def get_teachers(self, obj):
        queryset = obj.teachers.all()

        return [{'id': row.id, 'name': row.name} for row in queryset ]


class OftenAskedQuestionSerializer(serializers.ModelSerializer):

    # 序列化 常见问题
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = models.OftenAskedQuestion
        fields = "__all__"

    def get_content_type(self, obj):
        queryset = obj.content_object
        # 1.在价格策略表中添加一条数据
        # models.PricePolicy.objects.create(
        #     valid_period=7,
        #     price=6.6,
        #     content_type=ContentType.objects.get(model='course'),
        #     object_id=1
        # )

        # models.PricePolicy.objects.create(
        #     valid_period=14,
        #     price=9.9,
        #     content_object=models.Course.objects.get(id=1)
        # )

        # 2. 根据某个价格策略对象，找到他对应的表和数据，如：管理课程名称
        # price = models.PricePolicy.objects.get(id=2)
        # print(price.content_object.name) # 自动帮你找到

        # 3.找到某个课程关联的所有价格策略
        # obj = models.Course.objects.get(id=1)
        # for item in obj.policy_list.all():
        #     print(item.id,item.valid_period,item.price)
        #
        return queryset.name


class CourseOutlineSerializer(serializers.ModelSerializer):

    course_name = serializers.CharField(source='course_detail.course.name')
    course_detail_id = serializers.CharField(source='course_detail.pk')
    # course_detail = serializers.HyperlinkedIdentityField(
    #     view_name='course_detail',
    #     lookup_field='course_detail_id',
    #     lookup_url_kwarg="pk",
    # )
    class Meta:
        model = models.CourseOutline
        fields = ['id', 'order', 'title', 'content', 'course_name', 'course_detail_id']


class CourseChapterSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.name')

    class Meta:
        model = models.CourseChapter
        fields = "__all__"


class CourseSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CourseSection
        fields = "__all__"





