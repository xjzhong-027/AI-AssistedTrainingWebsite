
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
    for question_id in selected_questions:
        if question_id.startswith('main_'):
            main_id = int(question_id.split('main_')[1])
            main_question = MainQuestion.objects.get(id=main_id)
            preview_page.append({'main_question': main_question, 'page_info': page_info})
            main_id_list.append(main_id)
        elif question_id.startswith('sub_'):
            sub_id = int(question_id.split('sub_')[1])
            main_id = SubQuestion.objects.get(id=sub_id).main_question_id
            sub_question = SubQuestion.objects.get(id=sub_id)
            main_question = MainQuestion.objects.get(id=main_id)
            if main_id in main_id_list:
                for pre_page in preview_page:
                    if pre_page['main_question'].id == main_id:
                        pre_page['sub_questions'].append(sub_question)
            else:

                preview_page.append({'main_question': main_question, 'sub_questions': [sub_question], 'page_info': page_info})
                main_id_list.append(main_id)
    return preview_page