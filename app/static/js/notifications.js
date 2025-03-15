document.addEventListener('DOMContentLoaded', function() {
    const notificationsBtn = document.getElementById('notificationsBtn');
    const notificationsDropdown = document.getElementById('notificationsDropdown');

    if (notificationsBtn && notificationsDropdown) {
        notificationsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            notificationsDropdown.classList.toggle('show');
            
            // Log para debug
            console.log('Botão clicado, dropdown:', notificationsDropdown.classList.contains('show'));
        });

        // Fechar ao clicar fora
        document.addEventListener('click', function(e) {
            if (!notificationsDropdown.contains(e.target) && !notificationsBtn.contains(e.target)) {
                notificationsDropdown.classList.remove('show');
            }
        });

        // Prevenir que cliques dentro do dropdown fechem ele
        notificationsDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    } else {
        console.error('Elementos de notificação não encontrados');
    }
}); 