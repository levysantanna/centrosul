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
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const nome = document.getElementById('nome').value.trim();
        const email = document.getElementById('email').value.trim();
        const mensagem = document.getElementById('mensagem').value.trim();
        
        if (nome === '' || email === '' || mensagem === '') {
            alert('Por favor, preencha todos os campos do formulário.');
            return;
        }
        
        // Validação básica de email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Por favor, insira um endereço de email válido.');
            return;
        }
        
        // Aqui você adicionaria o código para enviar o formulário para o servidor
        alert('Mensagem enviada com sucesso! Em breve entraremos em contato.');
        contactForm.reset();
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