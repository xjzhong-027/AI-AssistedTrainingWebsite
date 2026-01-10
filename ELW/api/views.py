"""
Content management API views.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from common.api.response import Result
from ELW.api.serializers import (
    MediaMaterialSerializer, MainQuestionSerializer, SubQuestionSerializer,
    UnitSerializer, PaperPageSerializer
)
from ELW.services.content_service_impl import ContentServiceImpl
from Account.services.user_service_impl import UserServiceImpl


@extend_schema(tags=['内容管理'])
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


@extend_schema(tags=['内容管理'])
class MediaMaterialQuestionsView(APIView):
    """
    获取媒体素材关联的所有大题 API
    
    GET /api/v1/content/media-materials/{material_id}/questions/
    
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
    
    def get(self, request, material_id):
        """获取媒体素材关联的所有大题"""
        questions = ContentServiceImpl.get_main_questions_by_material(material_id)
        serializer = MainQuestionSerializer(questions, many=True)
        return Result.success(data=serializer.data, message='success')


@extend_schema(tags=['内容管理'])
class MediaMaterialDetailView(APIView):
    """
    媒体素材详情 API
    
    GET /api/v1/content/media-materials/{material_id}/ - 获取媒体素材详情
    DELETE /api/v1/content/media-materials/{material_id}/ - 删除媒体素材
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary='获取媒体素材详情',
        description='根据ID获取媒体素材的详细信息',
        responses={
            200: {
                'description': '成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'success',
                            'data': {
                                'id': 1,
                                'title': '示例标题',
                                'theme': '主题',
                                'abstract': '摘要',
                                'keywords': '关键词',
                                'transcript': '文本内容',
                                'media_url': '/media/example.mp3',
                                'image_url': '/media/example.jpg'
                            }
                        }
                    }
                }
            },
            404: {'description': '媒体素材不存在'}
        }
    )
    def get(self, request, material_id):
        """获取媒体素材详情"""
        material = ContentServiceImpl.get_media_material_by_id(material_id)
        if not material:
            return Result.not_found(message='Media material not found')
        
        serializer = MediaMaterialSerializer(material)
        return Result.success(data=serializer.data, message='success')
    
    @extend_schema(
        summary='删除媒体素材',
        description='删除指定的媒体素材，删除后将无法恢复',
        responses={
            200: {
                'description': '删除成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'Media material deleted successfully',
                            'data': None
                        }
                    }
                }
            },
            404: {'description': '媒体素材不存在'},
            500: {'description': '删除失败'}
        }
    )
    def delete(self, request, material_id):
        """删除媒体素材"""
        material = ContentServiceImpl.get_media_material_by_id(material_id)
        if not material:
            return Result.not_found(message='Media material not found')
        
        try:
            success = ContentServiceImpl.delete_media_material(material_id)
            if success:
                return Result.success(message='Media material deleted successfully')
            else:
                return Result.error(message='Failed to delete media material', code=500)
        except Exception as e:
            return Result.error(message=f'Failed to delete media material: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
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


@extend_schema(tags=['内容管理'])
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


@extend_schema(tags=['内容管理'])
class UnitListView(APIView):
    """
    获取单元列表 API
    
    GET /api/v1/content/units/ - 获取单元列表
    POST /api/v1/content/units/ - 创建单元（任务包）
    
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
    
    @extend_schema(
        summary='创建单元',
        description='创建新的单元（任务包）',
        responses={
            200: {
                'description': '创建成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'Unit created successfully',
                            'data': {
                                'id': 1,
                                'title': '单元名称',
                                'type': 'exam',
                                'order': 1,
                                'class_id': 1,
                                'class_name': '班级名称',
                                'pages': []
                            }
                        }
                    }
                }
            },
            400: {'description': '参数错误'}
        }
    )
    def post(self, request):
        """创建单元（任务包）"""
        try:
            data = request.data
            class_id = data.get('class_id')
            if not class_id:
                return Result.error(message='class_id is required', code=400)
            
            unit = ContentServiceImpl.create_unit(class_id, data)
            serializer = UnitSerializer(unit)
            return Result.success(data=serializer.data, message='Unit created successfully')
        except Exception as e:
            return Result.error(message=f'Failed to create unit: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
class UnitDetailView(APIView):
    """
    单元详情 API
    
    GET /api/v1/content/units/{unit_id}/ - 获取单元详情
    PUT /api/v1/content/units/{unit_id}/ - 更新单元（考试/练习）
    DELETE /api/v1/content/units/{unit_id}/ - 删除单元（考试/练习）
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary='获取单元详情',
        description='根据ID获取单元（考试/练习）的详细信息',
        responses={
            200: {
                'description': '成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'success',
                            'data': {
                                'id': 1,
                                'title': '单元名称',
                                'type': 'exam',
                                'order': 1,
                                'class_id': 1,
                                'class_name': '班级名称',
                                'pages': []
                            }
                        }
                    }
                }
            },
            404: {'description': '单元不存在'}
        }
    )
    def get(self, request, unit_id):
        """获取单元详情"""
        unit = ContentServiceImpl.get_unit_by_id(unit_id)
        if not unit:
            return Result.not_found(message='Unit not found')
        
        serializer = UnitSerializer(unit)
        return Result.success(data=serializer.data, message='success')
    
    @extend_schema(
        summary='更新单元',
        description='更新指定的单元（考试/练习）信息',
        responses={
            200: {
                'description': '更新成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'Unit updated successfully',
                            'data': {
                                'id': 1,
                                'title': '单元名称',
                                'type': 'exam',
                                'order': 1,
                                'class_id': 1,
                                'class_name': '班级名称',
                                'pages': []
                            }
                        }
                    }
                }
            },
            404: {'description': '单元不存在'},
            500: {'description': '更新失败'}
        }
    )
    def put(self, request, unit_id):
        """更新单元（考试/练习）"""
        unit = ContentServiceImpl.get_unit_by_id(unit_id)
        if not unit:
            return Result.not_found(message='Unit not found')
        
        try:
            data = request.data
            updated_unit = ContentServiceImpl.update_unit(unit_id, data)
            if updated_unit:
                serializer = UnitSerializer(updated_unit)
                return Result.success(data=serializer.data, message='Unit updated successfully')
            else:
                return Result.error(message='Failed to update unit', code=500)
        except Exception as e:
            return Result.error(message=f'Failed to update unit: {str(e)}', code=500)
    
    @extend_schema(
        summary='删除单元',
        description='删除指定的单元（考试/练习），删除后将无法恢复，且会删除所有相关的页面和题目',
        responses={
            200: {
                'description': '删除成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'Unit deleted successfully',
                            'data': None
                        }
                    }
                }
            },
            404: {'description': '单元不存在'},
            500: {'description': '删除失败'}
        }
    )
    def delete(self, request, unit_id):
        """删除单元（考试/练习）"""
        unit = ContentServiceImpl.get_unit_by_id(unit_id)
        if not unit:
            return Result.not_found(message='Unit not found')
        
        try:
            success = ContentServiceImpl.delete_unit(unit_id)
            if success:
                return Result.success(message='Unit deleted successfully')
            else:
                return Result.error(message='Failed to delete unit', code=500)
        except Exception as e:
            return Result.error(message=f'Failed to delete unit: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
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
    
    @extend_schema(
        summary='创建试卷页面',
        description='创建新的试卷页面并关联题目',
        responses={
            200: {
                'description': '创建成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'Paper page created successfully',
                            'data': {
                                'id': 1,
                                'order': 1,
                                'title': '页面标题',
                                'limited_time': 60,
                                'unit_id': 1,
                                'unit_name': '单元名称',
                                'main_questions': []
                            }
                        }
                    }
                }
            },
            400: {'description': '参数错误'}
        }
    )
    def post(self, request):
        """创建试卷页面并关联题目"""
        try:
            data = request.data
            unit_id = data.get('unit_id')
            if not unit_id:
                return Result.error(message='unit_id is required', code=400)
            
            # 创建页面
            page_data = {
                'order': data.get('order', 1),
                'text': data.get('text', ''),
                'can_modify': data.get('can_modify', False),
                'limited_time': data.get('limited_time')
            }
            page = ContentServiceImpl.create_paper_page(unit_id, page_data)
            
            # 关联题目
            main_question_ids = data.get('main_question_ids', [])
            if main_question_ids:
                ContentServiceImpl.associate_questions_to_page(page.id, main_question_ids)
            
            serializer = PaperPageSerializer(page)
            return Result.success(data=serializer.data, message='Paper page created successfully')
        except Exception as e:
            return Result.error(message=f'Failed to create paper page: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
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


@extend_schema(tags=['内容管理'])
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


@extend_schema(tags=['内容管理'])
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


@extend_schema(tags=['内容管理'])
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









