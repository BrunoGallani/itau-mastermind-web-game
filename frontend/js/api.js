// URL relativa (same-origin) — frontend servido pelo FastAPI
const API_URL = '';

/**
 * Extrai mensagem de erro da resposta da API.
 * O backend retorna detail como string (4xx) ou array de strings (422).
 */
function extractErrorMessage(errorBody, fallback) {
    if (!errorBody || !errorBody.detail) return fallback;
    if (Array.isArray(errorBody.detail)) return errorBody.detail.join('\n');
    return errorBody.detail;
}

async function fetchAPI(method, path, { body = null, fallbackError = 'Erro na requisição' } = {}) {
    const options = {
        method,
        credentials: 'include',
    };

    if (body !== null) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_URL}${path}`, options);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, fallbackError));
    }

    return response.json();
}

async function register(username, password) {
    return fetchAPI('POST', '/auth/register', {
        body: { username, password },
        fallbackError: 'Erro ao registrar',
    });
}

async function login(username, password) {
    return fetchAPI('POST', '/auth/login', {
        body: { username, password },
        fallbackError: 'Erro ao fazer login',
    });
}

async function logout() {
    return fetchAPI('POST', '/auth/logout', {
        fallbackError: 'Erro ao fazer logout',
    });
}

async function getMe() {
    return fetchAPI('GET', '/auth/me', { fallbackError: 'Erro ao buscar usuário' });
}

async function getMeStats() {
    return fetchAPI('GET', '/auth/me/stats', { fallbackError: 'Erro ao buscar estatísticas' });
}

async function createGame() {
    return fetchAPI('POST', '/games/', {
        body: {},
        fallbackError: 'Erro ao criar jogo',
    });
}

async function submitGuess(gameId, colors) {
    return fetchAPI('POST', `/games/${gameId}/guesses`, {
        body: { colors },
        fallbackError: 'Erro ao enviar tentativa',
    });
}

async function getGameState(gameId) {
    return fetchAPI('GET', `/games/${gameId}`, { fallbackError: 'Erro ao buscar jogo' });
}

async function getMyGames() {
    return fetchAPI('GET', '/games/my-games/', { fallbackError: 'Erro ao buscar histórico' });
}

async function getRanking() {
    return fetchAPI('GET', '/games/ranking/', { fallbackError: 'Erro ao buscar ranking' });
}

async function healthCheck() {
    try {
        const response = await fetch(`${API_URL}/health`, { credentials: 'include' });
        return response.ok;
    } catch {
        return false;
    }
}
