// ============ FUNÇÕES UTILITÁRIAS ============

/**
 * Fetch com tratamento de erros
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        return response;
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

/**
 * Mostrar mensagem de sucesso ou erro
 */
function showMessage(elementId, message, type = 'success') {
    const messageDiv = document.getElementById(elementId);
    if (messageDiv) {
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        messageDiv.style.display = 'block';
    }
}

/**
 * Esconder mensagem
 */
function hideMessage(elementId) {
    const messageDiv = document.getElementById(elementId);
    if (messageDiv) {
        messageDiv.style.display = 'none';
    }
}

/**
 * Copiar para clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showMessage('message', '✅ Copiado para a área de transferência!', 'success');
    }).catch(err => {
        showMessage('message', '❌ Erro ao copiar', 'error');
    });
}

/**
 * Download de arquivo de texto
 */
function downloadFile(content, filename = 'arquivo.txt') {
    const blob = new Blob([content], { type: 'text/plain; charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

/**
 * Validar email
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Validar senha (mínimo 6 caracteres)
 */
function isValidPassword(password) {
    return password.length >= 6;
}

/**
 * Limpar formulário
 */
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

/**
 * Validar formulário de registro
 */
function validateRegister(username, email, password) {
    if (!username || username.trim().length < 3) {
        return { valid: false, error: '❌ Usuário deve ter no mínimo 3 caracteres' };
    }
    if (!isValidEmail(email)) {
        return { valid: false, error: '❌ Email inválido' };
    }
    if (!isValidPassword(password)) {
        return { valid: false, error: '❌ Senha deve ter no mínimo 6 caracteres' };
    }
    return { valid: true };
}

/**
 * Mostrar/esconder loading spinner
 */
function toggleSpinner(show = true, elementId = 'loadingSpinner') {
    const spinner = document.getElementById(elementId);
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
}

/**
 * Formatar data brasileira
 */
function formatDateBR(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Truncar texto
 */
function truncateText(text, maxLength = 100) {
    if (text.length > maxLength) {
        return text.substring(0, maxLength) + '...';
    }
    return text;
}

/**
 * Contar caracteres em tempo real
 */
function setupCharCounter(inputId, counterId, maxChars = null) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);

    if (input && counter) {
        input.addEventListener('input', () => {
            const count = input.value.length;
            if (maxChars) {
                counter.textContent = `${count}/${maxChars}`;
                if (count > maxChars) {
                    input.value = input.value.substring(0, maxChars);
                }
            } else {
                counter.textContent = `${count} caracteres`;
            }
        });
    }
}

/**
 * Habilitar/desabilitar botão
 */
function toggleButton(buttonId, disabled = false) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = disabled;
        button.style.opacity = disabled ? '0.6' : '1';
    }
}

/**
 * Animar elemento
 */
function animateElement(elementId, animationClass = 'bounce') {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add(animationClass);
        setTimeout(() => {
            element.classList.remove(animationClass);
        }, 1000);
    }
}

/**
 * Debounce para evitar múltiplas chamadas
 */
function debounce(func, wait = 500) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle para limitar chamadas
 */
function throttle(func, limit = 1000) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============ ANIMAÇÕES CSS ============

const style = document.createElement('style');
style.textContent = `
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.bounce { animation: bounce 0.5s; }
.fadeIn { animation: fadeIn 0.3s; }
.slideIn { animation: slideIn 0.3s; }
`;
document.head.appendChild(style);

// ============ EVENT LISTENERS GLOBAIS ============

document.addEventListener('DOMContentLoaded', () => {
    console.log('VendiAI carregado com sucesso! 🚀');
    
    // Inicializar tooltips (opcional)
    initTooltips();
});

/**
 * Inicializar tooltips
 */
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltipText = e.target.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 1000;
                pointer-events: none;
            `;
            document.body.appendChild(tooltip);
            
            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - 30) + 'px';
        });
        
        element.addEventListener('mouseleave', () => {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

/**
 * Confirmar ação com dialog
 */
function confirmAction(message = 'Tem certeza?') {
    return confirm(message);
}

/**
 * Alert customizado
 */
function alertUser(message, type = 'success') {
    const alertBox = document.createElement('div');
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = message;
    alertBox.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#f59e0b'};
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s;
        max-width: 400px;
    `;
    document.body.appendChild(alertBox);
    
    setTimeout(() => {
        alertBox.style.animation = 'fadeOut 0.3s';
        setTimeout(() => alertBox.remove(), 300);
    }, 3000);
}

// ============ SETUP KEYBOARD SHORTCUTS ============

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + S para salvar (opcional)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const saveBtn = document.querySelector('[data-action="save"]');
        if (saveBtn) saveBtn.click();
    }

    // ESC para fechar modals (opcional)
    if (e.key === 'Escape') {
        const modal = document.querySelector('.modal.active');
        if (modal) {
            modal.classList.remove('active');
        }
    }
});

console.log('VendiAI JavaScript loaded! 🤖');
