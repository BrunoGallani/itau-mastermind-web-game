// ── Estado da aplicação ──────────────────────────────────

let currentUser = null;

let gameId = null;
let gameStatus = 'idle';
let attemptsLeft = 10;
let currentGuess = [];
let guessHistory = [];
let secretCode = null;
let gameScore = null;

let gameStartTime = null;
let timerInterval = null;

const COLOR_MAP = {
    'Red': '#e74c3c',
    'Blue': '#3498db',
    'Green': '#27ae60',
    'Yellow': '#f1c40f',
    'Orange': '#e67e22',
    'Purple': '#9b59b6',
};

const POSITION_LABELS = ['A', 'B', 'C', 'D'];

const TOAST_DURACAO_ERRO = 5000;
const TOAST_DURACAO_SUCESSO = 3000;

const SECTION_LOADERS = {
    ranking: () => loadRanking(),
    history: () => loadMyGames(),
    dashboard: () => { loadUserStats(); loadMiniRanking(); },
};


// ── Autenticação ────────────────────────────────────────

async function checkAuth() {
    try {
        currentUser = await getMe();
        updateNavbar();
        return true;
    } catch {
        currentUser = null;
        updateNavbar();
        return false;
    }
}

function updateNavbar() {
    const navLinks = document.getElementById('nav-links');
    const navUser = document.getElementById('nav-user');
    const navUsername = document.getElementById('nav-username');

    if (currentUser) {
        navLinks.style.display = 'flex';
        navUser.style.display = 'flex';
        navUsername.textContent = currentUser.username;
    } else {
        navLinks.style.display = 'none';
        navUser.style.display = 'none';
    }
}

async function withButtonLoading(buttonId, loadingText, originalText, action) {
    const btn = document.getElementById(buttonId);
    btn.disabled = true;
    btn.textContent = loadingText;
    try {
        await action();
    } catch (error) {
        showError(error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function handleLogin(event) {
    event.preventDefault();
    clearFieldErrors('login');

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    let hasError = false;
    if (username.length < VALIDATION_RULES.USERNAME_MIN || username.length > VALIDATION_RULES.USERNAME_MAX) {
        showFieldError('login-username-error', `Usuário deve ter entre ${VALIDATION_RULES.USERNAME_MIN} e ${VALIDATION_RULES.USERNAME_MAX} caracteres.`);
        hasError = true;
    }
    if (password.length < VALIDATION_RULES.PASSWORD_MIN) {
        showFieldError('login-password-error', `Senha deve ter no mínimo ${VALIDATION_RULES.PASSWORD_MIN} caracteres.`);
        hasError = true;
    }
    if (hasError) return;

    await withButtonLoading('login-btn', 'Entrando...', 'Entrar', async () => {
        await login(username, password);
        await checkAuth();
        showSection('dashboard');
        showSuccess(`Bem-vindo, ${currentUser.username}!`);
    });
}

async function handleRegister(event) {
    event.preventDefault();
    clearFieldErrors('register');

    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-password-confirm').value;

    let hasError = false;
    if (username.length < VALIDATION_RULES.USERNAME_MIN || username.length > VALIDATION_RULES.USERNAME_MAX) {
        showFieldError('register-username-error', `Usuário deve ter entre ${VALIDATION_RULES.USERNAME_MIN} e ${VALIDATION_RULES.USERNAME_MAX} caracteres.`);
        hasError = true;
    }
    if (password.length < VALIDATION_RULES.PASSWORD_MIN) {
        showFieldError('register-password-error', `Senha deve ter no mínimo ${VALIDATION_RULES.PASSWORD_MIN} caracteres.`);
        hasError = true;
    }
    if (password !== confirm) {
        showFieldError('register-confirm-error', 'As senhas não conferem.');
        hasError = true;
    }
    if (hasError) return;

    await withButtonLoading('register-btn', 'Cadastrando...', 'Cadastrar', async () => {
        await register(username, password);
        await checkAuth();
        showSection('dashboard');
        showSuccess('Conta criada com sucesso!');
    });
}

async function handleLogout() {
    try { await logout(); } catch { /* limpa estado local mesmo se falhar */ }

    currentUser = null;
    resetGameState();
    updateNavbar();
    showSection('auth');
    showSuccess('Até logo!');
}

function showAuthForm(formType) {
    document.getElementById('login-form').style.display = formType === 'register' ? 'none' : 'block';
    document.getElementById('register-form').style.display = formType === 'register' ? 'block' : 'none';
    clearFieldErrors('login');
    clearFieldErrors('register');
}

function showFieldError(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) el.textContent = message;
}

function clearFieldErrors(prefix) {
    document.querySelectorAll(`#${prefix}-form .field-error`).forEach(el => {
        el.textContent = '';
    });
}

function resetGameState() {
    gameId = null;
    gameStatus = 'idle';
    attemptsLeft = 10;
    currentGuess = [];
    guessHistory = [];
    secretCode = null;
    gameScore = null;
    stopTimer();
}

function startTimer() {
    gameStartTime = new Date();
    const timerDiv = document.getElementById('game-timer');
    const timerValue = document.getElementById('timer-value');

    timerDiv.style.display = 'block';
    timerValue.textContent = '00:00';

    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - gameStartTime.getTime()) / 1000);
        const min = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const sec = String(elapsed % 60).padStart(2, '0');
        timerValue.textContent = `${min}:${sec}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}


// ── Navegação ───────────────────────────────────────────

function showSection(sectionId) {
    const protectedSections = ['dashboard', 'game', 'history'];
    if (protectedSections.includes(sectionId) && !currentUser) {
        showSection('auth');
        return;
    }

    // Alterna tipo dos inputs de senha para evitar popup de gerenciadores de senha
    ['login-password', 'register-password', 'register-password-confirm'].forEach(id => {
        const input = document.getElementById(id);
        if (input) input.type = sectionId === 'auth' ? 'password' : 'text';
    });

    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');

    const target = document.getElementById(sectionId);
    if (target) target.style.display = 'block';

    const loader = SECTION_LOADERS[sectionId];
    if (loader) loader();
}


// ── Jogo ────────────────────────────────────────────────

async function startNewGame() {
    try {
        const response = await createGame();

        gameId = response.game_id;
        gameStatus = 'in_progress';
        attemptsLeft = 10;
        currentGuess = [];
        guessHistory = [];
        secretCode = null;
        gameScore = null;

        startTimer();
        updateGameUI();
        showSection('game');
    } catch (error) {
        showError('Erro ao criar jogo: ' + error.message);
    }
}

function selectColor(color) {
    if (gameStatus !== 'in_progress' || currentGuess.length >= 4) return;
    currentGuess.push(color);
    updateCurrentGuessUI();
}

function removeLastColor() {
    currentGuess.pop();
    updateCurrentGuessUI();
}

function clearCurrentGuess() {
    currentGuess = [];
    updateCurrentGuessUI();
}

async function sendGuess() {
    if (!gameId || currentGuess.length !== 4) return;

    try {
        const response = await submitGuess(gameId, currentGuess);

        guessHistory.push({
            attempt_number: response.attempt_number,
            colors: [...currentGuess],
            feedback: response.feedback,
        });

        gameStatus = response.status;
        attemptsLeft = response.attempts_left;
        if (response.secret_code) secretCode = response.secret_code;
        if (response.score !== undefined) gameScore = response.score;
        if (gameStatus !== 'in_progress') stopTimer();

        currentGuess = [];
        updateGameUI();
    } catch (error) {
        showError('Erro ao enviar tentativa: ' + error.message);
    }
}


// ── Interface do jogo ───────────────────────────────────

function updateGameUI() {
    updateGameStatus();
    updateCurrentGuessUI();
    updateGuessHistory();
    updateGameResult();
}

function updateGameStatus() {
    const statusDiv = document.getElementById('game-status');
    const colorPicker = document.getElementById('color-picker');
    const currentGuessDiv = document.getElementById('current-guess');

    const statusConfig = {
        idle: {
            html: '<p>Clique em "Iniciar Novo Jogo" na tela inicial para começar.</p>',
            className: 'game-status',
            showPicker: false,
        },
        in_progress: {
            html: `<p><strong>Jogo em andamento!</strong> Tentativas restantes: <strong>${attemptsLeft}</strong></p>`,
            className: 'game-status in-progress',
            showPicker: true,
        },
    };

    const config = statusConfig[gameStatus];
    if (config) {
        statusDiv.style.display = '';
        statusDiv.innerHTML = config.html;
        statusDiv.className = config.className;
        colorPicker.style.display = config.showPicker ? 'block' : 'none';
        currentGuessDiv.style.display = config.showPicker ? 'block' : 'none';
    } else {
        statusDiv.style.display = 'none';
        colorPicker.style.display = 'none';
        currentGuessDiv.style.display = 'none';
    }
}

function updateCurrentGuessUI() {
    const slotsDiv = document.getElementById('guess-slots');
    const submitBtn = document.getElementById('submit-btn');

    let html = '';
    for (let i = 0; i < 4; i++) {
        if (currentGuess[i]) {
            const color = COLOR_MAP[currentGuess[i]];
            html += `<div class="slot-wrapper"><span class="slot-label">${POSITION_LABELS[i]}</span><div class="slot filled" style="background-color: ${color};"></div></div>`;
        } else {
            html += `<div class="slot-wrapper"><span class="slot-label">${POSITION_LABELS[i]}</span><div class="slot empty"></div></div>`;
        }
    }
    slotsDiv.innerHTML = html;
    submitBtn.disabled = currentGuess.length !== 4;
}

function renderColorCircle(color, index) {
    return `<div class="color-circle-wrapper"><span class="circle-label">${POSITION_LABELS[index]}</span><div class="color-circle" style="background-color: ${COLOR_MAP[color]};"></div></div>`;
}

function updateGuessHistory() {
    const listDiv = document.getElementById('guesses-list');

    if (guessHistory.length === 0) {
        listDiv.innerHTML = '<p class="empty-message">Nenhuma tentativa ainda.</p>';
        return;
    }

    listDiv.innerHTML = guessHistory.map(guess => `
        <div class="guess-row">
            <span class="attempt-number">#${guess.attempt_number}</span>
            <div class="colors">
                ${guess.colors.map((c, i) => renderColorCircle(c, i)).join('')}
            </div>
            <div class="feedback">${renderFeedback(guess.feedback)}</div>
        </div>
    `).join('');
}

function renderFeedback(feedback) {
    let html = '';
    for (let i = 0; i < feedback.black_pegs; i++) {
        html += '<div class="peg black" title="Cor e posição corretas"></div>';
    }
    for (let i = 0; i < feedback.white_pegs; i++) {
        html += '<div class="peg white" title="Cor correta, posição errada"></div>';
    }
    return html;
}

function updateGameResult() {
    const resultDiv = document.getElementById('game-result');
    const titleEl = document.getElementById('result-title');
    const messageEl = document.getElementById('result-message');
    const scoreEl = document.getElementById('result-score');
    const secretEl = document.getElementById('secret-code-reveal');
    const timerDiv = document.getElementById('game-timer');

    if (gameStatus === 'won' || gameStatus === 'lost') {
        resultDiv.style.display = 'block';
        resultDiv.className = `game-result ${gameStatus}`;
        timerDiv.style.display = 'none';

        if (gameStatus === 'won') {
            titleEl.textContent = '🎉 Parabéns! Você venceu!';
            messageEl.textContent = `Você descobriu o código em ${guessHistory.length} tentativa(s)!`;
            scoreEl.textContent = `Pontuação: ${gameScore !== null ? gameScore : 0} pontos`;
        } else {
            titleEl.textContent = '😔 Que pena! Você perdeu.';
            messageEl.textContent = 'Não se preocupe, tente novamente!';
            scoreEl.textContent = 'Pontuação: 0 pontos';
        }

        if (secretCode) {
            const colorsHtml = secretCode.map((c, i) => renderColorCircle(c, i)).join('');
            secretEl.innerHTML = `<p>O código secreto era:</p><div class="secret-colors">${colorsHtml}</div>`;
        }
    } else {
        resultDiv.style.display = 'none';
    }
}


// ── Dashboard ───────────────────────────────────────────

async function loadUserStats() {
    const statsCard = document.getElementById('user-stats');
    const welcomeUsername = document.getElementById('welcome-username');

    if (!currentUser) {
        statsCard.style.display = 'none';
        return;
    }

    welcomeUsername.textContent = currentUser.username;

    try {
        const stats = await getMeStats();
        document.getElementById('user-total-games').textContent = stats.total_games;
        document.getElementById('user-wins').textContent = stats.wins;
        document.getElementById('user-losses').textContent = stats.losses;
        document.getElementById('user-best-score').textContent = stats.best_score !== null ? stats.best_score : '-';
        statsCard.style.display = 'block';
    } catch {
        statsCard.style.display = 'none';
    }
}


// ── Histórico ───────────────────────────────────────────

function getStatusBadge(status) {
    if (status === 'won') return '✓ Vitória';
    if (status === 'lost') return '✗ Derrota';
    return '⏳ Em andamento';
}

async function loadMyGames() {
    const tableBody = document.getElementById('history-table-body');

    try {
        const games = await getMyGames();

        if (games.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="empty-message">Você ainda não jogou nenhuma partida.</td></tr>';
            return;
        }

        tableBody.innerHTML = games.map((game, index) => `
            <tr>
                <td>${index + 1}</td>
                <td class="status-${game.status}">${getStatusBadge(game.status)}</td>
                <td>${game.attempts_used} / ${game.max_attempts}</td>
                <td>${game.score !== null ? game.score : '-'}</td>
                <td>${formatDuration(game.duration_seconds)}</td>
                <td>${formatDate(game.started_at)}</td>
            </tr>
        `).join('');
    } catch (error) {
        tableBody.innerHTML = `<tr><td colspan="6" class="error">Erro ao carregar histórico: ${error.message}</td></tr>`;
    }
}


// ── Ranking ─────────────────────────────────────────────

async function loadRanking() {
    const tableBody = document.getElementById('ranking-table-body');
    const totalGames = document.getElementById('total-games');
    const totalWins = document.getElementById('total-wins');
    const totalLosses = document.getElementById('total-losses');

    try {
        const games = await getRanking();

        totalGames.textContent = games.length;
        totalWins.textContent = games.filter(g => g.status === 'won').length;
        totalLosses.textContent = games.filter(g => g.status === 'lost').length;

        if (games.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="empty-message">Nenhuma partida finalizada ainda.</td></tr>';
            return;
        }

        tableBody.innerHTML = games.map((game, index) => `
            <tr>
                <td>${index + 1}º</td>
                <td>${game.username}</td>
                <td class="status-${game.status}">${getStatusBadge(game.status)}</td>
                <td>${game.attempts_used} / ${game.max_attempts}</td>
                <td>${game.score !== null ? game.score : '-'}</td>
                <td>${formatDuration(game.duration_seconds)}</td>
            </tr>
        `).join('');
    } catch (error) {
        tableBody.innerHTML = `<tr><td colspan="6" class="error">Erro ao carregar ranking: ${error.message}</td></tr>`;
    }
}

async function loadMiniRanking() {
    const listDiv = document.getElementById('mini-ranking-list');

    try {
        const games = await getRanking();
        const recent = games.slice(0, 5);

        if (recent.length === 0) {
            listDiv.innerHTML = '<p class="empty-message">Nenhuma partida finalizada ainda.</p>';
            return;
        }

        listDiv.innerHTML = recent.map(game => `
            <div class="ranking-item ${game.status}">
                <span>${game.status === 'won' ? '🏆' : '💔'} ${game.username} — ${game.status === 'won' ? 'Vitória' : 'Derrota'}</span>
                <span>${game.score !== null ? game.score + ' pts' : '-'}</span>
            </div>
        `).join('');
    } catch {
        listDiv.innerHTML = '<p class="error">Não foi possível carregar o ranking.</p>';
    }
}


// ── Notificações ────────────────────────────────────────

function showError(message) {
    const toast = document.getElementById('error-toast');
    document.getElementById('error-message').textContent = message;
    toast.style.display = 'flex';
    setTimeout(hideError, TOAST_DURACAO_ERRO);
}

function hideError() {
    document.getElementById('error-toast').style.display = 'none';
}

function showSuccess(message) {
    const toast = document.getElementById('success-toast');
    document.getElementById('success-message').textContent = message;
    toast.style.display = 'flex';
    setTimeout(hideSuccess, TOAST_DURACAO_SUCESSO);
}

function hideSuccess() {
    document.getElementById('success-toast').style.display = 'none';
}


// ── Inicialização ───────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    setupAuthValidation();

    const authenticated = await checkAuth();
    showSection(authenticated ? 'dashboard' : 'auth');
});

function addBlurValidation(inputId, errorId, validate) {
    const input = document.getElementById(inputId);
    input.addEventListener('blur', () => {
        const errorMsg = validate(input);
        showFieldError(errorId, errorMsg);
        input.classList.toggle('invalid', errorMsg.length > 0);
    });
}

function setupAuthValidation() {
    addBlurValidation('login-username', 'login-username-error', (input) => {
        const value = input.value.trim();
        return value ? validateUsername(value) : '';
    });

    addBlurValidation('login-password', 'login-password-error', (input) =>
        input.value ? validatePassword(input.value) : ''
    );

    addBlurValidation('register-username', 'register-username-error', (input) => {
        const value = input.value.trim();
        return value ? validateUsername(value) : '';
    });

    addBlurValidation('register-password', 'register-password-error', (input) =>
        input.value ? validatePassword(input.value) : ''
    );

    addBlurValidation('register-password-confirm', 'register-confirm-error', (input) =>
        input.value ? validatePasswordConfirm(
            document.getElementById('register-password').value,
            input.value
        ) : ''
    );
}
