let timeout;  // 用于保存定时器的 ID
let firstActivityTime = null;  // 记录首次活动的时间
let lastActivitySentTime = null;  // 记录上次发送请求的时间


// 监控鼠标点击事件
document.addEventListener('click', function() {
    console.log('clicked.')
    updateLastActivity();
});

// 监控键盘按键事件
document.addEventListener('keydown', function() {
    updateLastActivity();
});

// 监控鼠标移动事件
// document.addEventListener('mousemove', function() {
//     updateLastActivity();
// });

// 更新最后活跃时间
function updateLastActivity() {
    const currentTime = new Date();

    // 如果是第一次活动，立即发送请求，并设置第一次活动的时间
    if (!firstActivityTime) {
        firstActivityTime = currentTime;
        sendActivityToServer(currentTime.toISOString());  // 立即发送请求
        lastActivitySentTime = currentTime;  // 更新上次发送的时间
    }

    // 如果首次活动时间存在，检查距离上次发送请求是否超过5分钟
    const timeSinceLastRequest = currentTime - lastActivitySentTime;
    if (timeSinceLastRequest >= 5 * 60000) {  // 5分钟（300000毫秒 5 * 60 * 1000）
        sendActivityToServer(currentTime.toISOString());  // 发送请求
        lastActivitySentTime = currentTime;  // 更新上次发送的时间
    }

    // 设置定时器（每次活动都会清除前一个定时器，重置定时器）
    if (timeout) clearTimeout(timeout);

    // 设定定时器，5分钟后清空状态
    timeout = setTimeout(function() {
        firstActivityTime = null;  // 清除首次活动时间
        lastActivitySentTime = null;  // 清除上次发送的时间
    },   5 * 60000);  // 5分钟后清空活动状态
}

// 定期心跳机制（heartbeat）向服务器报告用户状态，服务器可以通过最后一次心跳时间推断用户是否关闭了浏览器。
setInterval(function() {
    const currentTime = new Date();
    const timeSinceLastRequest = currentTime - lastActivitySentTime;
    if (timeSinceLastRequest >= 30 * 60000) {
        console.log('心跳机制生效，未活跃时间大于三十分钟，强制登出。')
        fetch('/update_last_activity/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
    }

    // })
    // .then(response => {
    //     return response.json();
    // })
    // .then(data => {
    //     if (data.session_expired) {
    //         // 如果 session 已经过期，跳转到登录页面
    //         window.location.href = '/login/';
    //     }
    //     console.log(data.session_expired)

}, 10 * 60 * 1000);  // 每 10 分钟检查一次

// 将活动时间发送到后端
function sendActivityToServer(lastActiveTime) {
    console.log('already sent for 1!');
    fetch('/update_last_activity/', {
        method:'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // 获取 CSRF token
        },
        body: JSON.stringify({
            last_active_time: lastActiveTime
        })
    });
}

// 获取 CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}