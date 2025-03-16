document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pdfForm');
    if (!form) return;

    const fileInput = document.getElementById('pdfFile');
    const fileNameDisplay = document.getElementById('pdfName');

    // Preview do nome do arquivo
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            fileNameDisplay.textContent = this.files[0].name;
        } else {
            fileNameDisplay.textContent = '';
        }
    });

    // Upload do PDF
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            alert('Por favor, selecione um arquivo PDF');
            return;
        }

        const loading = document.getElementById('loading');
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', document.getElementById('title').value);
        formData.append('description', document.getElementById('description').value);

        try {
            loading.style.display = 'flex';
            
            const response = await fetch('/upload_pdf', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('Upload realizado com sucesso!');
                window.location.href = '/';
            } else {
                alert(data.error || 'Erro ao fazer upload do PDF');
            }
        } catch (error) {
            alert('Erro ao fazer upload: ' + error.message);
        } finally {
            loading.style.display = 'none';
        }
    });
}); 