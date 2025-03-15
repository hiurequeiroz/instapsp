# InstaPSP

Um projeto didático de rede social inspirado no Instagram, desenvolvido para fins educacionais na escola.

## 🎯 Objetivo

Este projeto foi criado como uma ferramenta de ensino para demonstrar conceitos de desenvolvimento web, banco de dados e programação Python usando o framework Flask.

## 🚀 Funcionalidades

- Autenticação de usuários
- Upload de fotos com filtros
- Sistema de curtidas e comentários
- Marcação de usuários
- Painel administrativo
- Timeline personalizada
- Sistema de notificações

## 🛠️ Tecnologias

- Python 3.8+
- Flask
- SQLite
- HTML/CSS/JavaScript
- Pillow (para processamento de imagens)

## ⚙️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/hiurequeiroz/instapsp.git
cd instapsp
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com:
```
SECRET_KEY="sua-chave-secreta"
MAIL_USERNAME="seu-email@gmail.com"
MAIL_PASSWORD="sua-senha-de-app"
```

5. Inicialize o banco de dados:
```bash
flask sync-db
```

6. Execute o servidor:
```bash
flask run
```

7. Acesse no navegador:
```
http://localhost:5000
```

## 👨‍💻 Primeiros Passos

1. Crie um usuário administrador:
```bash
flask create-admin admin senha123
```

2. Faça login com as credenciais:
   - Usuário: admin
   - Senha: senha123

3. Explore as funcionalidades:
   - Faça upload de fotos
   - Aplique filtros
   - Marque outros usuários
   - Gerencie a timeline
   - Modere comentários

## 🔧 Comandos Úteis

- Criar backup do banco:
```bash
flask backup
```

- Restaurar backup:
```bash
flask restore
```

- Listar usuários:
```bash
flask list-users
```

## 📁 Estrutura do Projeto

```
compose/
├── app/
│   ├── models/      # Modelos do banco de dados
│   ├── routes/      # Rotas e views
│   ├── static/      # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/   # Templates HTML
│   └── utils/       # Utilitários
├── instance/        # Banco de dados
├── migrations/      # Migrações do banco
└── backups/         # Backups do banco
```

## 🐛 Problemas Conhecidos

- O upload de imagens muito grandes pode falhar
- Algumas animações podem travar em navegadores antigos
- O sistema de notificações precisa ser atualizado manualmente

## 👥 Contribuição

Este é um projeto didático, mas contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🎓 Uso Educacional

Este projeto foi desenvolvido para fins educacionais e pode ser livremente utilizado por professores e alunos como material de estudo.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato:
- Email: seu.email@exemplo.com
- GitHub: [@hiurequeiroz](https://github.com/hiurequeiroz)