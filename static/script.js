// Script para efeito de rolagem suave
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            const headerOffset = 100;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Efeito de rolagem no cabeçalho
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    
    if (window.scrollY > 50) {
        header.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)';
        header.style.padding = '10px 50px';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        header.style.padding = '15px 50px';
    }
});

// Validação do formulário de contato
const contactForm = document.getElementById('contact-form');

if (contactForm) {
    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form values
        const nome = document.getElementById('nome').value.trim();
        const sobrenome = document.getElementById('sobrenome').value.trim();
        const email = document.getElementById('email').value.trim();
        const telefone = document.getElementById('telefone').value.trim();
        const cidade = document.getElementById('cidade').value.trim();
        const uf = document.getElementById('uf').value.trim();
        
        // Validate required fields
        if (!nome || !sobrenome || !email || !telefone || !cidade || !uf) {
            alert('Por favor, preencha todos os campos obrigatórios: nome, sobrenome, email, telefone, cidade e UF.');
            return;
        }
        
        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Por favor, insira um endereço de email válido.');
            return;
        }
        
        // Validate phone number (11 digits: DDD + number)
        if (!/^\d{11}$/.test(telefone)) {
            alert('Telefone deve conter 11 dígitos (DDD+telefone)');
            return;
        }
        
        const submitButton = this.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        
        try {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
            
            const formData = new FormData(this);
            const response = await fetch('/enviar', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                alert('Resposta enviada com sucesso!');
                this.reset();
            } else {
                alert(result.error || 'Erro ao enviar a resposta. Por favor, tente novamente.');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao enviar a resposta. Por favor, tente novamente.');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }
    });
}

// Animação para os cards de serviços
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Função para adicionar efeito de fade in nos elementos quando eles aparecem na tela
window.addEventListener('DOMContentLoaded', () => {
    // Adiciona a classe para os cards de serviços
    document.querySelectorAll('.servico-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `all 0.5s ease ${index * 0.1}s`;
        
        observer.observe(card);
    });
    
    // Adiciona listener para quando os cards se tornarem visíveis
    document.addEventListener('scroll', () => {
        document.querySelectorAll('.servico-card:not(.animate)').forEach(card => {
            const position = card.getBoundingClientRect();
            
            if (position.top < window.innerHeight * 0.9) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
                card.classList.add('animate');
            }
        });
    }, { passive: true });
});

document.addEventListener('DOMContentLoaded', function() {
    // Função para mostrar/esconder campos de estudo
    const estudaRadios = document.querySelectorAll('input[name="estuda"]');
    const estudoFields = document.getElementById('estudo_fields');

    estudaRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'sim') {
                estudoFields.style.display = 'flex';
                document.getElementById('curso').required = true;
                document.getElementById('instituicao').required = true;
            } else {
                estudoFields.style.display = 'none';
                document.getElementById('curso').required = false;
                document.getElementById('instituicao').required = false;
            }
        });
    });

    // Máscara para WhatsApp
    const whatsappInput = document.getElementById('whatsapp');
    if (whatsappInput) {
        whatsappInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            e.target.value = value;
        });
        whatsappInput.addEventListener('keypress', function(e) {
            if (!/[0-9]/.test(e.key) || whatsappInput.value.length >= 11) {
                e.preventDefault();
            }
        });
    }

    // Validação do formulário
    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Apenas campos obrigatórios: nome, sobrenome, email, whatsapp
            const nome = document.getElementById('nome').value.trim();
            const sobrenome = document.getElementById('sobrenome').value.trim();
            const email = document.getElementById('email').value.trim();
            const whatsapp = document.getElementById('whatsapp').value.trim();
            // Regex para 11 dígitos (DDD+telefone)
            const whatsappPattern = /^\d{11}$/;

            if (!nome) {
                showMessage('O campo Nome é obrigatório.', 'error');
                console.error('O campo Nome é obrigatório.');
                document.getElementById('nome').focus();
                return;
            }
            if (!sobrenome) {
                showMessage('O campo Sobrenome é obrigatório.', 'error');
                console.error('O campo Sobrenome é obrigatório.');
                document.getElementById('sobrenome').focus();
                return;
            }
            if (!email) {
                showMessage('O campo Email é obrigatório.', 'error');
                console.error('O campo Email é obrigatório.');
                document.getElementById('email').focus();
                return;
            }
            // Validação básica de email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showMessage('Por favor, insira um endereço de email válido.', 'error');
                console.error('Por favor, insira um endereço de email válido.');
                document.getElementById('email').focus();
                return;
            }
            if (!whatsapp) {
                showMessage('O campo WhatsApp é obrigatório.', 'error');
                console.error('O campo WhatsApp é obrigatório.');
                document.getElementById('whatsapp').focus();
                return;
            }
            if (!whatsappPattern.test(whatsapp)) {
                showMessage('Por favor, insira o WhatsApp com DDD, ex: 11999999999.', 'error');
                console.error('Por favor, insira o WhatsApp com DDD, ex: 11999999999.');
                document.getElementById('whatsapp').focus();
                return;
            }

            // Se estuda = sim, validar curso e instituição
            const estuda = document.querySelector('input[name="estuda"]:checked')?.value;
            if (estuda === 'sim') {
                const curso = document.getElementById('curso').value.trim();
                const instituicao = document.getElementById('instituicao').value.trim();
                if (!curso) {
                    showMessage('O campo Curso é obrigatório para quem estuda.', 'error');
                    document.getElementById('curso').focus();
                    return;
                }
                if (!instituicao) {
                    showMessage('O campo Instituição é obrigatório para quem estuda.', 'error');
                    document.getElementById('instituicao').focus();
                    return;
                }
            }

            const formData = new FormData(form);
            try {
                const response = await fetch('/enviar', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (response.ok) {
                    showMessage('Mensagem enviada com sucesso!', 'success');
                    form.reset();
                    estudoFields.style.display = 'none';
                } else {
                    showMessage(data.error || 'Erro ao enviar mensagem', 'error');
                }
            } catch (error) {
                showMessage('Erro ao processar a requisição', 'error');
            }
        });
    }
});

// Função para mostrar mensagens
function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    messageDiv.style.zIndex = '1050';
    messageDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}