
from django.shortcuts import get_object_or_404
import xml.etree.ElementTree as ET
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination

from pathology.tasks import readImageDzi
from .models import PathologyPictureItem,Diagnosis
from .serializers import PathologyPictureItemSerializer,DiagnosisSerializer,DiagnosisPatchSerializer
from rest_framework.decorators import action

from urllib.parse import urlparse
from django.utils.encoding import escape_uri_path
from django.db.models import Q
from .tasks import readRegionImage

from django.conf import settings
from  django.http import HttpResponse
from io import BytesIO
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path,PurePosixPath
from django_filters.rest_framework import DjangoFilterBackend
from docxtpl import DocxTemplate, InlineImage,RichText

# for height and width you have to use millimeters (Mm), inches or points(Pt) class :
from docx.shared import Mm
import jinja2
# Create your views here.

class PathologyPictureItemViewSet(ModelViewSet):
    queryset = PathologyPictureItem.objects.all()
    serializer_class = PathologyPictureItemSerializer

class DiagnosisViewSet(ModelViewSet):
    # queryset = Diagnosis.objects.select_related("patient").prefetch_related("items__pathologyPicture").all()
    serializer_class = DiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = LimitOffsetPagination
    filterset_fields = ['isFinished']
    def get_serializer_class(self):
        if self.request.method=="PATCH":
            return DiagnosisPatchSerializer
        else:
            return DiagnosisSerializer
    def get_queryset(self):
        user = self.request.user
        queryset = Diagnosis.objects.select_related("patient").prefetch_related("items__pathologyPicture")
        if not user.is_anonymous :
            queryset = queryset.filter(Q(doctors=user)) 
        return queryset
# class DiagnosisItemViewSet(ModelViewSet):
#     queryset = DiagnosisItem.objects.all()
#     serializer_class = DiagnosisItemSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['pathologyPicture__id']
#     @action(detail=True)
#     def image_detail(self,request,pk):
#         pathologyPictureItem = DiagnosisItem.objects.get(pk=pk).pathologyPicture
#         pathologyPicture = pathologyPictureItem.pathologyPicture
#         dzi = f"{Path(pathologyPicture.name).stem}.dzi"
#         v =  (settings.MEDIA_ROOT/pathologyPicture.name).parent/dzi
#         tree = ET.parse(v)
#         root = tree.getroot()
#         o=urlparse(f"{pathologyPicture.url}")

#         fileName = f"{PurePosixPath(pathologyPicture.name).stem}_files"
#         remoteCuttedFiles = str(PurePosixPath(pathologyPicture.url).parent/fileName)
#         # remoteCuttedFiles=str(Path(settings.AWS_LOCATION,settings.CUTTED_IMAGES_LOCATION) / f"{fileName}_files")
#         url = o._replace(path=str( f"{remoteCuttedFiles}/")).geturl()

#         # url = Path(pathologyPicture.url).parent/fileName

#         data = {
#             "Image": {
#                 "xmlns": "http://schemas.microsoft.com/deepzoom/2009",
#                 "Url": str(url),
#                 "Overlap": root.get("Overlap"),
#                 "TileSize": root.get("TileSize"),
#                 "Format": root.get("Format"),
#                 "Size": {
#                     "Height": root[0].get('Height'),
#                     "Width": root[0].get('Width'),
#                 },
#             }
#         }
        
#         return Response(data)


# class LabelItemViewSet(ModelViewSet):
#     serializer_class = LabelItemSerializer
#     def get_queryset(self):
#         diagnosisItem = get_object_or_404(DiagnosisItem,pk=self.kwargs["diagnosisitem_pk"])
#         others = self.request.query_params.get('others')
#         if others == 'true':
#             return LabelItem.objects.filter(
#                 diagnosisItem__pathologyPicture__id=diagnosisItem.pathologyPicture.id
#                 ).exclude(diagnosisItem_id=self.kwargs["diagnosisitem_pk"])
#         return LabelItem.objects.filter(diagnosisItem_id=self.kwargs["diagnosisitem_pk"])
        
#     def get_serializer_context(self):
        
#         return {"diagnosisitem_pk":self.kwargs["diagnosisitem_pk"],"doctor":self.request.user}
# class ReportViewSet(ModelViewSet):
#     queryset = Report.objects.all()
#     serializer_class = ReportSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['diagnosis_id']
    # def get_serializer_class(self):
    #     if self.request.method=="PATCH":
    #         return ReportPatchSerializer
    #     else:
    #         return ReportSerializer
def checkedElement():
    elm = OxmlElement('w:checked')
    elm.set(qn('w:val'),"true")
    return elm
def generateDocument(request):
    diagnosisId = request.GET.get("diagnosis__id")
    
    diagnosis = get_object_or_404(Diagnosis, pk=diagnosisId)
    
    docx_title=f"{diagnosis.pathologyPicture.patient.name}诊断报告.docx"
    tpl = DocxTemplate(settings.BASE_DIR / 'template.docx')
    
    context = {
        'doctor_advice':diagnosis.doctor_advice,
        "high":diagnosis.high,
        "medium":diagnosis.medium,
        "low":diagnosis.low,
        "advice":diagnosis.advice,
        'regionPicture':InlineImage(tpl, diagnosis.regionPicture.path, height=Mm(60)),
        'pathologyPicture':InlineImage(tpl, diagnosis.pathologyPicture.pathologyPicture.path, height=Mm(60))
        
    }
    jinja_env = jinja2.Environment(autoescape=True)
    tpl.render(context, jinja_env)

    # Prepare document for download        
    # -----------------------------
    f = BytesIO()
    tpl.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename={escape_uri_path(docx_title)}'
    response['Content-Length'] = length
    return response
