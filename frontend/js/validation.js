// Manter sincronizado com VALID_COLORS no backend (game_logic.py)
const VALID_COLORS = ['Red', 'Blue', 'Green', 'Yellow', 'Orange', 'Purple'];

function validateUsername(value) {
    if (!value || value.trim().length === 0) return 'Usuário é obrigatório.';
    const trimmed = value.trim();
    if (trimmed.length < 3) return 'Usuário deve ter no mínimo 3 caracteres.';
    if (trimmed.length > 50) return 'Usuário deve ter no máximo 50 caracteres.';
    return '';
}

function validatePassword(value) {
    if (!value || value.length === 0) return 'Senha é obrigatória.';
    if (value.length < 6) return 'Senha deve ter no mínimo 6 caracteres.';
    return '';
}

function validatePasswordConfirm(password, confirm) {
    if (!confirm || confirm.length === 0) return 'Confirmação de senha é obrigatória.';
    if (password !== confirm) return 'As senhas não conferem.';
    return '';
}

function validateGuessColors(colors) {
    if (!Array.isArray(colors)) return 'Cores devem ser um array.';
    if (colors.length !== 4) return 'Selecione exatamente 4 cores.';
    for (const color of colors) {
        if (!VALID_COLORS.includes(color)) return `Cor inválida: ${color}.`;
    }
    return '';
}

function formatDurationUtil(seconds) {
    if (seconds === null || seconds === undefined) return '-';
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    if (min === 0) return `${sec}s`;
    return `${min}m ${sec}s`;
}

function formatDateUtil(isoString) {
    if (!isoString) return '-';
    return new Date(isoString).toLocaleDateString('pt-BR');
}
