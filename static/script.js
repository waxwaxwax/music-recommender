document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('mobile-menu');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;

    if (!menuToggle || !navMenu) {
        console.error("ハンバーガーメニューの要素が見つかりません");
        return;
    }

    menuToggle.addEventListener('click', function () {
        const isActive = navMenu.classList.toggle('active');
        menuToggle.classList.toggle('active');

        // メニューを開いたときにスクロールを無効化
        body.style.overflow = isActive ? 'hidden' : 'auto';

        // アクセシビリティ向上のための属性変更
        menuToggle.setAttribute('aria-expanded', isActive ? "true" : "false");
    });

    // メニュー内のリンクをクリックしたら閉じる
    document.querySelectorAll('.nav-menu a').forEach(item => {
        item.addEventListener('click', function () {
            navMenu.classList.remove('active');
            menuToggle.classList.remove('active');
            body.style.overflow = 'auto'; // スクロールを有効化
            menuToggle.setAttribute('aria-expanded', "false");
        });
    });
});
