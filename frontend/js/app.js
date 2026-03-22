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

async function handleLogin(event) {
    event.preventDefault();
    clearFieldErrors('login');

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    let hasError = false;
    if (username.length < 3 || username.length > 50) {
        showFieldError('login-username-error', 'Usuário deve ter entre 3 e 50 caracteres.');
        hasError = true;
    }
    if (password.length < 6) {
        showFieldError('login-password-error', 'Senha deve ter no mínimo 6 caracteres.');
        hasError = true;
    }
    if (hasError) return;

    const btn = document.getElementById('login-btn');
    btn.disabled = true;
    btn.textContent = 'Entrando...';

    try {
        await login(username, password);
        await checkAuth();
        showSection('dashboard');
        showSuccess(`Bem-vindo, ${currentUser.username}!`);
    } catch (error) {
        showError(error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Entrar';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    clearFieldErrors('register');

    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-password-confirm').value;

    let hasError = false;
    if (username.length < 3 || username.length > 50) {
        showFieldError('register-username-error', 'Usuário deve ter entre 3 e 50 caracteres.');
        hasError = true;
    }
    if (password.length < 6) {
        showFieldError('register-password-error', 'Senha deve ter no mínimo 6 caracteres.');
        hasError = true;
    }
    if (password !== confirm) {
        showFieldError('register-confirm-error', 'As senhas não conferem.');
        hasError = true;
    }
    if (hasError) return;

    const btn = document.getElementById('register-btn');
    btn.disabled = true;
    btn.textContent = 'Cadastrando...';

    try {
        await register(username, password);
        await checkAuth();
        showSection('dashboard');
        showSuccess('Conta criada com sucesso!');
    } catch (error) {
        showError(error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Cadastrar';
    }
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

    if (sectionId === 'ranking') loadRanking();
    if (sectionId === 'history') loadMyGames();
    if (sectionId === 'dashboard') {
        loadUserStats();
        loadMiniRanking();
    }
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

    if (gameStatus === 'idle') {
        statusDiv.innerHTML = '<p>Clique em "Iniciar Novo Jogo" na tela inicial para começar.</p>';
        statusDiv.className = 'game-status';
        colorPicker.style.display = 'none';
        currentGuessDiv.style.display = 'none';
    } else if (gameStatus === 'in_progress') {
        statusDiv.innerHTML = `<p><strong>Jogo em andamento!</strong> Tentativas restantes: <strong>${attemptsLeft}</strong></p>`;
        statusDiv.className = 'game-status in-progress';
        colorPicker.style.display = 'block';
        currentGuessDiv.style.display = 'block';
    } else {
        statusDiv.style.display = 'none';
        colorPicker.style.display = 'none';
        currentGuessDiv.style.display = 'none';
    }
}

function updateCurrentGuessUI() {
    const slotsDiv = document.getElementById('guess-slots');
    const submitBtn = document.getElementById('submit-btn');
    const labels = ['A', 'B', 'C', 'D'];

    let html = '';
    for (let i = 0; i < 4; i++) {
        if (currentGuess[i]) {
            const color = COLOR_MAP[currentGuess[i]];
            html += `<div class="slot-wrapper"><span class="slot-label">${labels[i]}</span><div class="slot filled" style="background-color: ${color};"></div></div>`;
        } else {
            html += `<div class="slot-wrapper"><span class="slot-label">${labels[i]}</span><div class="slot empty"></div></div>`;
        }
    }
    slotsDiv.innerHTML = html;
    submitBtn.disabled = currentGuess.length !== 4;
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
                ${guess.colors.map((c, i) => `<div class="color-circle-wrapper"><span class="circle-label">${['A','B','C','D'][i]}</span><div class="color-circle" style="background-color: ${COLOR_MAP[c]};"></div></div>`).join('')}
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
            const colorsHtml = secretCode.map((c, i) =>
                `<div class="color-circle-wrapper"><span class="circle-label">${['A','B','C','D'][i]}</span><div class="color-circle" style="background-color: ${COLOR_MAP[c]};"></div></div>`
            ).join('');
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
                <td class="status-${game.status}">
                    ${game.status === 'won' ? '✓ Vitória' : game.status === 'lost' ? '✗ Derrota' : '⏳ Em andamento'}
                </td>
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

function formatDate(isoString) {
    if (!isoString) return '-';
    return new Date(isoString).toLocaleDateString('pt-BR');
}


// ── Ranking ─────────────────────────────────────────────

function formatDuration(seconds) {
    if (seconds === null || seconds === undefined) return '-';
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    if (min === 0) return `${sec}s`;
    return `${min}m ${sec}s`;
}

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
                <td class="status-${game.status}">${game.status === 'won' ? '✓ Vitória' : '✗ Derrota'}</td>
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
    setTimeout(hideError, 5000);
}

function hideError() {
    document.getElementById('error-toast').style.display = 'none';
}

function showSuccess(message) {
    const toast = document.getElementById('success-toast');
    document.getElementById('success-message').textContent = message;
    toast.style.display = 'flex';
    setTimeout(hideSuccess, 3000);
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

function setupAuthValidation() {
    const loginUsername = document.getElementById('login-username');
    const loginPassword = document.getElementById('login-password');

    loginUsername.addEventListener('blur', () => {
        const value = loginUsername.value.trim();
        if (value && (value.length < 3 || value.length > 50)) {
            showFieldError('login-username-error', 'Usuário deve ter entre 3 e 50 caracteres.');
            loginUsername.classList.add('invalid');
        } else {
            showFieldError('login-username-error', '');
            loginUsername.classList.remove('invalid');
        }
    });

    loginPassword.addEventListener('blur', () => {
        if (loginPassword.value && loginPassword.value.length < 6) {
            showFieldError('login-password-error', 'Senha deve ter no mínimo 6 caracteres.');
            loginPassword.classList.add('invalid');
        } else {
            showFieldError('login-password-error', '');
            loginPassword.classList.remove('invalid');
        }
    });

    const regUsername = document.getElementById('register-username');
    const regPassword = document.getElementById('register-password');
    const regConfirm = document.getElementById('register-password-confirm');

    regUsername.addEventListener('blur', () => {
        const value = regUsername.value.trim();
        if (value && (value.length < 3 || value.length > 50)) {
            showFieldError('register-username-error', 'Usuário deve ter entre 3 e 50 caracteres.');
            regUsername.classList.add('invalid');
        } else {
            showFieldError('register-username-error', '');
            regUsername.classList.remove('invalid');
        }
    });

    regPassword.addEventListener('blur', () => {
        if (regPassword.value && regPassword.value.length < 6) {
            showFieldError('register-password-error', 'Senha deve ter no mínimo 6 caracteres.');
            regPassword.classList.add('invalid');
        } else {
            showFieldError('register-password-error', '');
            regPassword.classList.remove('invalid');
        }
    });

    regConfirm.addEventListener('blur', () => {
        if (regConfirm.value && regConfirm.value !== regPassword.value) {
            showFieldError('register-confirm-error', 'As senhas não conferem.');
            regConfirm.classList.add('invalid');
        } else {
            showFieldError('register-confirm-error', '');
            regConfirm.classList.remove('invalid');
        }
    });
}
