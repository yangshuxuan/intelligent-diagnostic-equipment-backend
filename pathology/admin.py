import os
from django.contrib import admin

from django.conf import settings
from django.apps import apps
from django.db.models.aggregates import Count

from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.utils.safestring import mark_safe
from . import models


admin.site.site_header = "病理辅助诊断工作站"
admin.site.site_title = "病理辅助诊断"


@admin.register(models.PathologyPictureItem)
class PathologyPictureAdmin(admin.ModelAdmin):
    list_display = ['id','show_patient','diagnoses','createdAt','pathologyPicture']
    autocomplete_fields = ['patient']
    ordering = ['createdAt']
    list_per_page = 10
    list_select_related = ['patient']
    search_fields = ['description']

    @admin.display(description="智能诊断")
    def diagnoses(self, pathologyPicture):
        url = (
            reverse('admin:pathology_diagnosis_changelist')
            + '?'
            + urlencode({
                'pathologyPicture__id': str(pathologyPicture.id)
            }))
        return format_html('<a href="{}"><img src="{}pathology/finger.svg" width="25" height="20" alt="诊断"></a>', url,settings.STATIC_URL)

    
    @admin.display(description="患者")
    def show_patient(self, pathologyPictureItem):
        url = (
            reverse('admin:pathology_patient_changelist')
            + '?'
            + urlencode({
                'id': str(pathologyPictureItem.patient.id)
            }))
        return format_html('<a href="{}">{}</a>', url, pathologyPictureItem.patient.name)
 

class DiagnosisInline(admin.StackedInline):
    model = models.Diagnosis

    fields = ("doctors", "description")

    filter_horizontal = (
        'doctors',
    )
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "doctors":
            kwargs["queryset"] = apps.get_model(settings.AUTH_USER_MODEL).objects.filter(groups__name='普通医生')
        
        field = super(DiagnosisInline, self).formfield_for_manytomany(db_field, request, **kwargs)
        
        return field
    extra = 0



@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name','pathologypicture_count',
    # 'diagnoses_count',
    'sex','age']
    # inlines = [DiagnosisInline]
    search_fields = ['name']

    # @admin.display(ordering='diagnoses_count',description="诊断数")
    # def diagnoses_count(self, patient):
    #     url = (
    #         reverse('admin:pathology_diagnosis_changelist')
    #         + '?'
    #         + urlencode({
    #             'patient__id': str(patient.id)
    #         }))
    #     return format_html('<a href="{}">{} 诊断</a>', url, patient.diagnoses_count)
    @admin.display(ordering='pathologypicture_count',description="病理图片数")
    def pathologypicture_count(self, patient):
        url = (
            reverse('admin:pathology_pathologypictureitem_changelist')
            + '?'
            + urlencode({
                'patient__id': str(patient.id)
            }))
        return format_html('<a href="{}">{} 病理图片</a>', url, patient.pathologypicture_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            pathologypicture_count=Count('pathologypictures',distinct=True))
        # 'pathologypicture_count',,pathologypicture_count=Count('pathologypictures')
        
    

# @admin.register(models.LabelItem)
# class LabelItemAdmin(admin.ModelAdmin):
#     list_display = ['id','getDiagnosisItem','x','y','w','h','category','doctor_name','confidence','showRegionPicture']
#     @admin.display(description="医生")
#     def doctor_name(self, labelItem):
#         return labelItem.doctor.username
#     @admin.display(description="标注区域图")
#     def showRegionPicture(self, labelItem):
#         # return mark_safe('<img src="{url}" />'.format(url = labelItem.regionPicture.url)
#         width = 50
#         # if obj and obj.pathologyPicture  and obj.pathologyPicture.size <= 10 *1024 * 1024  :
#         return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
#             url = labelItem.regionPicture.url,
#             width=width,
#             height=1.0 * labelItem.regionPicture.height/labelItem.regionPicture.width * width,
#         )
#     )

# class DiagnosisItemInline(admin.TabularInline):
#     autocomplete_fields = ['pathologyPicture']
#     min_num = 1
#     max_num = 10
#     model = models.DiagnosisItem
#     extra = 0
@admin.register(models.Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    # autocomplete_fields = ['patient']
    readonly_fields = ["headshot_pathologyPicture","headshot_regionPicture"]
    fieldsets = (
        ('诊断输入', {
            'fields': ( 'headshot_pathologyPicture',),
            # 'classes': ('extrapretty',),
        }),
        ('智能分析结果', {
            'fields': ('headshot_regionPicture',('high', 'medium','low'), 'advice',),
            # 'classes': ('extrapretty',),
        }),
        ('医生诊断意见', {
            'fields': ( 'doctor_advice',),
            # 'classes': ('extrapretty',),
        }),
        

    )
    list_display = ['id',
    'show_patient',
    # 'doctorNames',
    # 'diagnosisitem_count',
    # 'show_report',
    # 'isFinished',
    "generateDignoseDoc",
    "showPathologyPicture",
    "showRegionPicture",
    'last_update',
    'createdAt'
    ]
    @admin.display(description="病理图片")
    def showPathologyPicture(self,obj):
        if obj and obj.pathologyPicture:
            
            return format_html('<a href="{}"  target="_blank">{}</a>',
            obj.pathologyPicture.pathologyPicture.url,
            os.path.basename(obj.pathologyPicture.pathologyPicture.name))
        else:
            return None
    @admin.display(description="分子标记物表达图")
    def showRegionPicture(self,obj):
        if obj and obj.regionPicture:
            
            return format_html('<a href="{}"  target="_blank">{}</a>',
            obj.regionPicture.url,
            os.path.basename(obj.regionPicture.name))
        else:
            return None
    def makeImgUrl(self,image):
        width = 400
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                url = image.url,
                width=width,
                height=1.0 * image.height/image.width * width,
            ))

    @admin.display(description="病理图片")
    def headshot_pathologyPicture(self, obj):
        

        if obj and obj.pathologyPicture  and obj.pathologyPicture.pathologyPicture.size <= 100 *1024 * 1024:
            
            return self.makeImgUrl(obj.pathologyPicture.pathologyPicture)
    
    @admin.display(description="分子标记物表达图")
    def headshot_regionPicture(self, obj):
        

        if obj and obj.regionPicture  and obj.regionPicture.size <= 100 *1024 * 1024:
            
            return self.makeImgUrl(obj.regionPicture)

    @admin.display(description="诊断报告")
    def generateDignoseDoc(self,diagnosis):
        base_url = "/pathology/generatedoc"
        query_string =  urlencode({'diagnosis__id': diagnosis.id})  
        url = '{}?{}'.format(base_url, query_string)
        return format_html('<a href="{}"><img src="{}pathology/explorer.svg" width="25" height="20" alt="浏览"></a>',url,settings.STATIC_URL)    

    # inlines = [DiagnosisItemInline]
    # search_fields = ['patient__name']
    # @admin.display(description="报告ID")
    # def show_report(self, diagnosis):
    #     url = (
    #         reverse('admin:pathology_report_changelist')
    #         + '?'
    #         + urlencode({
    #             'id': str(diagnosis.report.id)
    #         }))
    #     return format_html('<a href="{}">{}</a>', url, diagnosis.report.id)
    @admin.display(description="患者")
    def show_patient(self, diagnosis):
        url = (
            reverse('admin:pathology_patient_changelist')
            + '?'
            + urlencode({
                'id': str(diagnosis.pathologyPicture.patient.id)
            }))
        return format_html('<a href="{}">{}</a>', url, diagnosis.pathologyPicture.patient.name)

    # filter_horizontal = (
    #     'doctors',
    # )
    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "doctors":
    #         kwargs["queryset"] = apps.get_model(settings.AUTH_USER_MODEL).objects.filter(groups__name='普通医生')
        
    #     field = super(DiagnosisAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
        
    #     return field
    # @admin.display(ordering='diagnoses_count',description="诊断项数")
    # def diagnosisitem_count(self, diagnosis):
    #     url = (
    #         reverse('admin:pathology_diagnosisitem_changelist')
    #         + '?'
    #         + urlencode({
    #             'diagnosis__id': str(diagnosis.id)
    #         }))
    #     return format_html('<a href="{}">{} 诊断项</a>', url, diagnosis.diagnosisitem_count)

    # def get_queryset(self, request):
    #     return super().get_queryset(request).annotate(
    #         diagnosisitem_count=Count('items')
    #     )

# @admin.register(models.DiagnosisItem)
# class DiagnosisItemAdmin(admin.ModelAdmin):
#     list_display = ['id','show_diagnosis','show_pathologyPicture','labelitem_count','last_update','createdAt']
#     @admin.display(description="病理图片ID")
#     def show_pathologyPicture(self, diagnosisItem):
#         url = (
#             reverse('admin:pathology_pathologypictureitem_changelist')
#             + '?'
#             + urlencode({
#                 'id': str(diagnosisItem.pathologyPicture.id)
#             }))
#         return format_html('<a href="{}">{}</a>', url, diagnosisItem.pathologyPicture.id)
#     @admin.display(description="诊断ID")
#     def show_diagnosis(self, diagnosisItem):
#         url = (
#             reverse('admin:pathology_diagnosis_changelist')
#             + '?'
#             + urlencode({
#                 'id': str(diagnosisItem.diagnosis.id)
#             }))
#         return format_html('<a href="{}">{}</a>', url, diagnosisItem.diagnosis.id)
#     @admin.display(ordering='labelitem_count',description="标注项数")
#     def labelitem_count(self, diagnosisItem):
#         url = (
#             reverse('admin:pathology_labelitem_changelist')
#             + '?'
#             + urlencode({
#                 'diagnosisItem__id': str(diagnosisItem.id)
#             }))
#         return format_html('<a href="{}">{} 标注项</a>', url, diagnosisItem.labelitem_count)

#     def get_queryset(self, request):
#         return super().get_queryset(request).annotate(
#             labelitem_count=Count('items')
#         )
    
# @admin.register(models.Report)
# class ReportAdmin(admin.ModelAdmin):
#     list_display = ['id','show_diagnosis','generateDignoseDoc','modifiedAt','createdAt']
#     filter_horizontal = (
#         'labelitems',
#     )
#     @admin.display(description="诊断报告")
#     def generateDignoseDoc(self,report):
#         base_url = "/pathology/generatedoc"
#         query_string =  urlencode({'report__id': report.id})  
#         url = '{}?{}'.format(base_url, query_string)
#         return format_html('<a href="{}"><img src="{}pathology/explorer.svg" width="25" height="20" alt="浏览"></a>',url,settings.STATIC_URL)    

#     @admin.display(description="诊断ID")
#     def show_diagnosis(self, report):
#         url = (
#             reverse('admin:pathology_diagnosis_changelist')
#             + '?'
#             + urlencode({
#                 'id': str(report.diagnosis.id)
#             }))
#         return format_html('<a href="{}">{}</a>', url, report.diagnosis.id)