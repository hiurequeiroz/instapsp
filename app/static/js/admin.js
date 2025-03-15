document.querySelectorAll('.timeline-preferences-form').forEach(form => {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const userId = this.dataset.userId;
        const selectElement = this.querySelector('.timeline-sort');
        const sortBy = selectElement.value;
        
        try {
            const response = await fetch(`/admin/users/${userId}/timeline-preferences`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sort_by: sortBy })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Mantém a opção selecionada
                selectElement.value = sortBy;
                
                // Mostra feedback
                const feedback = document.createElement('div');
                feedback.className = 'save-feedback show';
                feedback.innerHTML = `
                    <i class="fas fa-check"></i>
                    <span>Salvo com sucesso!</span>
                `;
                
                // Remove feedback anterior se existir
                const oldFeedback = this.querySelector('.save-feedback');
                if (oldFeedback) {
                    oldFeedback.remove();
                }
                
                this.appendChild(feedback);
                
                setTimeout(() => {
                    feedback.remove();
                }, 2000);
            } else {
                throw new Error(data.error || 'Erro ao salvar preferências');
            }
        } catch (error) {
            console.error('Erro ao salvar preferências:', error);
            // Reverte para a seleção anterior em caso de erro
            selectElement.value = selectElement.dataset.previousValue;
            alert('Erro ao salvar preferências. Tente novamente.');
        }
    });

    // Guarda o valor anterior quando o select muda
    const select = form.querySelector('.timeline-sort');
    select.dataset.previousValue = select.value;
    select.addEventListener('change', function() {
        this.dataset.previousValue = this.value;
    });
}); 