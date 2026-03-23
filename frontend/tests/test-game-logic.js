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

describe('formatDurationUtil', () => {
    it('retorna "-" para null', () => assertEqual(formatDurationUtil(null), '-'));
    it('retorna "-" para undefined', () => assertEqual(formatDurationUtil(undefined), '-'));
    it('formata 0 segundos como "0s"', () => assertEqual(formatDurationUtil(0), '0s'));
    it('formata 45 segundos como "45s"', () => assertEqual(formatDurationUtil(45), '45s'));
    it('formata 60 segundos como "1m 0s"', () => assertEqual(formatDurationUtil(60), '1m 0s'));
    it('formata 65 segundos como "1m 5s"', () => assertEqual(formatDurationUtil(65), '1m 5s'));
    it('formata 3600 segundos como "60m 0s"', () => assertEqual(formatDurationUtil(3600), '60m 0s'));
    it('formata 125 segundos como "2m 5s"', () => assertEqual(formatDurationUtil(125), '2m 5s'));
});

describe('formatDateUtil', () => {
    it('retorna "-" para null', () => assertEqual(formatDateUtil(null), '-'));
    it('retorna "-" para string vazia', () => assertEqual(formatDateUtil(''), '-'));

    it('formata data ISO em pt-BR', () => {
        const result = formatDateUtil('2026-03-22T10:30:00');
        assertTrue(result.includes('22'), `Data deve conter "22", recebeu "${result}"`);
        assertTrue(result.includes('2026'), `Data deve conter "2026", recebeu "${result}"`);
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
