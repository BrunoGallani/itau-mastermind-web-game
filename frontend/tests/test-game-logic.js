describe('VALID_COLORS', () => {
    it('contém exatamente 6 cores', () => {
        assertEqual(VALID_COLORS.length, 6);
    });

    it('contém Red', () => assertTrue(VALID_COLORS.includes('Red')));
    it('contém Blue', () => assertTrue(VALID_COLORS.includes('Blue')));
    it('contém Green', () => assertTrue(VALID_COLORS.includes('Green')));
    it('contém Yellow', () => assertTrue(VALID_COLORS.includes('Yellow')));
    it('contém Orange', () => assertTrue(VALID_COLORS.includes('Orange')));
    it('contém Purple', () => assertTrue(VALID_COLORS.includes('Purple')));
});

describe('COLOR_MAP', () => {
    it('tem mapeamento para todas as 6 cores válidas', () => {
        for (const color of VALID_COLORS) {
            assertTrue(COLOR_MAP[color] !== undefined, `COLOR_MAP não tem ${color}`);
        }
    });

    it('todos os valores são códigos hexadecimais', () => {
        for (const color of VALID_COLORS) {
            assertTrue(COLOR_MAP[color].startsWith('#'), `${color} não começa com #`);
            assertEqual(COLOR_MAP[color].length, 7, `${color} não tem 7 caracteres`);
        }
    });
});

describe('formatDuration', () => {
    it('retorna "-" para null', () => assertEqual(formatDuration(null), '-'));
    it('retorna "-" para undefined', () => assertEqual(formatDuration(undefined), '-'));
    it('formata 0 segundos como "0s"', () => assertEqual(formatDuration(0), '0s'));
    it('formata 45 segundos como "45s"', () => assertEqual(formatDuration(45), '45s'));
    it('formata 60 segundos como "1m 0s"', () => assertEqual(formatDuration(60), '1m 0s'));
    it('formata 65 segundos como "1m 5s"', () => assertEqual(formatDuration(65), '1m 5s'));
    it('formata 3600 segundos como "60m 0s"', () => assertEqual(formatDuration(3600), '60m 0s'));
    it('formata 125 segundos como "2m 5s"', () => assertEqual(formatDuration(125), '2m 5s'));
});

describe('formatDate', () => {
    it('retorna "-" para null', () => assertEqual(formatDate(null), '-'));
    it('retorna "-" para string vazia', () => assertEqual(formatDate(''), '-'));

    it('formata data ISO em pt-BR', () => {
        const result = formatDate('2026-03-22T10:30:00');
        assertTrue(result.includes('22'), `Data deve conter "22", recebeu "${result}"`);
        assertTrue(result.includes('2026'), `Data deve conter "2026", recebeu "${result}"`);
    });
});

describe('formatDateTime', () => {
    it('retorna "-" para null', () => assertEqual(formatDateTime(null), '-'));
    it('retorna "-" para string vazia', () => assertEqual(formatDateTime(''), '-'));
    it('retorna "-" para undefined', () => assertEqual(formatDateTime(undefined), '-'));

    it('formata data ISO com hora em pt-BR', () => {
        const result = formatDateTime('2026-03-22T10:30:00');
        assertTrue(result.includes('22'), `Data deve conter "22", recebeu "${result}"`);
        assertTrue(result.includes('10'), `Data deve conter hora "10", recebeu "${result}"`);
        assertTrue(result.includes('30'), `Data deve conter minuto "30", recebeu "${result}"`);
    });
});

describe('getStatusBadge', () => {
    it('retorna badge de vitória para "won"', () => {
        assertTrue(getStatusBadge('won').includes('Vitória'));
    });
    it('retorna badge de derrota para "lost"', () => {
        assertTrue(getStatusBadge('lost').includes('Derrota'));
    });
    it('retorna badge de abandonado para "abandoned"', () => {
        assertTrue(getStatusBadge('abandoned').includes('Abandonado'));
    });
    it('retorna badge de em andamento para "in_progress"', () => {
        assertTrue(getStatusBadge('in_progress').includes('Em andamento'));
    });
});

describe('renderFeedback', () => {
    it('renderiza 4 pinos pretos para acerto total', () => {
        const html = renderFeedback({ black_pegs: 4, white_pegs: 0 });
        assertEqual((html.match(/peg black/g) || []).length, 4);
        assertEqual((html.match(/peg white/g) || []).length, 0);
    });

    it('renderiza 0 pinos para erro total', () => {
        assertEqual(renderFeedback({ black_pegs: 0, white_pegs: 0 }), '');
    });

    it('renderiza 2 pretos e 1 branco', () => {
        const html = renderFeedback({ black_pegs: 2, white_pegs: 1 });
        assertEqual((html.match(/peg black/g) || []).length, 2);
        assertEqual((html.match(/peg white/g) || []).length, 1);
    });

    it('renderiza apenas pinos brancos', () => {
        const html = renderFeedback({ black_pegs: 0, white_pegs: 3 });
        assertEqual((html.match(/peg black/g) || []).length, 0);
        assertEqual((html.match(/peg white/g) || []).length, 3);
    });
});
