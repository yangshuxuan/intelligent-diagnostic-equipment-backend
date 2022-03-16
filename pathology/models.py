from uuid import uuid4
from django.contrib import admin
from django.db import models
from django.conf import settings


class Patient(models.Model):
    name = models.CharField(max_length=255,verbose_name="病人姓名")
    sex = models.CharField(max_length=255,verbose_name="性别")
    age = models.PositiveSmallIntegerField(blank=True,null=True,verbose_name="年龄")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = '病人'
        verbose_name_plural = '病人集'

class  PathologyPictureItem(models.Model):
    pathologyPicture = models.ImageField(verbose_name="病理图片",upload_to=settings.ORIGIN_IMAGES_LOCATION)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="图片上传时间")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,verbose_name="患者",related_name='pathologypictures')
    description = models.TextField(blank=True,null=True,verbose_name="图片描述")
    isCutted = models.BooleanField(default=False,verbose_name="是否已经切图")
    def __str__(self) -> str:
        return f"{self.patient}-{self.id}-{self.description}"

    class Meta:
        verbose_name = '病理图片'
        verbose_name_plural = '病理图片集'





class  Diagnosis(models.Model):
    
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="诊断创建时间")

    last_update = models.DateTimeField(auto_now=True,verbose_name="诊断更新时间")
    
    # patient = models.ForeignKey(Patient, on_delete=models.PROTECT,verbose_name="患者",related_name='diagnoses')
    
    

    pathologyPicture = models.ForeignKey(PathologyPictureItem,on_delete=models.PROTECT,verbose_name="病理图片")

    regionPicture = models.ImageField(blank=True,null=True,verbose_name="分子标记物表达图")
    
    high = models.FloatField(default=1.0,verbose_name="高表达概率")
    medium = models.FloatField(default=1.0,verbose_name="中表达概率")
    low = models.FloatField(default=1.0,verbose_name="低表达概率")
    advice = models.TextField(blank=True,null=True,verbose_name="临床意义判读")

    # doctor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,verbose_name="医生")

    doctor_advice = models.TextField(blank=True,null=True,verbose_name="肉眼病理所见")
    

    


    def __str__(self) -> str:
        return f"{self.pathologyPicture.patient.name} ID为{self.id}的诊断"
    
    # @admin.display(description="诊断医生")
    # def doctorNames(self):
    #     return ",".join([ d.username for d in list(self.doctors.all())])
    class Meta:
        verbose_name = '诊断'
        verbose_name_plural = '诊断集'





# class AnalysisItem(models.Model):
    
#     id = models.UUIDField(primary_key=True,default=uuid4)
#     createdAt = models.DateTimeField(auto_now_add=True,verbose_name="分析时间")
#     modifiedAt = models.DateTimeField(auto_now=True,verbose_name="分析更新时间")
#     diagnosisItem = models.ForeignKey(DiagnosisItem,on_delete=models.PROTECT,verbose_name="诊断项",related_name="items")
    
#     regionPicture = models.ImageField(blank=True,null=True,verbose_name="分子标记物表达图")
    
#     high = models.FloatField(default=1.0,verbose_name="高表达概率")
#     medium = models.FloatField(default=1.0,verbose_name="中表达概率")
#     low = models.FloatField(default=1.0,verbose_name="低表达概率")
#     advice = models.TextField(blank=True,null=True,verbose_name="临床意义判读")

#     doctor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,verbose_name="医生")


#     @admin.display(description="诊断ID")
#     def getDiagnosisItem(self):
#         return self.diagnosisItem.id
#     class Meta:
#         verbose_name = '分析'
#         verbose_name_plural = '分析集'


# class Report(models.Model):
    
#     createdAt = models.DateTimeField(auto_now_add=True,verbose_name="报告时间")
#     modifiedAt = models.DateTimeField(auto_now=True,verbose_name="报告更新时间")
#     diagnosis = models.OneToOneField(Diagnosis,on_delete=models.PROTECT,verbose_name="诊断",related_name="report")
#     advice = models.TextField(blank=True,null=True,verbose_name="肉眼病理所见")
#     class Meta:
#         verbose_name = '报告'
#         verbose_name_plural = '报告集'
