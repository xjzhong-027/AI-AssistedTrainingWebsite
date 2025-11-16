
from .models import (
    MediaMaterial,
    MainQuestion,
    SubQuestion,
    MatchingOption,
    Correction,
    ChoiceOption,
    Unit,
    PaperPage,
    PageMainQuestion,
    PageSubQuestion,
)

def preview_page(selected_questions, page_info):
    preview_page = []
    main_id_list = []
    
    # 如果题目列表为空，返回空列表
    if not selected_questions:
        return preview_page
    
    for question_id in selected_questions:
        if question_id.startswith('main_'):
            main_id = int(question_id.split('main_')[1])
            main_question = MainQuestion.objects.get(id=main_id)
            preview_page.append({'main_question': main_question, 'page_info': page_info})
            main_id_list.append(main_id)
        elif question_id.startswith('sub_'):
            sub_id = int(question_id.split('sub_')[1])
            sub_question = SubQuestion.objects.get(id=sub_id)
            main_id = sub_question.main_question_id
            main_question = MainQuestion.objects.get(id=main_id)
            
            # 检查该大题是否已在预览列表中
            if main_id in main_id_list:
                # 找到对应的大题，添加小题
                for pre_page in preview_page:
                    if pre_page['main_question'].id == main_id:
                        # 确保 sub_questions 列表存在
                        if 'sub_questions' not in pre_page:
                            pre_page['sub_questions'] = []
                        pre_page['sub_questions'].append(sub_question)
                        break
            else:
                # 新大题，创建新记录
                preview_page.append({
                    'main_question': main_question, 
                    'sub_questions': [sub_question], 
                    'page_info': page_info
                })
                main_id_list.append(main_id)
    
    return preview_page