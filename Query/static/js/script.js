document.addEventListener('DOMContentLoaded', function() {
    // const navLinks = document.querySelectorAll('#sidebar .nav-link');
    //
    // // 点击时也为当前项添加 active 类
    // const sidebar = document.getElementById('sidebar');
    // sidebar.addEventListener('click', function(event) {
    //     // 检查点击的目标是否是 .nav-link
    //     if (event.target && event.target.matches('.nav-link')) {
    //         // 移除所有项的 active 类
    //         navLinks.forEach(link => link.parentElement.classList.remove('active'));
    //
    //         // 给点击的项添加 active 类
    //         event.target.parentElement.classList.add('active');
    //     }
    // });
    //


    // 隐藏左侧导航栏
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'toggle-btn';
    toggleBtn.innerHTML = '&#9776;'; // 使用汉堡菜单符号
    document.body.appendChild(toggleBtn);

    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('content-panel');

    toggleBtn.addEventListener('click', function() {
        // 切换左侧导航栏的显示与隐藏
        sidebar.classList.toggle('hidden');

        // 切换右侧内容区域的宽度
        mainContent.classList.toggle('shifted');
    });
});
