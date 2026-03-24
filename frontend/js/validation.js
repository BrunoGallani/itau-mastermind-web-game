// Manter sincronizado com VALID_COLORS no backend (game_logic.py)
const VALID_COLORS = ['Red', 'Blue', 'Green', 'Yellow', 'Orange', 'Purple'];

const VALIDATION_RULES = {
    USERNAME_MIN: 3,
    USERNAME_MAX: 50,
    PASSWORD_MIN: 6,
    GUESS_LENGTH: 4,
};

function validateUsername(value) {
    if (!value || value.trim().length === 0) return 'Usuário é obrigatório.';
    const trimmed = value.trim();
    if (trimmed.length < VALIDATION_RULES.USERNAME_MIN) return `Usuário deve ter no mínimo ${VALIDATION_RULES.USERNAME_MIN} caracteres.`;
    if (trimmed.length > VALIDATION_RULES.USERNAME_MAX) return `Usuário deve ter no máximo ${VALIDATION_RULES.USERNAME_MAX} caracteres.`;
    return '';
}

function validatePassword(value) {
    if (!value || value.length === 0) return 'Senha é obrigatória.';
    if (value.length < VALIDATION_RULES.PASSWORD_MIN) return `Senha deve ter no mínimo ${VALIDATION_RULES.PASSWORD_MIN} caracteres.`;
    return '';
}

function validatePasswordConfirm(password, confirm) {
    if (!confirm || confirm.length === 0) return 'Confirmação de senha é obrigatória.';
    if (password !== confirm) return 'As senhas não conferem.';
    return '';
}

function validateGuessColors(colors) {
    if (!Array.isArray(colors)) return 'Cores devem ser um array.';
    if (colors.length !== VALIDATION_RULES.GUESS_LENGTH) return `Selecione exatamente ${VALIDATION_RULES.GUESS_LENGTH} cores.`;
    for (const color of colors) {
        if (!VALID_COLORS.includes(color)) return `Cor inválida: ${color}.`;
    }
    return '';
}

function formatDuration(seconds) {
    if (seconds === null || seconds === undefined) return '-';
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    if (min === 0) return `${sec}s`;
    return `${min}m ${sec}s`;
}

function ensureUTC(isoString) {
    if (!isoString) return isoString;
    return isoString.endsWith('Z') ? isoString : isoString + 'Z';
}

function formatDate(isoString) {
    if (!isoString) return '-';
    return new Date(ensureUTC(isoString)).toLocaleDateString('pt-BR');
}

function formatDateTime(isoString) {
    if (!isoString) return '-';
    return new Date(ensureUTC(isoString)).toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}
