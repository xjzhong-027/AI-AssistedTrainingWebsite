// 页面倒计时
document.addEventListener('DOMContentLoaded', function () {
    const pageTimerElement = document.getElementById('page-time-remaining');
    const pageTimerContainer = document.getElementById('page-timer');
    let remainingTime = parseFloat("{{ remaining_time }}"); // 从后端获取的初始剩余时间（秒）
    let pageTimerInterval = null;

    // 更新页面倒计时显示
    function updatePageTimer() {
        remainingTime -= 1; // 每秒减少1秒

        if (remainingTime <= 0) {
            clearInterval(pageTimerInterval);
            pageTimerElement.textContent = '00:00:00';
            alert("Time is up! Redirecting to the next page...");
            window.location.href = "{% url 'accessment:exam_page' exam.id order|add:1 %}";
            return;
        }

        const hours = Math.floor(remainingTime / 3600);
        const minutes = Math.floor((remainingTime % 3600) / 60);
        const seconds = Math.floor(remainingTime % 60);

        pageTimerElement.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        // 如果剩余时间少于 1 分钟，添加警告样式
        if (remainingTime < 50) {
            pageTimerContainer.classList.add('warning');
        } else {
            pageTimerContainer.classList.remove('warning');
        }
    }

    // 启动倒计时
    function startPageTimer() {
        clearInterval(pageTimerInterval); // 清除之前的定时器
        pageTimerInterval = setInterval(updatePageTimer, 1000);
    }

    // 暂停倒计时
    function pausePageTimer() {
        clearInterval(pageTimerInterval);
    }

    // 页面失去焦点时暂停倒计时，并更新剩余时间到后端
    window.onblur = function () {
        pausePageTimer();
        fetch("{% url 'accessment:update_remaining_time' student_page_record.id %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
            },
            body: JSON.stringify({ remaining_time: remainingTime }) // 以秒为单位
        });
    };
// 页面即将卸载时更新剩余时间到后端
    window.onbeforeunload = function () {
        fetch("{% url 'accessment:update_remaining_time' student_page_record.id %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
            },
            body: JSON.stringify({ remaining_time: remainingTime }) // 以秒为单位
        });
    };

    // 页面重新获得焦点时恢复倒计时
    window.onfocus = function () {
        startPageTimer();
    };

    // 初始更新倒计时显示
    updatePageTimer();

    // 初始启动倒计时
    startPageTimer();
});

<!-- 自动手动保存 提交当前页面 -->
    // 手动保存：将答案暂存到缓存
    function manualSave() {
    const examForm = document.getElementById('save-answers-form');
    const formData = new FormData(examForm);

    // 直接在 FormData 中设置值
    formData.set('manual_save', 'true');
    formData.set('is_manual_submit', 'false');

    // 调用 submitForm 提交表单
    submitForm(formData);
}

    // 提交：将答案保存到数据库
    function manualSubmit() {
    const examForm = document.getElementById('save-answers-form');
    const formData = new FormData(examForm);

    // 直接在 FormData 中设置值
    formData.set('manual_save', 'false');
    formData.set('is_manual_submit', 'true');

    // 调用 submitForm 提交表单
    submitForm(formData);
}

    // 提交表单的通用函数
    function submitForm(formData) {
        const examForm = document.getElementById('save-answers-form');
                const unfinishedConfirmationModal = document.getElementById('unfinishedConfirmationModal');
                const finishedConfirmationModal = document.getElementById('finishedConfirmationModal');
                const unfinishedConfirmationMessage = document.getElementById('unfinishedConfirmationMessage');
                const finishedConfirmationMessage = document.getElementById('finishedConfirmationMessage');
                const unfinishedConfirmSubmitButton = document.getElementById('unfinishedConfirmSubmit');
                const finishedConfirmSubmitButton = document.getElementById('finishedConfirmSubmit');

        for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }
        fetch(examForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(response => response.json())
        .then(data => {
                            if (data.status === 'unfinished') {
                                // 有未完成的题目，显示模态框
                                unfinishedConfirmationMessage.textContent = data.message;
                                unfinishedConfirmationModal.style.display = 'block';
                                unfinishedConfirmSubmitButton.onclick = addForceSubmitAndSubmitForm;
                            } else if (data.status === 'finished') {
                                // 没有未完成的题目，提示用户“是否确认提交？”
                                finishedConfirmationMessage.textContent = data.message;
                                finishedConfirmationModal.style.display = 'block';
                                finishedConfirmSubmitButton.onclick = addForceSubmitAndSubmitForm;
                            } else if (data.status === 'saved') {   // 可以修改的页面但有未完成的页面
                                successMessage.textContent = data.message;
                                successModal.style.display = 'block';
                                setTimeout(() => {
                                    successModal.style.display = 'none';
                                    canModify();
                                }, 500);

                            } else {
                                // 其他情况，显示返回的消息
                                alert(data.message);
                            }
                        })
        .catch(error => {
            console.error('Error:', error);
            alert('保存答案时出错，请检查网络连接或稍后再试。');
        });
    }

    // 强制提交：将答案保存到数据库并跳转到下一页
    function addForceSubmitAndSubmitForm() {
        const examForm = document.getElementById('save-answers-form');
        const forceSubmitInput = document.createElement('input');
        forceSubmitInput.type = 'hidden';
        forceSubmitInput.name = 'force_submit';
        forceSubmitInput.value = 'true';
        examForm.appendChild(forceSubmitInput);
        examForm.submit();
    }
function canModify() {
                const examForm = document.getElementById('save-answers-form');
                const canModifyInput = document.createElement('input');
                canModifyInput.type = 'hidden';
                canModifyInput.name = 'saved';
                canModifyInput.value = 'true';
                examForm.appendChild(canModifyInput);
                examForm.submit();
            }
    // 自动保存逻辑：每隔一段时间将答案暂存到缓存
    function autoSaveAnswers() {
        const examForm = document.getElementById('save-answers-form');
        const formData = new FormData(examForm);

        // 设置 manual_save 为 true，表示自动保存
        document.querySelector('input[name="manual_save"]').value = "true";
        document.querySelector('input[name="is_manual_submit"]').value = "false";

        fetch(examForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
            }
        }).then(response => {
            if (response.ok) {
                console.log('Auto-save successful');
            } else {
                console.error('Auto-save failed');
            }
        }).catch(error => {
            console.error('Error during auto-save:', error);
        });
    }

    // 每隔30秒自动保存一次
    setInterval(autoSaveAnswers, 30000);

    // 页面加载完成后绑定事件
    document.addEventListener('DOMContentLoaded', function () {
        // 关闭模态框
        document.querySelector('.modal .close').onclick = function () {
            document.getElementById('unfinishedConfirmationModal').style.display = 'none';
            document.getElementById('finishedConfirmationModal').style.display = 'none';
        };

        // 继续完成按钮的点击事件
        document.querySelector('#unfinishedConfirmationModal .btn-secondary').onclick = function () {
            document.getElementById('unfinishedConfirmationModal').style.display = 'none';
        };

        // 取消按钮的点击事件
        document.querySelector('#finishedConfirmationModal .btn-secondary').onclick = function () {
            document.getElementById('finishedConfirmationModal').style.display = 'none';
        };
    });

        <!--  页面导航 -->
document.addEventListener('DOMContentLoaded', function () {
    //const currentPageNumber = {{ page.order | safe }};
    const pageNavCircles = document.querySelectorAll('.nav-circle');

    // 更新页面导航圆点的状态
    function updateNavCircles() {
        pageNavCircles.forEach(circle => {
            const pageNumber = parseInt(circle.getAttribute('data-page-number'));

            // 当前页面显示为红色
            if (pageNumber === currentPageNumber) {
                circle.classList.add('active');
            } else {
                circle.classList.remove('active');
            }

            // 未到达的页面显示为灰色
            if (pageNumber > currentPageNumber) {
                circle.classList.add('disabled');
            } else {
                circle.classList.remove('disabled');
            }
        });
    }

    // 初始化页面导航圆点状态
    updateNavCircles();
});
        <!-- 交卷 -->
document.addEventListener('DOMContentLoaded', function () {
    const submitExamButton = document.getElementById('submit-exam-btn');
    const examForm = document.getElementById('submit-exam-form');
    const saveAnswersForm = document.getElementById('save-answers-form');
    const ExamunfinishedConfirmationModal = document.getElementById('ExamunfinishedConfirmationModal');
    const ExamunfinishedConfirmationMessage = document.getElementById('ExamunfinishedConfirmationMessage');
    const ExamunfinishedConfirmSubmitButton = document.getElementById('ExamunfinishedConfirmSubmit');
    const gotofinishButton = document.getElementById('gotofinishButton');
    const ExamfinishedConfirmationModal = document.getElementById('ExamfinishedConfirmationModal');
    const ExamfinishedConfirmationMessage = document.getElementById('ExamfinishedConfirmationMessage');
    const ExamfinishedConfirmSubmitButton = document.getElementById('ExamfinishedConfirmSubmit');

    // 交卷按钮点击事件
    submitExamButton.addEventListener('click', function (event) {
        event.preventDefault(); // 阻止默认提交行为

        // 调用保存答案的逻辑
        manualSave().then(() => {
            // 保存成功后，提交试卷
           ExamUtils.submitExamForm();
        }).catch((error) => {
            alert('保存答案时出错，请稍后再试。');
            console.error('Error:', error);
        });
    });

    // 保存答案的逻辑
    function manualSave() {
        return new Promise((resolve, reject) => {
            const formData = new FormData(saveAnswersForm);
formData.set('manual_save', 'true');
    formData.set('is_manual_submit', 'false');
            fetch(saveAnswersForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: formData

            })
            .then(response => response.json())
            .then(data => {
                if (data.message === '已保存') {
                    console.log('答案已成功保存');
                    formData.forEach((value, key) => {
    console.log(`${key}: ${value}`);
});
                    resolve(); // 保存成功
                } else {
                    console.error('保存答案失败:', data.message);
                    reject(new Error(data.message)); // 保存失败
                }
            })
            .catch(error => {
                console.error('保存答案时出错:', error);
                reject(error); // 网络错误
            });
        });
    }

    // 提交试卷表单
        window.ExamUtils = {
            submitExamForm: function (forceSubmit = false) {
        const formData = new FormData(examForm);

        if (forceSubmit) {
        forceSubmitForm()
    }


        fetch(examForm.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (!forceSubmit) {
                if (data.status === 'exam_unfinished') {
                    // 显示未完成提示模态框
                    ExamunfinishedConfirmationMessage.textContent = data.message;
                    ExamunfinishedConfirmationModal.style.display = 'block';
                    ExamunfinishedConfirmSubmitButton.onclick = stillSubmitForm;
                    gotofinishButton.onclick = () => goToIncompletePage(data.unsubmitted_pages);
                } else if (data.status === 'exam_finished') {
                    // 显示确认提交模态框
                    ExamfinishedConfirmationMessage.textContent = data.message;
                    ExamfinishedConfirmationModal.style.display = 'block';
                    ExamfinishedConfirmSubmitButton.onclick = function () {
                        const finishSubmitInput = document.createElement('input');
                        finishSubmitInput.type = 'hidden';
                        finishSubmitInput.name = 'finish_submit';
                        finishSubmitInput.value = 'true';
                        examForm.appendChild(finishSubmitInput);
                        examForm.submit();
                    };
                } else {
                    // 其他情况，显示返回的消息
                    alert(data.message);
                }
            }else{
                alert('试卷已成功提交');
                    window.location.href = '/exam-result';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('提交出错，请检查网络连接或稍后再试。');
        });
    }
}
    function stillSubmitForm() {
        // 添加 still_submit 标志并提交表单
        const stillSubmitInput = document.createElement('input');
        stillSubmitInput.type = 'hidden';
        stillSubmitInput.name = 'still_submit';
        stillSubmitInput.value = 'true';
        examForm.appendChild(stillSubmitInput);
        examForm.submit();
    }
function forceSubmitForm() {
        const forceSubmitInput = document.createElement('input');
        forceSubmitInput.type = 'hidden';
        forceSubmitInput.name = 'force_submit';
        forceSubmitInput.value = 'true';
        examForm.appendChild(forceSubmitInput);
        examForm.submit();
    }
    function goToIncompletePage(unsubmittedPages) {
        // 跳转到第一个未完成的页面
        const firstIncompletePage = Math.min(...unsubmittedPages);
        window.location.href = "{% url 'accessment:exam_page' exam_id=exam.id order=1 %}".replace(/1/, firstIncompletePage);
    }

    // 关闭模态框
    document.querySelector('.modal .close').onclick = function () {
        ExamunfinishedConfirmationModal.style.display = 'none';
        ExamfinishedConfirmationModal.style.display = 'none';
    };
});
        <!--  倒计时 -->
 document.addEventListener('DOMContentLoaded', function () {
                const timerElement = document.getElementById('time-remaining');
            const startedAt = new Date("{{ student_exam_record.started_at|date:'Y-m-d H:i:s' }}");
            const endedAt = new Date("{{ student_exam_record.ended_at|date:'Y-m-d H:i:s' }}");

            // 计算剩余时间
            function calculateRemainingTime(startedAt, endedAt) {
                const now = new Date();
                const endTime = new Date(endedAt);
                const remainingTime = endTime - now;

                if (remainingTime <= 0) {
                    return '00:00:00';
                }

                const hours = Math.floor((remainingTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);

                return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }

            // 更新倒计时显示
            function updateTimer() {
                const remainingTime = calculateRemainingTime(startedAt, endedAt);
                timerElement.textContent = remainingTime;

                if (remainingTime === '00:00:00') {
                    // 倒计时结束，强制交卷
                    ExamUtils.submitExamForm(true);
                }
            }

            // 每秒更新倒计时
            setInterval(updateTimer, 1000);

            // 初始更新
            updateTimer();
});

    // 改错题
        document.addEventListener('DOMContentLoaded', function() {
        // 获取所有可点击的单词
        const clickableWords = document.querySelectorAll('.clickable-word');

        clickableWords.forEach(word => {
            word.addEventListener('click', function() {
                const subQuestionId = word.closest('.corrections').dataset.subQuestionId;
                const correctionIndex = document.getElementById(`correction_index_${subQuestionId}`);
                const selectedWord = document.getElementById(`selected_word_${subQuestionId}`);

                // 更新隐藏字段和显示的单词
                correctionIndex.value = word.dataset.index;
                selectedWord.textContent = `${word.dataset.word}`;
            });
        });
    });


        <!--  练习端发帖 -->

var subQuestionId = null; // 定义为全局变量
var quoteButton = null; // 定义为全局变量

document.addEventListener('selectionchange', function() {
    var selectedText = window.getSelection().toString().trim();

    // 假设每个小题都有一个唯一的ID标识符
    var selectedElements = document.querySelectorAll('[data-sub-question-id]');

    // 找到最接近的包含小题ID的元素
    for (var i = 0; i < selectedElements.length; i++) {
        var element = selectedElements[i];
        var range = window.getSelection().getRangeAt(0);
        if (range.intersectsNode(element)) {
            subQuestionId = element.getAttribute('data-sub-question-id');
            break;
        }
    }
    console.log('subQuestionId: ' + subQuestionId);

    if (selectedText) {
        if (!quoteButton) {
            // 如果按钮不存在，则创建它
            quoteButton = document.createElement('button');
            quoteButton.textContent = '发帖询问';
            quoteButton.id = 'quoteButton';
            quoteButton.style.position = 'absolute';
            quoteButton.style.top = '10px'; // 根据需要调整位置
            quoteButton.style.right = '10px';
            quoteButton.style.zIndex = '1000';
            document.body.appendChild(quoteButton);
        }
        // 显示按钮
        quoteButton.style.display = 'inline';
    } else {
        // 如果没有选中文本，隐藏按钮
        if (quoteButton) {
            quoteButton.style.display = 'none';
        }
    }
});

// 监听按钮点击事件
document.addEventListener('click', function(event) {
    if (event.target === quoteButton) {
        // 构建跳转URL，包含小题ID
        var url = '{% url "forum:post_new" %}?sub_question_id=' + encodeURIComponent(subQuestionId);
        window.location.href = url;
    }
});
