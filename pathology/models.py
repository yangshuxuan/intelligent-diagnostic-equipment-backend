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
    pathologyPicture = models.FileField(verbose_name="病理图片",upload_to=settings.ORIGIN_IMAGES_LOCATION)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="图片上传时间")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,verbose_name="患者",related_name='pathologypictures')
    description = models.TextField(verbose_name="图片描述")
    isCutted = models.BooleanField(default=False,verbose_name="是否已经切图")
    def __str__(self) -> str:
        return f"{self.patient}-{self.id}-{self.description}"

    class Meta:
        verbose_name = '病理图片'
        verbose_name_plural = '病理图片集'





class  Diagnosis(models.Model):
    
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="诊断创建时间")

    last_update = models.DateTimeField(auto_now=True,verbose_name="诊断更新时间")
    
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT,verbose_name="患者",related_name='diagnoses')
    
    doctors = models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name="医生")
    
    description = models.TextField(blank=True,null=True,verbose_name="诊断描述")

    isFinished = models.BooleanField(default=False,verbose_name="诊断是否完成")

    def __str__(self) -> str:
        return f"{self.patient.name} ID为{self.id}的诊断"
    
    @admin.display(description="诊断医生")
    def doctorNames(self):
        return ",".join([ d.username for d in list(self.doctors.all())])
    class Meta:
        verbose_name = '诊断'
        verbose_name_plural = '诊断集'


class  DiagnosisItem(models.Model):
    """
    每个诊断至少有一张图片
    """

    
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="诊断项创建时间")

    last_update = models.DateTimeField(auto_now=True,verbose_name="诊断项更新时间")

    diagnosis = models.ForeignKey(Diagnosis,on_delete=models.PROTECT,verbose_name="诊断",related_name="items")

    pathologyPicture = models.ForeignKey(PathologyPictureItem,on_delete=models.PROTECT,verbose_name="病理图片")
    
    def __str__(self) -> str:
        return f"第{self.id}诊断项"
    class Meta:
        verbose_name = '诊断项'
        verbose_name_plural = '诊断项集'


class LabelItem(models.Model):
    MUSHROOM = 'M'
    CATEGORY_CHOICES = [
        (MUSHROOM, '真菌'),
        ("TR",  "阴道滴虫" ),
        ("AM",  "放线菌" ),
        ("CL",  "线索细胞" ),
        ("CMV",  "巨细胞病毒" ),
        ("HSV",  "疱疹病毒" ),
        ("IM",  "炎症" ),
        ("S",  "萎缩" ),
        ("ASC-US",  "非典型鳞状细胞意义不明" ),
        ("ASC-H",  "非典型鳞状细胞不除外上皮高度病" ),
        ("AGC(NSL)-CC",  "非典型腺细胞(无具体指向)宫颈管" ),
        ("AGC(NSL)-E",  "非典型腺细胞(无具体指向)宫内膜" ),
        ("AGC(NSL)-US",  "非典型腺细胞(无具体指向)不能确定来源" ),
        ("LSIL",  "鳞状上皮内低度病变" ),
        ("AGC(FN)-CC",  "非典型腺细胞(倾向瘤变)宫颈管" ),
        ("AGC(FN)-US",  "非典型腺细胞(倾向瘤变)不能确定来源" ),
        ("HSIL",  "鳞状上皮内高度病变" ),
        ("AIS",  "颈管原位癌" ),
        ("SCC",  "鳞状细胞癌" ),
        ("GC-CC",  "腺癌宫颈管" ),
        ("GC-E",  "腺癌宫内膜" ),
        ("GC-OT",  "腺癌其他" )
    ]
    id = models.UUIDField(primary_key=True,default=uuid4)
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="标注时间")
    modifiedAt = models.DateTimeField(auto_now=True,verbose_name="标注更新时间")
    diagnosisItem = models.ForeignKey(DiagnosisItem,on_delete=models.PROTECT,verbose_name="诊断项",related_name="items")
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default=MUSHROOM,verbose_name="类别")
    x = models.FloatField(verbose_name="标注起点坐标X")
    y = models.FloatField(verbose_name="标注起点坐标Y")
    w = models.FloatField(verbose_name="标注宽度")
    h = models.FloatField(verbose_name="标注高度")
    zoomLevel = models.FloatField(default=10.0,verbose_name="标注时放大倍数")
    regionPicture = models.ImageField(blank=True,null=True,verbose_name="标注区域图")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,verbose_name="医生")
    confidence = models.FloatField(default=1.0,verbose_name="自信度")
    
    @admin.display(description="诊断ID")
    def getDiagnosisItem(self):
        return self.diagnosisItem.id
    class Meta:
        verbose_name = '标注'
        verbose_name_plural = '标注集'

class Report(models.Model):
    
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name="报告时间")
    modifiedAt = models.DateTimeField(auto_now=True,verbose_name="报告更新时间")
    diagnosis = models.OneToOneField(Diagnosis,on_delete=models.PROTECT,verbose_name="诊断",related_name="report")
    labelitems = models.ManyToManyField(LabelItem,blank=True,verbose_name="标注")
    manyi = models.BooleanField(default=False,verbose_name="满意")
    jinguanxibao = models.BooleanField(default=False,verbose_name="颈管细胞")
    huashengxibao = models.BooleanField(default=False,verbose_name="化生细胞")
    bumanyi = models.BooleanField(default=False,verbose_name="不满意")
    M=models.BooleanField(default=False,verbose_name= '真菌')
    TR=models.BooleanField(default=False,verbose_name=  "阴道滴虫" )
    AM=models.BooleanField(default=False,verbose_name=  "放线菌" )
    CL=models.BooleanField(default=False,verbose_name=  "线索细胞" )
    CMV=models.BooleanField(default=False,verbose_name=  "巨细胞病毒" )
    HSV=models.BooleanField(default=False,verbose_name=  "疱疹病毒" )
    IM=models.BooleanField(default=False,verbose_name=  "炎症" )#10
    S=models.BooleanField(default=False,verbose_name=  "萎缩" )#11
    ASC_US=models.BooleanField(default=False,verbose_name=  "非典型鳞状细胞意义不明" )
    ASC_H=models.BooleanField(default=False,verbose_name=  "非典型鳞状细胞不除外上皮高度病" )
    AGC_NSL_CC=models.BooleanField(default=False,verbose_name=  "非典型腺细胞(无具体指向)宫颈管" )#14
    AGC_NSL_E=models.BooleanField(default=False,verbose_name=  "非典型腺细胞(无具体指向)宫内膜" )#15
    AGC_NSL_US=models.BooleanField(default=False,verbose_name=  "非典型腺细胞(无具体指向)不能确定来源" )
    LSIL=models.BooleanField(default=False,verbose_name=  "鳞状上皮内低度病变" )#17
    AGC_FN_CC=models.BooleanField(default=False,verbose_name=  "非典型腺细胞(倾向瘤变)宫颈管" )#18
    AGC_FN_US=models.BooleanField(default=False,verbose_name=  "非典型腺细胞(倾向瘤变)不能确定来源" )#19
    HSIL=models.BooleanField(default=False,verbose_name=  "鳞状上皮内高度病变" )#20
    AIS=models.BooleanField(default=False,verbose_name=  "颈管原位癌" )#21
    SCC=models.BooleanField(default=False,verbose_name=  "鳞状细胞癌" )#22
    GC_CC=models.BooleanField(default=False,verbose_name=  "腺癌宫颈管" )
    GC_E=models.BooleanField(default=False,verbose_name=  "腺癌宫内膜" )
    GC_OT=models.BooleanField(default=False,verbose_name=  "腺癌其他" )
    OTHER=models.BooleanField(default=False,verbose_name=  "其他恶性肿瘤" )
    advice = models.TextField(blank=True,null=True,verbose_name="诊断意见")
    class Meta:
        verbose_name = '报告'
        verbose_name_plural = '报告集'
