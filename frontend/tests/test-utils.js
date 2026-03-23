const testResults = { passed: 0, failed: 0, errors: [], currentGroup: '' };

function describe(name, fn) {
    testResults.currentGroup = name;
    console.group(`📦 ${name}`);

    const output = document.getElementById('test-output');
    if (output) output.innerHTML += `<h3>📦 ${name}</h3>`;

    fn();
    console.groupEnd();
}

function it(name, fn) {
    const output = document.getElementById('test-output');

    try {
        fn();
        testResults.passed++;
        console.log(`  ✅ ${name}`);
        if (output) output.innerHTML += `<div class="test-pass">✅ ${name}</div>`;
    } catch (e) {
        testResults.failed++;
        testResults.errors.push({ group: testResults.currentGroup, test: name, error: e.message });
        console.error(`  ❌ ${name} — ${e.message}`);
        if (output) output.innerHTML += `<div class="test-fail">❌ ${name} — <code>${e.message}</code></div>`;
    }
}

function assertEqual(actual, expected, msg) {
    if (actual !== expected) {
        throw new Error(msg || `Esperado ${JSON.stringify(expected)}, recebeu ${JSON.stringify(actual)}`);
    }
}

function assertTrue(value, msg) {
    if (!value) throw new Error(msg || `Esperado valor verdadeiro, recebeu ${JSON.stringify(value)}`);
}

function assertFalse(value, msg) {
    if (value) throw new Error(msg || `Esperado valor falso, recebeu ${JSON.stringify(value)}`);
}

function assertArrayEqual(actual, expected, msg) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(msg || `Arrays diferentes:\n  Obtido: ${JSON.stringify(actual)}\n  Esperado: ${JSON.stringify(expected)}`);
    }
}

function showTestSummary() {
    const total = testResults.passed + testResults.failed;
    console.log(`\n📊 Resultado: ${testResults.passed}/${total} testes passaram`);

    if (testResults.failed > 0) {
        console.log(`\n❌ ${testResults.failed} teste(s) falharam:`);
        for (const err of testResults.errors) {
            console.log(`  [${err.group}] ${err.test}: ${err.error}`);
        }
    }

    const summaryDiv = document.getElementById('test-summary');
    if (summaryDiv) {
        summaryDiv.className = testResults.failed === 0 ? 'summary-pass' : 'summary-fail';
        summaryDiv.textContent = `${testResults.passed}/${total} testes passaram` +
            (testResults.failed > 0 ? ` (${testResults.failed} falhas)` : ' ✅');
    }
}
