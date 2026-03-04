"""
Content management API views.
"""
import os
from django.http import HttpResponseRedirect
from django.conf import settings
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
    
    @extend_schema(
        summary='创建媒体素材',
        description='新建一条媒体素材（标题、主题、摘要、原文等）',
        request=MediaMaterialSerializer,
        responses={
            200: {'description': '创建成功', 'content': {'application/json': {'example': {'code': 200, 'message': 'success', 'data': {'id': 1, 'title': '...'}}}}},
            400: {'description': '参数错误'}
        }
    )
    def post(self, request):
        """创建媒体素材"""
        try:
            data = request.data
            material = ContentServiceImpl.create_media_material({
                'title': data.get('title', ''),
                'theme': data.get('theme', ''),
                'abstract': data.get('abstract', ''),
                'keywords': data.get('keywords', ''),
                'transcript': data.get('transcript', ''),
                'media_url': data.get('media_url', ''),
                'image_url': data.get('image_url', ''),
            })
            serializer = MediaMaterialSerializer(material)
            return Result.success(data=serializer.data, message='创建成功')
        except Exception as e:
            return Result.error(message=f'创建失败: {str(e)}', code=400)


@extend_schema(tags=['内容管理'])
class MediaMaterialQuestionsView(APIView):
    """
    获取媒体素材关联的所有大题 API
    
    GET /api/v1/content/media-materials/{material_id}/questions/ - 列表
    POST /api/v1/content/media-materials/{material_id}/questions/ - 创建一道大题（含小题与选项）
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, material_id):
        """获取媒体素材关联的所有大题"""
        questions = ContentServiceImpl.get_main_questions_by_material(material_id)
        serializer = MainQuestionSerializer(questions, many=True)
        return Result.success(data=serializer.data, message='success')
    
    @extend_schema(
        summary='在媒体素材下创建题目',
        description='创建一道大题，含小题；选择题需传 options，连线题传 matching_options，改错题传 corrections',
        request=None,
        responses={200: {'description': '创建成功'}, 400: {'description': '参数错误'}, 404: {'description': '素材不存在'}}
    )
    def post(self, request, material_id):
        """创建大题及小题、选项"""
        from ELW.models import MainQuestion, SubQuestion, ChoiceOption, MatchingOption, Correction
        material = ContentServiceImpl.get_media_material_by_id(material_id)
        if not material:
            return Result.not_found(message='Media material not found')
        data = request.data
        question_type = data.get('question_type', 'choice')
        main_data = {
            'question_type': question_type,
            'question_text': data.get('question_text', ''),
            'maximum_play': data.get('maximum_play', 3),
            'minimum_play': data.get('minimum_play', 0),
            'no_media': data.get('no_media', False),
        }
        try:
            main_question = ContentServiceImpl.create_main_question(material_id, main_data)
        except ValueError as e:
            return Result.error(message=str(e), code=400)
        sub_questions_payload = data.get('sub_questions') or []
        for sub in sub_questions_payload:
            sub_data = {
                'question_text': sub.get('question_text', ''),
                'answer': sub.get('answer', ''),
                'score': float(sub.get('score', 1.0)),
                'tips': sub.get('tips') or '',
                'analysis': sub.get('analysis') or '',
            }
            try:
                sub_question = ContentServiceImpl.create_sub_question(main_question.id, sub_data)
            except ValueError as e:
                return Result.error(message=str(e), code=400)
            if question_type == 'choice':
                for idx, opt in enumerate(sub.get('options') or []):
                    label = (str(opt.get('option_label', '')).strip() or
                             chr(65 + (idx % 26)))
                    ChoiceOption.objects.create(
                        sub_question=sub_question,
                        option_label=label,
                        option_content=opt.get('option_content', ''),
                        is_answer=bool(opt.get('is_answer', False)),
                    )
            elif question_type == 'matching':
                for opt in sub.get('matching_options') or []:
                    MatchingOption.objects.create(
                        sub_question=sub_question,
                        option_label=str(opt.get('option_label', '')).strip() or 'A',
                        option_content=opt.get('option_content', ''),
                    )
            elif question_type == 'correction':
                for corr in sub.get('corrections') or []:
                    Correction.objects.create(
                        sub_question=sub_question,
                        type=corr.get('type', 'insert'),
                        index=int(corr.get('index', 0)),
                    )
        main_question.refresh_from_db()
        serializer = MainQuestionSerializer(main_question)
        return Result.success(data=serializer.data, message='题目创建成功')


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
class MediaMaterialUploadMediaView(APIView):
    """
    上传媒体文件（音频/视频），返回可存入 media_url 的相对路径。
    POST /api/v1/content/media-materials/upload-media/
    Content-Type: multipart/form-data, file: 媒体文件
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from ELW.services.file_service_impl import FileServiceImpl
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Result.error(message='请选择媒体文件', code=400)
        try:
            file_path, _ = FileServiceImpl.upload_media_file(file_obj, file_type='media')
            relative = os.path.relpath(file_path, settings.MEDIA_ROOT).replace('\\', '/')
            return Result.success(data={'media_url': relative}, message='上传成功')
        except Exception as e:
            return Result.error(message=f'上传失败: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
class MediaMaterialUploadImageView(APIView):
    """
    上传图片，返回可存入 image_url 的相对路径。
    POST /api/v1/content/media-materials/upload-image/
    Content-Type: multipart/form-data, file: 图片文件
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from ELW.services.file_service_impl import FileServiceImpl
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Result.error(message='请选择图片文件', code=400)
        try:
            url_list = FileServiceImpl.upload_image_files([file_obj])
            if not url_list:
                return Result.error(message='上传失败', code=500)
            # 返回相对 MEDIA_ROOT 的路径，便于存入 DB
            raw = url_list[0].replace('\\', '/')
            if raw.startswith('media_material/'):
                relative = raw[len('media_material/'):]
            else:
                relative = raw
            return Result.success(data={'image_url': relative}, message='上传成功')
        except Exception as e:
            return Result.error(message=f'上传失败: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
class MediaMaterialMediaView(APIView):
    """
    获取媒体素材的音频/视频文件 URL（重定向到实际文件）
    GET /api/v1/content/media-materials/{material_id}/media/
    若素材已设置 media_url，则 302 重定向到可播放的地址；否则 404。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, material_id):
        material = ContentServiceImpl.get_media_material_by_id(material_id)
        if not material:
            return Result.not_found(message='Media material not found')
        if not (getattr(material, 'media_url', None) or '').strip():
            return Result.error(message='该素材未设置媒体文件地址', code=404)
        media_url = (material.media_url or '').strip().lstrip('/')
        base = (settings.MEDIA_URL or '/media_material/').rstrip('/')
        path = f"{base}/{media_url}"
        redirect_url = request.build_absolute_uri(path)
        return HttpResponseRedirect(redirect_url)


@extend_schema(tags=['内容管理'])
class TranscribeMediaView(APIView):
    """
    使用 Whisper 将音频/视频转为文字（transcript）。
    POST /api/v1/content/transcribe-media/
    Content-Type: multipart/form-data, file: 媒体文件
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='语音识别提取 transcript',
        description='上传音频/视频文件，使用 Whisper 转为文字。需安装 openai-whisper 和 FFmpeg。',
        request={'multipart/form-data': {'type': 'object', 'properties': {'file': {'type': 'string', 'format': 'binary'}}}},
        responses={
            200: {'description': '成功', 'content': {'application/json': {'example': {'code': 200, 'message': 'success', 'data': {'transcript': '...'}}}}},
            400: {'description': '未选择文件'}, 500: {'description': '识别失败'}
        }
    )
    def post(self, request):
        from ELW.services.file_service_impl import FileServiceImpl
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Result.error(message='请选择媒体文件', code=400)
        try:
            file_path, file_url = FileServiceImpl.upload_media_file(file_obj, file_type='media')
            relative = os.path.relpath(file_path, settings.MEDIA_ROOT).replace('\\', '/')
            from AI_module.ASR_from_Whisper import ASR_from_Whisper
            asr = ASR_from_Whisper()
            transcript = asr.transcribe_audio(file_path, language='en')
            return Result.success(data={'transcript': transcript, 'media_url': relative}, message='语音识别完成')
        except ImportError as e:
            return Result.error(message=f'请安装 openai-whisper: pip install openai-whisper', code=500)
        except Exception as e:
            return Result.error(message=f'语音识别失败: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
class AnalyzeMaterialView(APIView):
    """
    根据 transcript 解析 title、theme、abstract、keywords。
    POST /api/v1/content/analyze-material/
    Body: { "transcript": "..." }
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='AI 智能分析素材',
        description='根据 transcript 解析标题、主题、摘要、关键词',
        request={'application/json': {'schema': {'type': 'object', 'properties': {'transcript': {'type': 'string'}}, 'required': ['transcript']}}},
        responses={
            200: {'description': '成功', 'content': {'application/json': {'example': {'code': 200, 'data': {'title': '...', 'theme': '...', 'abstract': '...', 'keywords': '...'}}}}},
            400: {'description': 'transcript 为空'}, 500: {'description': '分析失败'}
        }
    )
    def post(self, request):
        transcript = (request.data.get('transcript') or '').strip()
        if not transcript:
            return Result.error(message='请提供 transcript 内容', code=400)
        try:
            from AI_module.Get_from_AI import Get_from_AI
            import json
            import re
            ai = Get_from_AI()
            ai.set_prompt_variables(my_key='transcript', my_value=transcript, mode='update')
            prompt = ai.get_prompt('素材分析')
            raw = ai.get_answer(prompt)
            # 解析 JSON 输出
            match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(raw)
            return Result.success(data={
                'title': data.get('title', ''),
                'theme': data.get('theme', ''),
                'abstract': data.get('abstract', ''),
                'keywords': data.get('keywords', ''),
            }, message='分析完成')
        except json.JSONDecodeError as e:
            return Result.error(message=f'AI 返回格式解析失败: {str(e)}', code=500)
        except Exception as e:
            return Result.error(message=f'分析失败: {str(e)}', code=500)


@extend_schema(tags=['内容管理'])
class BatchImportChoicesView(APIView):
    """
    批量导入选择题到指定素材。
    POST /api/v1/content/media-materials/{material_id}/batch-import-choices/
    Body: { "questions": [{ "question_text", "option_A", "option_B", "option_C", "option_D", "correct_answer", "score" }] }
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='批量导入选择题',
        description='按格式批量导入选择题到素材，每道题一个大题。Body: { "questions": [{ "question_text", "option_A", "option_B", "option_C", "option_D", "correct_answer", "score" }] }',
        request={'application/json': {'schema': {'type': 'object', 'properties': {'questions': {'type': 'array', 'items': {'type': 'object'}}}, 'required': ['questions']}}},
        responses={
            200: {'description': '成功'}, 400: {'description': '参数错误'}, 404: {'description': '素材不存在'}
        }
    )
    def post(self, request, material_id):
        from ELW.models import MainQuestion, SubQuestion, ChoiceOption
        material = ContentServiceImpl.get_media_material_by_id(material_id)
        if not material:
            return Result.not_found(message='素材不存在')
        questions = request.data.get('questions') or []
        if not questions:
            return Result.error(message='请提供 questions 数组', code=400)
        created = 0
        for q in questions:
            qt = (q.get('question_text') or '').strip()
            oa, ob, oc, od = (q.get('option_A') or '').strip(), (q.get('option_B') or '').strip(), (q.get('option_C') or '').strip(), (q.get('option_D') or '').strip()
            ans = (q.get('correct_answer') or 'A').strip().upper()
            if ans not in ('A', 'B', 'C', 'D'):
                ans = 'A'
            sc = float(q.get('score', 1.0))
            if not qt or not all([oa, ob, oc, od]):
                continue
            main = ContentServiceImpl.create_main_question(material_id, {
                'question_type': 'choice',
                'question_text': qt,
                'maximum_play': 3,
                'minimum_play': 0,
                'no_media': False,
            })
            sub = ContentServiceImpl.create_sub_question(main.id, {
                'question_text': qt,
                'answer': ans,
                'score': sc,
                'tips': '',
                'analysis': '',
            })
            for label, content in [('A', oa), ('B', ob), ('C', oc), ('D', od)]:
                ChoiceOption.objects.create(
                    sub_question=sub,
                    option_label=label,
                    option_content=content,
                    is_answer=(label == ans),
                )
            created += 1
        return Result.success(data={'count': created}, message=f'成功导入 {created} 道选择题')


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
        from ELW.models import Unit, TimeManagement
        from datetime import datetime, date
        from Account.models import Students

        class_id = request.query_params.get('class_id')
        unit_type = request.query_params.get('unit_type')

        if class_id:
            units = ContentServiceImpl.get_units_by_class(int(class_id))
        else:
            units = Unit.objects.all().order_by('order', 'id')

        if unit_type:
            units = units.filter(type=unit_type)

        # 学生端按开放周次过滤
        student = None
        if hasattr(request, 'user') and hasattr(request.user, 'students'):
            try:
                student = request.user.students
            except Students.DoesNotExist:
                pass
        if not student and hasattr(request, 'user') and request.user:
            student = Students.objects.filter(user=request.user).first()

        if student and student.class_instance_id and unit_type == 'practice':
            if not class_id:
                units = units.filter(class_instance_id=student.class_instance_id)
            class_obj = student.class_instance
            start_date_str = getattr(class_obj, 'start_date', None) or ''
            current_week = None
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str[:10], '%Y-%m-%d').date()
                    today = date.today()
                    current_week = max(1, (today - start_date).days // 7 + 1)
                except (ValueError, TypeError):
                    pass
            if current_week is not None:
                unit_ids_future = set(
                    TimeManagement.objects.filter(unit__in=units, week__gt=current_week)
                    .values_list('unit_id', flat=True)
                )
                units = units.exclude(id__in=unit_ids_future)

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


@extend_schema(tags=['周任务管理'])
class WeekTaskPackageCreateView(APIView):
    """
    创建周任务包 API

    POST /api/v1/content/week-task-packages/

    Headers:
    Authorization: Bearer <access_token>
    Content-Type: multipart/form-data

    Request Body (multipart/form-data):
    - title: string (required) - 任务标题
    - theme: string (optional) - 主题
    - abstract: string (optional) - 摘要
    - keywords: string (optional) - 关键词
    - transcript: string (optional) - 文本内容
    - media_file: file (required) - 媒体文件（音频/视频）
    - image_file: file[] (optional) - 图片文件（可多个）

    Response:
    {
        "code": 200,
        "message": "Week task package created successfully",
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

    @extend_schema(
        summary='创建周任务包',
        description='创建新的周任务包，包含媒体素材和图片',
        responses={
            200: {
                'description': '创建成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': 'Week task package created successfully',
                            'data': {
                                'id': 1,
                                'title': '任务包标题',
                                'theme': '主题',
                                'abstract': '摘要',
                                'keywords': '关键词',
                                'transcript': '文本内容',
                                'media_url': '/media/...',
                                'image_url': '/media/...'
                            }
                        }
                    }
                }
            },
            400: {'description': '参数错误或缺少必填字段'},
            500: {'description': '创建失败'}
        }
    )
    def post(self, request):
        """创建周任务包"""
        try:
            from ELW.services.file_service_impl import FileServiceImpl
            from ELW.models import MediaMaterial

            # 检查必填字段
            media_file = request.FILES.get('media_file')
            if not media_file:
                return Result.error(message='请上传媒体文件（音频/视频）', code=400)

            # 上传媒体文件
            media_file_path, media_url = FileServiceImpl.upload_media_file(media_file, file_type='media')

            # 上传图片文件
            image_files = request.FILES.getlist('image_file')
            image_urls = ''
            if image_files:
                image_url_list = FileServiceImpl.upload_image_files(image_files)
                image_urls = ','.join(image_url_list)
                if image_urls:
                    image_urls += ','

            # 创建MediaMaterial对象
            new_task_package = MediaMaterial.objects.create(
                title=request.data.get('title', ''),
                theme=request.data.get('theme', ''),
                abstract=request.data.get('abstract', ''),
                keywords=request.data.get('keywords', ''),
                transcript=request.data.get('transcript', ''),
                media_url=media_url,
                image_url=image_urls,
            )

            serializer = MediaMaterialSerializer(new_task_package)
            return Result.success(data=serializer.data, message='Week task package created successfully')
        except Exception as e:
            return Result.error(message=f'Failed to create week task package: {str(e)}', code=500)


@extend_schema(tags=['周任务管理'])
class WeekTaskImportView(APIView):
    """
    导入周任务Word文档 API

    POST /api/v1/content/week-task-import/

    Headers:
    Authorization: Bearer <access_token>
    Content-Type: multipart/form-data

    Request Body:
    - word_file: file (required) - Word文档(.docx格式)
    - material_id: int (required) - 素材包ID

    Response:
    {
        "code": 200,
        "message": "Document parsed successfully",
        "data": {
            "question_data": [...]
        }
    }
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='导入Word文档',
        description='上传并解析Word文档，提取题目信息',
        responses={
            200: {'description': '解析成功'},
            400: {'description': '参数错误或文件格式错误'},
            500: {'description': '解析失败'}
        }
    )
    def post(self, request):
        """导入Word文档并解析"""
        try:
            from io import BytesIO
            from docx import Document
            from ELW.models import MediaMaterial
            import ELW.doc_page_func as doc_page_func
            import re

            word_file = request.FILES.get('word_file')
            material_id = request.data.get('material_id')

            if not word_file:
                return Result.error(message='请上传Word文档', code=400)

            if not material_id:
                return Result.error(message='缺少素材包ID', code=400)

            # 验证文件扩展名
            if not word_file.name.lower().endswith('.docx'):
                return Result.error(
                    message='请上传有效的Word文档（仅支持.docx格式）',
                    code=400
                )

            # 验证素材包是否存在
            try:
                media_material = MediaMaterial.objects.get(pk=material_id)
            except MediaMaterial.DoesNotExist:
                return Result.error(message='素材包不存在', code=404)

            # 提取文本内容
            def extract_text_from_word(doc_file):
                try:
                    file_content = doc_file.read()
                    doc_file.seek(0)
                    docx_file = BytesIO(file_content)
                    doc = Document(docx_file)

                    text = ''
                    for para in doc.paragraphs:
                        text += para.text + '\n'
                    return text
                except Exception as e:
                    error_msg = str(e)
                    if 'Content_Types' in error_msg or 'not a zip file' in error_msg.lower():
                        raise ValueError(
                            '无法读取Word文档。请确保：1) 文件是有效的.docx格式（不是.doc格式）；'
                            '2) 文件没有损坏。如果您有.doc格式的文件，请在Word中打开并另存为.docx格式。'
                        )
                    else:
                        raise ValueError(f'无法读取Word文档: {error_msg}')

            text_content = extract_text_from_word(word_file)
            question_data = doc_page_func.main_process(text_content)

            # 获取图片路径根目录
            img_directory = ""
            if media_material.image_url:
                first_path = media_material.image_url.split(',')[0]
                match = re.match(r"(.+[/\\])[^/\\]+$", first_path)
                if match:
                    img_directory = match.group(1)

            # 处理题目数据
            for page_question in question_data:
                # 将页面限制时间转为分钟
                hours, minutes, seconds = map(int, page_question['limited_time'].split(':'))
                page_question['limited_time'] = int(hours * 60 + minutes + seconds / 60)

                for main_question in page_question['page_content']:
                    main_question['media_material_id'] = material_id
                    main_question['img_directory'] = img_directory

                    if main_question['question_type'] == 'correction':
                        for sub_question in main_question['sub_questions']:
                            sub_question['questions'] = []
                            for i in range(len(sub_question['sub_list'])):
                                sub_question['questions'].append({
                                    'sub': sub_question['sub_list'][i],
                                    'type': sub_question['type_list'][i],
                                    'answer': sub_question['answer_list'][i],
                                    'index': sub_question['index_list'][i]
                                })

            return Result.success(
                data={'question_data': question_data},
                message='Document parsed successfully'
            )
        except ValueError as e:
            return Result.error(message=str(e), code=400)
        except Exception as e:
            return Result.error(message=f'Failed to parse document: {str(e)}', code=500)


@extend_schema(tags=['周任务管理'])
class WeekTaskSaveView(APIView):
    """
    保存周任务 API

    POST /api/v1/content/week-task-save/

    Headers:
    Authorization: Bearer <access_token>

    Request Body:
    {
        "title": "string",
        "class_id": int,
        "type": "task|practice|exam|quiz",
        "week": int,
        "order": int,
        "material_id": int,
        "question_data": [...],
        "exam_date": "YYYY-MM-DD" (optional),
        "start_time": "HH:MM:SS" (optional),
        "end_time": "HH:MM:SS" (optional),
        "duration": int (optional),
        "overdue_rule_id": int (optional)
    }

    Response:
    {
        "code": 200,
        "message": "Task saved successfully",
        "data": {
            "unit_id": int
        }
    }
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='保存周任务',
        description='保存周任务及其题目数据',
        responses={
            200: {'description': '保存成功'},
            400: {'description': '参数错误'},
            500: {'description': '保存失败'}
        }
    )
    def post(self, request):
        """保存周任务"""
        try:
            from ELW.models import (
                Unit, PaperPage, MainQuestion, SubQuestion, PageMainQuestion,
                PageSubQuestion, MediaMaterial, TimeManagement, OverdueDeductionRule,
                ChoiceOption, MatchingOption, Correction
            )
            from Account.services.user_service_impl import UserServiceImpl
            import datetime

            data = request.data

            # 验证必填字段
            required_fields = ['title', 'class_id', 'type', 'week', 'material_id', 'question_data']
            for field in required_fields:
                if field not in data:
                    return Result.error(message=f'缺少必填字段: {field}', code=400)

            # 获取班级
            class_instance = UserServiceImpl.get_class_by_id(data['class_id'])
            if not class_instance:
                return Result.error(message='班级不存在', code=404)

            # 获取逾期规则
            overdue_rule_instance = None
            if data.get('overdue_rule_id'):
                try:
                    overdue_rule_instance = OverdueDeductionRule.objects.get(id=data['overdue_rule_id'])
                except OverdueDeductionRule.DoesNotExist:
                    pass

            # 创建Unit
            unit_instance = Unit.objects.create(
                class_instance=class_instance,
                order=data.get('order', 0),
                title=data['title'],
                type=data['type'],
                overdue_rule=overdue_rule_instance
            )

            # 创建TimeManagement
            if data['type'] == 'exam' and data.get('exam_date'):
                TimeManagement.objects.create(
                    unit=unit_instance,
                    duration=data.get('duration', 60),
                    exam_date=datetime.date.fromisoformat(data['exam_date']),
                    start_time=datetime.time.fromisoformat(data['start_time']) if data.get('start_time') else None,
                    end_time=datetime.time.fromisoformat(data['end_time']) if data.get('end_time') else None,
                )
            elif data['type'] in ['quiz', 'task']:
                TimeManagement.objects.create(
                    unit=unit_instance,
                    week=data['week'],
                    duration=data.get('duration', 60),
                )

            # 获取素材包
            media_material = MediaMaterial.objects.get(pk=data['material_id'])

            # 遍历所有页面
            for page_idx, page_item in enumerate(data['question_data']):
                # 创建PaperPage
                paper_page = PaperPage.objects.create(
                    unit=unit_instance,
                    order=page_idx,
                    text=f'第{page_idx+1}个页面',
                    limited_time=page_item.get('limited_time'),
                    can_modify=page_item.get('can_modify', False)
                )

                # 遍历所有大题
                for main_item in page_item.get('page_content', []):
                    # 创建MainQuestion
                    main_question = MainQuestion.objects.create(
                        media_material=media_material,
                        question_type=main_item.get('question_type'),
                        question_text=main_item.get('question_text', ''),
                        maximum_play=int(main_item.get('max', 3)),
                        minimum_play=int(main_item.get('min', 1)),
                        start_time=datetime.time.fromisoformat(main_item['start']) if main_item.get('start') else None,
                        end_time=datetime.time.fromisoformat(main_item['end']) if main_item.get('end') else None,
                        allow_pause=main_item.get('allow_pause', False),
                        limited_time=datetime.time.fromisoformat(main_item['limited_time']) if main_item.get('limited_time') else None,
                        no_media=main_item.get('no_media', False)
                    )

                    # 保存大题图片
                    if main_item.get('main_question_images'):
                        main_question.image_url = ','.join(main_item['main_question_images'])
                        main_question.save()

                    # 创建PageMainQuestion关联
                    PageMainQuestion.objects.create(
                        page=paper_page,
                        main_question=main_question
                    )

                    # 创建小题
                    for sub_item in main_item.get('sub_questions', []):
                        sub_question = SubQuestion.objects.create(
                            main_question=main_question,
                            question_text=sub_item.get('question_text', ''),
                            score=float(sub_item.get('score', 0)),
                            answer=sub_item.get('answer', ''),
                            tips=sub_item.get('tips', ''),
                            analysis=sub_item.get('analysis', ''),
                            image_url=sub_item.get('image_url', '')
                        )

                        # 创建选择题选项
                        if main_item['question_type'] == 'choice':
                            for option in sub_item.get('options', []):
                                ChoiceOption.objects.create(
                                    sub_question=sub_question,
                                    option_label=option.get('label', ''),
                                    option_content=option.get('content', ''),
                                    image_url=option.get('image_url', ''),
                                    is_answer=option.get('is_answer', False)
                                )

                        # 创建连线题选项
                        elif main_item['question_type'] == 'matching':
                            for option in sub_item.get('matching_options', []):
                                MatchingOption.objects.create(
                                    sub_question=sub_question,
                                    option_label=option.get('label', ''),
                                    option_content=option.get('content', ''),
                                    image_url=option.get('image_url', '')
                                )

                        # 创建改错题
                        elif main_item['question_type'] == 'correction':
                            for correction in sub_item.get('corrections', []):
                                Correction.objects.create(
                                    sub_question=sub_question,
                                    type=correction.get('type', ''),
                                    index=correction.get('index', 0)
                                )

            serializer = UnitSerializer(unit_instance)
            return Result.success(
                data={'unit_id': unit_instance.id, 'unit': serializer.data},
                message='Task saved successfully'
            )
        except Exception as e:
            return Result.error(message=f'Failed to save task: {str(e)}', code=500)









