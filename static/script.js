document.getElementById('recommendForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // ローディングスピナーを表示
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').innerHTML = '';

    const situation = document.getElementById('situation').value;
    const genre = document.getElementById('genre').value;
    const era = document.getElementById('era').value;
    
    try {
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ situation, genre, era })
        });
        
        const result = await response.json();
        
        if(result.error) {
            document.getElementById('result').innerHTML = `<p>Error: ${result.error}</p><p>${result.details}</p>`;
        } else {
            // URLをハイパーリンクに変換
            const htmlRecommendation = result.recommendation.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
            document.getElementById('result').innerHTML = `<h2>おすすめ:</h2><pre>${htmlRecommendation}</pre>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `<p>Error: ${error.message}</p>`;
    } finally {
        // ローディングスピナーを非表示にする
        document.getElementById('loading').style.display = 'none';
    }
});
