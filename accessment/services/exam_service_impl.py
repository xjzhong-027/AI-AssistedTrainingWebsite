"""
Exam service implementation.

This module implements the ExamService interface, providing unified access
to exam/practice functionality. It merges duplicate code from accessment and stu_practice modules.
"""
import json
import threading
from typing import Optional, List, Dict
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from common.services.exam_service import ExamService
from accessment.models import (
    StudentExamRecord, StudentPageRecord, StudentAnswer, StudentMediaPlayRecord
)
from ELW.models import (
    PageMainQuestion, PageSubQuestion, Correction
)
from ELW.services.content_service_impl import ContentServiceImpl
from AI_module.Get_from_AI import Get_from_AI


class ExamServiceImpl(ExamService):
    """考试服务实现"""

    @staticmethod
    def create_exam_record(student_id: int, unit_id: int) -> StudentExamRecord:
        """创建考试记录"""
        from Account.models import Students
        from ELW.models import Unit
        
        student = Students.objects.get(id=student_id)
        unit = Unit.objects.get(id=unit_id)
        
        record, created = StudentExamRecord.objects.get_or_create(
            user=student,
            exam=unit
        )
        
        if created:
            record.started_at = timezone.now()
            record.save()
        
        return record

    @staticmethod
    def get_exam_record(student_id: int, unit_id: int) -> Optional[StudentExamRecord]:
        """获取考试记录"""
        try:
            from Account.models import Students
            from ELW.models import Unit
            
            student = Students.objects.get(id=student_id)
            unit = Unit.objects.get(id=unit_id)
            return StudentExamRecord.objects.get(user=student, exam=unit)
        except (StudentExamRecord.DoesNotExist, Students.DoesNotExist, Unit.DoesNotExist):
            return None

    @staticmethod
    def get_exam_record_by_id(record_id: int) -> Optional[StudentExamRecord]:
        """根据ID获取考试记录"""
        try:
            return StudentExamRecord.objects.get(id=record_id)
        except StudentExamRecord.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_page_record(
        exam_record_id: int,
        page_id: int
    ) -> StudentPageRecord:
        """获取或创建页面记录"""
        exam_record = ExamServiceImpl.get_exam_record_by_id(exam_record_id)
        if not exam_record:
            raise ValueError(f"Exam record {exam_record_id} not found")
        
        page = ContentServiceImpl.get_paper_page_by_id(page_id)
        if not page:
            raise ValueError(f"Page {page_id} not found")
        
        page_record, created = StudentPageRecord.objects.get_or_create(
            student_exam_record=exam_record,
            page=page
        )
        
        if created and page.limited_time and page.limited_time > 0:
            page_record.remaining_time = page.limited_time * 60
            page_record.save()
        
        return page_record

    @staticmethod
    def get_page_record_by_id(record_id: int) -> Optional[StudentPageRecord]:
        """根据ID获取页面记录"""
        try:
            return StudentPageRecord.objects.get(id=record_id)
        except StudentPageRecord.DoesNotExist:
            return None

    @staticmethod
    def get_page_records_by_exam(exam_record_id: int) -> List[StudentPageRecord]:
        """获取考试记录的所有页面记录"""
        exam_record = ExamServiceImpl.get_exam_record_by_id(exam_record_id)
        if not exam_record:
            return []
        
        return list(StudentPageRecord.objects.filter(student_exam_record=exam_record))

    @staticmethod
    def save_answer(
        student_page_record_id: int,
        sub_question_id: int,
        answer_text: str,
        is_correct: Optional[bool] = None
    ) -> StudentAnswer:
        """保存学生答案"""
        page_record = ExamServiceImpl.get_page_record_by_id(student_page_record_id)
        if not page_record:
            raise ValueError(f"Page record {student_page_record_id} not found")
        
        sub_question = ContentServiceImpl.get_sub_question_by_id(sub_question_id)
        if not sub_question:
            raise ValueError(f"Sub question {sub_question_id} not found")
        
        answer, created = StudentAnswer.objects.update_or_create(
            student_page_record=page_record,
            sub_question=sub_question,
            defaults={'text': answer_text}
        )
        
        if is_correct is not None:
            answer.score = sub_question.score if is_correct else 0
        
        return answer

    @staticmethod
    def get_answers_by_page_record(page_record_id: int) -> List[StudentAnswer]:
        """获取页面记录的所有答案"""
        page_record = ExamServiceImpl.get_page_record_by_id(page_record_id)
        if not page_record:
            return []
        
        return list(StudentAnswer.objects.filter(student_page_record=page_record))

    @staticmethod
    def load_answers(page_record_id: int) -> Dict:
        """加载页面记录的答案（从缓存或数据库）"""
        page_record = ExamServiceImpl.get_page_record_by_id(page_record_id)
        if not page_record:
            return {}
        
        cache_key = f"answers_{page_record_id}"
        cached_answers = cache.get(cache_key)
        
        if cached_answers is not None:
            answers_dict = {}
            for sub_question_id, answer_text in cached_answers.items():
                if answer_text:
                    if isinstance(answer_text, str) and answer_text.startswith('['):
                        answers_dict[int(sub_question_id)] = json.loads(answer_text)
                    else:
                        answers_dict[int(sub_question_id)] = answer_text
            return answers_dict
        
        # 从数据库加载
        answers = StudentAnswer.objects.filter(student_page_record=page_record)
        answers_dict = {}
        
        for answer in answers:
            sub_question_id = int(answer.sub_question_id)
            if answer.sub_question.main_question.question_type == 'correction':
                if sub_question_id not in answers_dict:
                    answers_dict[sub_question_id] = []
                answers_dict[sub_question_id].append({
                    'text': answer.text,
                    'index': answer.index,
                    'type': answer.type
                })
            else:
                answers_dict[sub_question_id] = answer.text
        
        # 更新缓存
        cache.set(cache_key, answers_dict, timeout=600)
        
        return answers_dict

    @staticmethod
    def save_answers_to_cache(
        page_record_id: int,
        answers_data: Dict
    ) -> bool:
        """保存答案到缓存"""
        cache_key = f"answers_{page_record_id}"
        cache.set(cache_key, answers_data, timeout=600)
        return True

    @staticmethod
    def save_answers_to_database(page_record_id: int) -> bool:
        """从缓存读取答案并保存到数据库"""
        cache_key = f"answers_{page_record_id}"
        cached_answers = cache.get(cache_key, {})
        
        page_record = ExamServiceImpl.get_page_record_by_id(page_record_id)
        if not page_record:
            return False
        
        with transaction.atomic():
            for sub_question_id, answer_text in cached_answers.items():
                sub_question_id = int(sub_question_id)
                sub_question = ContentServiceImpl.get_sub_question_by_id(sub_question_id)
                if not sub_question:
                    continue
                
                if sub_question.main_question.question_type == 'correction':
                    if answer_text == 'none':
                        StudentAnswer.objects.filter(
                            sub_question=sub_question,
                            student_page_record_id=page_record_id
                        ).delete()
                    else:
                        StudentAnswer.objects.filter(
                            sub_question=sub_question,
                            student_page_record_id=page_record_id
                        ).delete()
                        
                        corrections = json.loads(answer_text) if isinstance(answer_text, str) else answer_text
                        for correction in corrections:
                            StudentAnswer.objects.create(
                                sub_question=sub_question,
                                student_page_record_id=page_record_id,
                                text=correction['text'],
                                index=int(correction['index']),
                                type=correction['type']
                            )
                else:
                    StudentAnswer.objects.update_or_create(
                        sub_question_id=sub_question_id,
                        student_page_record_id=page_record_id,
                        defaults={'text': answer_text}
                    )
            
            # 更新缓存
            ExamServiceImpl._update_cache(page_record)
        
        return True

    @staticmethod
    def _update_cache(page_record: StudentPageRecord):
        """从数据库中读取最新答案并更新缓存"""
        cache_key = f"answers_{page_record.id}"
        cached_answers = {}
        
        student_answers = StudentAnswer.objects.filter(student_page_record=page_record)
        for answer in student_answers:
            sub_question_id = answer.sub_question.id
            if answer.sub_question.main_question.question_type == 'correction':
                corrections = []
                if answer.type and answer.index is not None and answer.text:
                    corrections.append({
                        'type': answer.type,
                        'index': answer.index,
                        'text': answer.text
                    })
                cached_answers[sub_question_id] = json.dumps(corrections)
            else:
                cached_answers[sub_question_id] = answer.text
        
        cache.set(cache_key, cached_answers, timeout=600)

    @staticmethod
    def submit_page(page_record_id: int) -> bool:
        """提交页面"""
        page_record = ExamServiceImpl.get_page_record_by_id(page_record_id)
        if not page_record:
            return False
        
        page_record.submitted = True
        page_record.submitted_at = timezone.now()
        page_record.save()
        
        return True

    @staticmethod
    def grade_page(page_record_id: int) -> bool:
        """批改页面"""
        page_record = ExamServiceImpl.get_page_record_by_id(page_record_id)
        if not page_record:
            return False
        
        student_answers = StudentAnswer.objects.filter(student_page_record_id=page_record_id)
        
        total_score = 0
        feedback = []
        
        for student_answer in student_answers:
            sub_question = student_answer.sub_question
            correct_answer = sub_question.answer
            question_type = sub_question.main_question.question_type
            
            if question_type == 'choice':
                if student_answer.text == correct_answer:
                    score = sub_question.score
                else:
                    score = 0
                feedback.append(f"第{sub_question.id}题: 你的答案是 {student_answer.text}, 正确答案是 {correct_answer}")
            elif question_type == 'blank':
                if student_answer.text == correct_answer:
                    score = sub_question.score
                else:
                    score = 0
            elif question_type == 'matching':
                if student_answer.text == correct_answer:
                    score = sub_question.score
                else:
                    score = 0
            elif question_type == 'correction':
                correct_corrections = Correction.objects.filter(sub_question=sub_question)
                student_corrections = StudentAnswer.objects.filter(
                    sub_question=sub_question,
                    student_page_record=page_record
                )
                correct = True
                for correct_correction in correct_corrections:
                    found = False
                    for student_correction in student_corrections:
                        if (student_correction.type == correct_correction.type and
                                student_correction.index == correct_correction.index):
                            found = True
                            break
                    if not found:
                        correct = False
                        break
                score = sub_question.score if correct else 0
            elif question_type == 'comprehension':
                score = -1
                # 启动后台线程进行AI评分
                grading_thread = threading.Thread(
                    target=ExamServiceImpl._background_grade_comprehension,
                    args=(sub_question, student_answer, page_record)
                )
                grading_thread.daemon = True
                grading_thread.start()
                continue
            
            if score is not None and score >= 0:
                total_score += score
                student_answer.score = score
            else:
                student_answer.score = score
            
            student_answer.save()
        
        page_record.page_score = total_score
        page_record.feedback = "\n".join(feedback)
        page_record.is_graded = True
        page_record.save()
        
        return True

    @staticmethod
    def grade_comprehension(
        sub_question_id: int,
        student_answer_id: int
    ) -> float:
        """批改理解题（使用AI）"""
        sub_question = ContentServiceImpl.get_sub_question_by_id(sub_question_id)
        if not sub_question:
            raise ValueError(f"Sub question {sub_question_id} not found")
        
        student_answer = StudentAnswer.objects.get(id=student_answer_id)
        
        try:
            m = Get_from_AI(model='ZhipuAI')
            m.set_prompt_variables(my_dict={
                "原文": "暂无",
                "题目": sub_question.question_text,
                "参考答案": sub_question.answer,
                "学生回答": student_answer.text,
                "其他要求_评分": "请按格式｛\"分数\":, \"理由\":｝给出分数和理由，使用英文符号"
            })
            res = m.get_answer(m.get_prompt("题目评分"))
            dic = json.loads(res)
            score = float(dic['分数']) * sub_question.score // 100
            student_answer.score = score
            student_answer.save()
            return score
        except Exception as e:
            print(f"Error grading comprehension: {e}")
            return 0.0

    @staticmethod
    def _background_grade_comprehension(sub_question, student_answer, page_record):
        """后台批改理解题"""
        try:
            score = ExamServiceImpl.grade_comprehension(
                sub_question.id,
                student_answer.id
            )
            
            # 重新计算并更新页面分数
            answers = StudentAnswer.objects.filter(student_page_record=page_record)
            valid_scores = [ans.score for ans in answers if ans.score is not None and ans.score >= 0]
            if valid_scores:
                page_record.page_score = sum(valid_scores)
                page_record.save()
            
            # 更新考试记录总分
            exam_record = page_record.student_exam_record
            page_records = StudentPageRecord.objects.filter(
                student_exam_record=exam_record,
                is_graded=True
            )
            total_score = sum(pr.page_score for pr in page_records if pr.page_score is not None)
            exam_record.score = total_score
            exam_record.save()
        except Exception as e:
            print(f"后台评分错误: {e}")

    @staticmethod
    def update_media_play_record(
        exam_record_id: int,
        main_question_id: int,
        play_count: int,
        last_pause_time: float
    ) -> StudentMediaPlayRecord:
        """更新媒体播放记录"""
        exam_record = ExamServiceImpl.get_exam_record_by_id(exam_record_id)
        if not exam_record:
            raise ValueError(f"Exam record {exam_record_id} not found")
        
        main_question = ContentServiceImpl.get_main_question_by_id(main_question_id)
        if not main_question:
            raise ValueError(f"Main question {main_question_id} not found")
        
        media_material = main_question.media_material
        
        play_record, created = StudentMediaPlayRecord.objects.get_or_create(
            student_exam_record=exam_record,
            main_question=main_question,
            media_material=media_material,
            defaults={'play_count': 0, 'last_pause_time': 0}
        )
        
        play_record.play_count = play_count
        play_record.last_pause_time = last_pause_time
        play_record.save()
        
        return play_record

    @staticmethod
    def get_media_play_record(
        exam_record_id: int,
        main_question_id: int
    ) -> Optional[StudentMediaPlayRecord]:
        """获取媒体播放记录"""
        try:
            exam_record = ExamServiceImpl.get_exam_record_by_id(exam_record_id)
            if not exam_record:
                return None
            
            main_question = ContentServiceImpl.get_main_question_by_id(main_question_id)
            if not main_question:
                return None
            
            return StudentMediaPlayRecord.objects.get(
                student_exam_record=exam_record,
                main_question=main_question
            )
        except StudentMediaPlayRecord.DoesNotExist:
            return None

    @staticmethod
    def submit_exam(exam_record_id: int) -> bool:
        """提交考试"""
        exam_record = ExamServiceImpl.get_exam_record_by_id(exam_record_id)
        if not exam_record:
            return False
        
        # 根据各页面得分重新计算总分（修复：同步批改时未更新 exam_record.score 的问题）
        page_records = ExamServiceImpl.get_page_records_by_exam(exam_record_id)
        total_score = sum(
            float(pr.page_score) for pr in page_records
            if pr.page_score is not None
        )
        exam_record.score = total_score
        
        exam_record.submitted = True
        exam_record.finished_at = timezone.now()
        exam_record.save()
        
        return True

    @staticmethod
    def get_exam_records_by_user(user_id: int) -> List[StudentExamRecord]:
        """获取用户的所有考试记录"""
        from Account.models import Students
        
        try:
            student = Students.objects.get(id=user_id)
            return list(StudentExamRecord.objects.filter(user=student).order_by('-started_at'))
        except Students.DoesNotExist:
            return []

    @staticmethod
    def get_media_play_records_by_exam(
        exam_record_id: int,
        main_question_ids: Optional[List[int]] = None
    ) -> List[StudentMediaPlayRecord]:
        """获取考试记录的所有媒体播放记录"""
        exam_record = ExamServiceImpl.get_exam_record_by_id(exam_record_id)
        if not exam_record:
            return []
        
        query = StudentMediaPlayRecord.objects.filter(student_exam_record=exam_record)
        if main_question_ids:
            query = query.filter(main_question_id__in=main_question_ids)
        
        return list(query)

