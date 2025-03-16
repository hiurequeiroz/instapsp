// Controle das abas
document.addEventListener('DOMContentLoaded', function() {
    // Elementos
    const photoInput = document.getElementById('photoInput');
    const imagePreview = document.getElementById('imagePreview');
    const emptyPreview = document.querySelector('.empty-preview');
    const previewContainer = document.querySelector('.preview-container');
    const filtersSection = document.querySelector('.filters-section');
    const uploadForm = document.getElementById('uploadForm');
    const filterOptions = document.querySelectorAll('.filter-option');
    const selectedFilterInput = document.getElementById('selectedFilter');

    // Controle das abas
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            // Remove active de todas as abas
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            button.classList.add('active');

            // Esconde todos os conteúdos
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });

            // Mostra o conteúdo selecionado
            const contentId = `${button.dataset.tab}-content`;
            document.getElementById(contentId).style.display = 'block';
        });
    });

    // Preview de imagem
    if (photoInput) {
        photoInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Atualiza a imagem principal
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    emptyPreview.style.display = 'none';

                    // Atualiza os previews dos filtros
                    document.querySelectorAll('.filter-preview').forEach(preview => {
                        preview.src = e.target.result;
                    });
                };
                reader.readAsDataURL(file);
            } else {
                // Se nenhum arquivo foi selecionado, mostra o estado vazio
                imagePreview.style.display = 'none';
                emptyPreview.style.display = 'flex';
                document.querySelectorAll('.filter-preview').forEach(preview => {
                    preview.src = defaultImage;
                });
            }
        });
    }

    // Seleção de filtros
    filterOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove seleção anterior
            filterOptions.forEach(opt => opt.classList.remove('selected'));
            // Seleciona o novo filtro
            this.classList.add('selected');
            
            // Atualiza o input hidden
            selectedFilterInput.value = this.dataset.filter;

            // Aplica o filtro na preview principal
            const filterValue = this.dataset.filter;
            switch(filterValue) {
                case 'grayscale':
                    imagePreview.style.filter = 'grayscale(100%)';
                    break;
                case 'sepia':
                    imagePreview.style.filter = 'sepia(100%)';
                    break;
                case 'contrast':
                    imagePreview.style.filter = 'contrast(150%)';
                    break;
                case 'brightness':
                    imagePreview.style.filter = 'brightness(130%)';
                    break;
                case 'blur':
                    imagePreview.style.filter = 'blur(2px)';
                    break;
                case 'saturate':
                    imagePreview.style.filter = 'saturate(200%)';
                    break;
                case 'hue-rotate':
                    imagePreview.style.filter = 'hue-rotate(90deg)';
                    break;
                default:
                    imagePreview.style.filter = 'none';
            }
        });
    });

    // Upload do formulário
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData();
            formData.append('file', photoInput.files[0]);
            formData.append('filter', selectedFilterInput.value);
            formData.append('caption', this.caption.value);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    window.location.href = '/';  // Redireciona para a página inicial
                } else {
                    const data = await response.json();
                    alert(data.error || 'Erro ao fazer upload');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert('Erro ao fazer upload');
            }
        });
    }
});

// Validação de arquivos
function validateFile(file, type) {
    console.log('Validando arquivo:', file);
    console.log('Tipo:', type);
    console.log('Content Type:', file.type);
    
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedImageTypes = ['image/jpeg', 'image/png', 'image/gif'];
    const allowedPDFTypes = ['application/pdf'];
    
    if (file.size > maxSize) {
        alert('Arquivo muito grande. Tamanho máximo permitido: 16MB');
        return false;
    }
    
    if (type === 'pdf') {
        if (!allowedPDFTypes.includes(file.type)) {
            console.log('PDF não válido:', file.type);
            alert('Apenas arquivos PDF são permitidos');
            return false;
        }
        return true;
    }
    
    if (type === 'image') {
        if (!allowedImageTypes.includes(file.type)) {
            console.log('Imagem não válida:', file.type);
            alert('Tipo de imagem não permitido. Use: JPG, PNG ou GIF');
            return false;
        }
        return true;
    }
    
    return false;
}