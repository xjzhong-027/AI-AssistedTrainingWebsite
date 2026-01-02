"""
Content management API views.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from common.api.response import Result
from ELW.api.serializers import (
    MediaMaterialSerializer, MainQuestionSerializer, SubQuestionSerializer,
    UnitSerializer, PaperPageSerializer
)
from ELW.services.content_service_impl import ContentServiceImpl
from Account.services.user_service_impl import UserServiceImpl


class MediaMaterialListView(APIView):
    """
    获取媒体素材列表 API
    
    GET /api/v1/content/media-materials/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "title": "string",
                "theme": "string",
                "abstract": "string",
                "keywords": "string",
                "transcript": "string",
                "media_url": "string",
                "image_url": "string"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取媒体素材列表"""
        from ELW.models import MediaMaterial
        materials = MediaMaterial.objects.all().order_by('-id')
        serializer = MediaMaterialSerializer(materials, many=True)
        return Result.success(data=serializer.data, message='success')


class MediaMaterialDetailView(APIView):
    """
    获取媒体素材详情 API
    
    GET /api/v1/content/media-materials/{material_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "title": "string",
            "theme": "string",
            "abstract": "string",
            "keywords": "string",
            "transcript": "string",
            "media_url": "string",
            "image_url": "string"
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, material_id):
        """获取媒体素材详情"""
        material = ContentServiceImpl.get_media_material_by_id(material_id)
        if not material:
            return Result.not_found(message='Media material not found')
        
        serializer = MediaMaterialSerializer(material)
        return Result.success(data=serializer.data, message='success')


class MainQuestionDetailView(APIView):
    """
    获取大题详情 API
    
    GET /api/v1/content/main-questions/{question_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "question_text": "string",
            "question_type": "string",
            "media_material_id": int,
            "media_material_title": "string",
            "sub_questions": [...]
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, question_id):
        """获取大题详情"""
        question = ContentServiceImpl.get_main_question_by_id(question_id)
        if not question:
            return Result.not_found(message='Main question not found')
        
        serializer = MainQuestionSerializer(question)
        return Result.success(data=serializer.data, message='success')


class SubQuestionDetailView(APIView):
    """
    获取小题详情 API
    
    GET /api/v1/content/sub-questions/{sub_question_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "question_text": "string",
            "answer": "string",
            "score": float,
            "question_type": "string",
            "choice_options": [...],
            "matching_options": [...],
            "corrections": [...]
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sub_question_id):
        """获取小题详情"""
        question = ContentServiceImpl.get_sub_question_by_id(sub_question_id)
        if not question:
            return Result.not_found(message='Sub question not found')
        
        serializer = SubQuestionSerializer(question)
        return Result.success(data=serializer.data, message='success')


class UnitListView(APIView):
    """
    获取单元列表 API
    
    GET /api/v1/content/units/
    
    Query Parameters:
    - class_id: 可选，按班级筛选
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "name": "string",
                "type": "string",
                "order": int,
                "class_id": int,
                "class_name": "string",
                "pages": [...]
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取单元列表"""
        class_id = request.query_params.get('class_id')
        
        if class_id:
            units = ContentServiceImpl.get_units_by_class(int(class_id))
        else:
            from ELW.models import Unit
            units = Unit.objects.all().order_by('order', 'id')
        
        serializer = UnitSerializer(units, many=True)
        return Result.success(data=serializer.data, message='success')


class UnitDetailView(APIView):
    """
    获取单元详情 API
    
    GET /api/v1/content/units/{unit_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "name": "string",
            "type": "string",
            "order": int,
            "class_id": int,
            "class_name": "string",
            "pages": [...]
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, unit_id):
        """获取单元详情"""
        unit = ContentServiceImpl.get_unit_by_id(unit_id)
        if not unit:
            return Result.not_found(message='Unit not found')
        
        serializer = UnitSerializer(unit)
        return Result.success(data=serializer.data, message='success')


class PaperPageListView(APIView):
    """
    获取试卷页面列表 API
    
    GET /api/v1/content/pages/
    
    Query Parameters:
    - unit_id: 可选，按单元筛选
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "order": int,
                "title": "string",
                "limited_time": int,
                "unit_id": int,
                "unit_name": "string",
                "main_questions": [...]
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取试卷页面列表"""
        unit_id = request.query_params.get('unit_id')
        
        if unit_id:
            pages = ContentServiceImpl.get_pages_by_unit(int(unit_id))
        else:
            from ELW.models import PaperPage
            pages = PaperPage.objects.all().order_by('order', 'id')
        
        serializer = PaperPageSerializer(pages, many=True)
        return Result.success(data=serializer.data, message='success')


class PaperPageDetailView(APIView):
    """
    获取试卷页面详情 API
    
    GET /api/v1/content/pages/{page_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "order": int,
            "title": "string",
            "limited_time": int,
            "unit_id": int,
            "unit_name": "string",
            "main_questions": [...]
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, page_id):
        """获取试卷页面详情"""
        page = ContentServiceImpl.get_paper_page_by_id(page_id)
        if not page:
            return Result.not_found(message='Paper page not found')
        
        serializer = PaperPageSerializer(page)
        return Result.success(data=serializer.data, message='success')


class UnitPagesView(APIView):
    """
    获取单元的所有页面 API
    
    GET /api/v1/content/units/{unit_id}/pages/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "order": int,
                "title": "string",
                "limited_time": int,
                "unit_id": int,
                "unit_name": "string",
                "main_questions": [...]
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, unit_id):
        """获取单元的所有页面"""
        unit = ContentServiceImpl.get_unit_by_id(unit_id)
        if not unit:
            return Result.not_found(message='Unit not found')
        
        pages = ContentServiceImpl.get_pages_by_unit(unit_id)
        serializer = PaperPageSerializer(pages, many=True)
        return Result.success(data=serializer.data, message='success')


class PageQuestionsView(APIView):
    """
    获取页面的所有大题 API
    
    GET /api/v1/content/pages/{page_id}/questions/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "question_text": "string",
                "question_type": "string",
                "media_material_id": int,
                "media_material_title": "string",
                "sub_questions": [...]
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, page_id):
        """获取页面的所有大题"""
        page = ContentServiceImpl.get_paper_page_by_id(page_id)
        if not page:
            return Result.not_found(message='Paper page not found')
        
        questions = ContentServiceImpl.get_questions_by_page(page_id)
        serializer = MainQuestionSerializer(questions, many=True)
        return Result.success(data=serializer.data, message='success')


class MainQuestionSubQuestionsView(APIView):
    """
    获取大题的所有小题 API
    
    GET /api/v1/content/main-questions/{question_id}/sub-questions/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "question_text": "string",
                "answer": "string",
                "score": float,
                "question_type": "string",
                "choice_options": [...],
                "matching_options": [...],
                "corrections": [...]
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, question_id):
        """获取大题的所有小题"""
        question = ContentServiceImpl.get_main_question_by_id(question_id)
        if not question:
            return Result.not_found(message='Main question not found')
        
        sub_questions = ContentServiceImpl.get_sub_questions_by_main(question_id)
        serializer = SubQuestionSerializer(sub_questions, many=True)
        return Result.success(data=serializer.data, message='success')







