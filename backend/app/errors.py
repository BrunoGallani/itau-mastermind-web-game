"""Constantes de mensagens de erro da API."""

# Autenticacao
NOT_AUTHENTICATED = "Não autenticado."
INVALID_SESSION = "Sessão inválida ou expirada."
USERNAME_EXISTS = "Username já existe."
INVALID_CREDENTIALS = "Credenciais inválidas."

# Jogo
GAME_NOT_FOUND = "Jogo não encontrado."
GAME_NOT_IN_PROGRESS = "Apenas jogos em andamento podem ser abandonados."
GAME_ALREADY_FINISHED = "O jogo já terminou com status: {status}."

# Generico
INTERNAL_SERVER_ERROR = "Erro interno do servidor."

# Validacao (schemas)
USERNAME_LENGTH = "Username deve ter entre 3 e 50 caracteres."
PASSWORD_LENGTH = "Senha deve ter pelo menos 6 caracteres."
GUESS_LENGTH = "A tentativa deve conter exatamente {length} cores."
INVALID_COLOR = "Cor inválida: '{color}'. Cores válidas: {valid_colors}"
