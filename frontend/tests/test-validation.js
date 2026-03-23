describe('validateUsername', () => {
    it('retorna erro para string vazia', () => {
        assertTrue(validateUsername('').length > 0);
    });

    it('retorna erro para username com 2 caracteres', () => {
        assertTrue(validateUsername('ab').length > 0);
    });

    it('aceita username com 3 caracteres', () => {
        assertEqual(validateUsername('abc'), '');
    });

    it('aceita username com 50 caracteres', () => {
        assertEqual(validateUsername('a'.repeat(50)), '');
    });

    it('retorna erro para username com 51 caracteres', () => {
        assertTrue(validateUsername('a'.repeat(51)).length > 0);
    });

    it('faz trim do valor antes de validar', () => {
        assertTrue(validateUsername('  ab  ').length > 0);
    });

    it('retorna erro para null', () => {
        assertTrue(validateUsername(null).length > 0);
    });

    it('retorna erro para undefined', () => {
        assertTrue(validateUsername(undefined).length > 0);
    });
});

describe('validatePassword', () => {
    it('retorna erro para string vazia', () => {
        assertTrue(validatePassword('').length > 0);
    });

    it('retorna erro para senha com 5 caracteres', () => {
        assertTrue(validatePassword('12345').length > 0);
    });

    it('aceita senha com 6 caracteres', () => {
        assertEqual(validatePassword('123456'), '');
    });

    it('aceita senha longa', () => {
        assertEqual(validatePassword('a'.repeat(100)), '');
    });

    it('retorna erro para null', () => {
        assertTrue(validatePassword(null).length > 0);
    });
});

describe('validatePasswordConfirm', () => {
    it('retorna erro quando senhas não conferem', () => {
        assertTrue(validatePasswordConfirm('abc123', 'abc456').length > 0);
    });

    it('aceita quando senhas são iguais', () => {
        assertEqual(validatePasswordConfirm('abc123', 'abc123'), '');
    });

    it('retorna erro para confirmação vazia', () => {
        assertTrue(validatePasswordConfirm('abc123', '').length > 0);
    });

    it('retorna erro para confirmação null', () => {
        assertTrue(validatePasswordConfirm('abc123', null).length > 0);
    });
});

describe('validateGuessColors', () => {
    it('aceita 4 cores válidas', () => {
        assertEqual(validateGuessColors(['Red', 'Blue', 'Green', 'Yellow']), '');
    });

    it('retorna erro para menos de 4 cores', () => {
        assertTrue(validateGuessColors(['Red', 'Blue']).length > 0);
    });

    it('retorna erro para mais de 4 cores', () => {
        assertTrue(validateGuessColors(['Red', 'Blue', 'Green', 'Yellow', 'Orange']).length > 0);
    });

    it('retorna erro para cor inválida', () => {
        assertTrue(validateGuessColors(['Red', 'Blue', 'Green', 'Pink']).length > 0);
    });

    it('retorna erro para valor não-array', () => {
        assertTrue(validateGuessColors('Red').length > 0);
    });

    it('aceita cores repetidas', () => {
        assertEqual(validateGuessColors(['Red', 'Red', 'Red', 'Red']), '');
    });

    it('aceita todas as 6 cores válidas em grupos de 4', () => {
        assertEqual(validateGuessColors(['Orange', 'Purple', 'Red', 'Blue']), '');
    });
});
