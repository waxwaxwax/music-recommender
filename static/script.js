document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('recommendForm'); 
    if (!form) {
        console.error("音楽推薦フォームが見つかりません");
        return;
    }

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const situation = document.getElementById('situation').value.trim();
        const genre = document.getElementById('genre').value.trim();
        const era = document.getElementById('era').value.trim();
        const loadingSpinner = document.getElementById('loading');
        const resultDiv = document.getElementById('result');

        console.log("選択されたデータ:", { situation, genre, era }); // デバッグ用

        if (!situation || !genre || !era) {
            alert("すべてのフィールドを入力してください");
            return;
        }

        const requestData = { situation, genre, era };

        try {
            loadingSpinner.style.display = "block"; // ローディングを表示
            resultDiv.innerHTML = ""; // 結果をリセット

            const response = await fetch('/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            console.log("リクエスト送信:", requestData); // デバッグ用
            console.log("レスポンスステータス:", response.status); // デバッグ用

            loadingSpinner.style.display = "none"; // ローディングを非表示

            if (!response.ok) {
                throw new Error('サーバーエラーが発生しました');
            }

            const data = await response.json();
            console.log("受信データ:", data); // デバッグ用
            resultDiv.innerHTML = `<p>${data.recommendation}</p>`;
        } catch (error) {
            loadingSpinner.style.display = "none"; // ローディングを非表示
            console.error("エラー:", error);
            alert("音楽推薦の取得に失敗しました");
        }
    });
});
