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

async function register(username, password) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao registrar'));
    }
    return response.json();
}

async function login(username, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao fazer login'));
    }
    return response.json();
}

async function logout() {
    const response = await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao fazer logout'));
    }
    return response.json();
}

async function getMe() {
    const response = await fetch(`${API_URL}/auth/me`, {
        credentials: 'include',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao buscar usuário'));
    }
    return response.json();
}

async function getMeStats() {
    const response = await fetch(`${API_URL}/auth/me/stats`, {
        credentials: 'include',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao buscar estatísticas'));
    }
    return response.json();
}

async function createGame() {
    const response = await fetch(`${API_URL}/games/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({}),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao criar jogo'));
    }
    return response.json();
}

async function submitGuess(gameId, colors) {
    const response = await fetch(`${API_URL}/games/${gameId}/guesses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ colors }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao enviar tentativa'));
    }
    return response.json();
}

async function getGameState(gameId) {
    const response = await fetch(`${API_URL}/games/${gameId}`, {
        credentials: 'include',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao buscar jogo'));
    }
    return response.json();
}

async function getMyGames() {
    const response = await fetch(`${API_URL}/games/my-games/`, {
        credentials: 'include',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao buscar histórico'));
    }
    return response.json();
}

async function getRanking() {
    const response = await fetch(`${API_URL}/games/ranking/`, {
        credentials: 'include',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(extractErrorMessage(error, 'Erro ao buscar ranking'));
    }
    return response.json();
}

async function healthCheck() {
    try {
        const response = await fetch(`${API_URL}/health`, { credentials: 'include' });
        return response.ok;
    } catch {
        return false;
    }
}
