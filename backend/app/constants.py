"""Constantes de mensagens da API organizadas por dominio."""

from enum import StrEnum


class AuthError(StrEnum):
    NOT_AUTHENTICATED = "Não autenticado."
    INVALID_SESSION = "Sessão inválida ou expirada."
    USERNAME_EXISTS = "Username já existe."
    INVALID_CREDENTIALS = "Credenciais inválidas."


class AuthMessage(StrEnum):
    REGISTER_SUCCESS = "Usuário registrado com sucesso!"
    LOGIN_SUCCESS = "Login realizado com sucesso!"
    LOGOUT_SUCCESS = "Logout realizado com sucesso!"


class GameError(StrEnum):
    NOT_FOUND = "Jogo não encontrado."
    NOT_IN_PROGRESS = "Apenas jogos em andamento podem ser abandonados."
    ALREADY_FINISHED = "O jogo já terminou com status: {status}."


class GameMessage(StrEnum):
    CREATED = "Jogo criado! Você tem 10 tentativas. Boa sorte!"
    ABANDONED = "Jogo abandonado."


class ValidationError(StrEnum):
    USERNAME_LENGTH = "Username deve ter entre 3 e 50 caracteres."
    PASSWORD_LENGTH = "Senha deve ter pelo menos 6 caracteres."
    GUESS_LENGTH = "A tentativa deve conter exatamente {length} cores."
    INVALID_COLOR = "Cor inválida: '{color}'. Cores válidas: {valid_colors}"


class HttpError(StrEnum):
    INTERNAL_SERVER_ERROR = "Erro interno do servidor."


SESSION_COOKIE_KEY = "session_id"
SECONDS_PER_HOUR = 3600


class HttpMeta(StrEnum):
    PROBLEM_TYPE_BLANK = "about:blank"
    PROBLEM_CONTENT_TYPE = "application/problem+json"
    STATUS_TITLE_DEFAULT = "Erro"
    STATUS_TITLE_400 = "Requisição Inválida"
    STATUS_TITLE_401 = "Não Autenticado"
    STATUS_TITLE_403 = "Acesso Negado"
    STATUS_TITLE_404 = "Não Encontrado"
    STATUS_TITLE_422 = "Erro de Validação"
    STATUS_TITLE_500 = "Erro Interno"


STATUS_TITLES: dict[int, str] = {
    400: HttpMeta.STATUS_TITLE_400,
    401: HttpMeta.STATUS_TITLE_401,
    403: HttpMeta.STATUS_TITLE_403,
    404: HttpMeta.STATUS_TITLE_404,
    422: HttpMeta.STATUS_TITLE_422,
    500: HttpMeta.STATUS_TITLE_500,
}
