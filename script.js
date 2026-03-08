async function generateImage() {
    const prompt = document.getElementById('img-prompt').value;
    const num = parseInt(document.getElementById('img-num').value);
    if (!prompt || num < 1 || num > 100) {
        alert('有効なプロンプトと枚数を入力してください (1-100)');
        return;
    }
    
    try {
        const response = await fetch('/generate_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, num_images: num })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        const results = document.getElementById('img-results');
        results.innerHTML = '';
        data.images.forEach(img => {
            const image = document.createElement('img');
            image.src = `data:image/png;base64,${img}`;
            results.appendChild(image);
        });
    } catch (e) {
        alert(`エラー: ${e.message}`);
    }
}

async function editImage() {
    const prompt = document.getElementById('edit-prompt').value;
    const files = document.getElementById('edit-images').files;
    if (!prompt || files.length === 0 || files.length > 100) {
        alert('プロンプトと画像 (1-100枚) を選択してください');
        return;
    }
    
    const formData = new FormData();
    formData.append('prompt', prompt);
    Array.from(files).forEach(file => formData.append('images', file));
    
    try {
        const response = await fetch('/edit_image', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        const results = document.getElementById('edit-results');
        results.innerHTML = '';
        data.images.forEach(img => {
            const image = document.createElement('img');
            image.src = `data:image/png;base64,${img}`;
            results.appendChild(image);
        });
    } catch (e) {
        alert(`エラー: ${e.message}`);
    }
}

async function generateVideo() {
    const prompt = document.getElementById('video-prompt').value;
    const audioText = document.getElementById('audio-text').value;
    if (!prompt) {
        alert('プロンプトを入力してください');
        return;
    }
    
    try {
        const response = await fetch('/generate_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, audio_text: audioText })
        });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error);
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const results = document.getElementById('video-results');
        results.innerHTML = '';
        const video = document.createElement('video');
        video.src = url;
        video.controls = true;
        results.appendChild(video);
    } catch (e) {
        alert(`エラー: ${e.message}`);
    }
}
