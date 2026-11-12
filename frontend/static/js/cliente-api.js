/**
 * Cliente HTTP compartilhado pelas telas (app.js e sprint03.js).
 *
 * As chamadas usam caminhos relativos (/api/...). Na nuvem, a Vercel repassa esses caminhos
 * para a API no Render (frontend/vercel.json), então o navegador enxerga uma única origem e o
 * cookie de sessão e o token CSRF funcionam como no ambiente local.
 *
 * No plano gratuito do Render, a API "dorme" após um período sem acessos e leva cerca de um
 * minuto para voltar. Consultas (GET) que falham nesse intervalo são repetidas automaticamente,
 * com um aviso na tela. Operações que alteram dados (POST, PUT...) nunca são repetidas.
 */
(() => {
  'use strict';
  const ESPERAS_MS = [2000, 3000, 5000, 8000, 10000, 10000, 10000, 15000, 15000];
  const STATUS_TEMPORARIOS = new Set([502, 503, 504]);
  const dormir = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  let avisoAberto = false;

  const avisarInicio = () => {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = 'Conectando ao servidor. No primeiro acesso, isso pode levar até um minuto…';
    el.className = 'toast';
    el.hidden = false;
    avisoAberto = true;
  };
  const encerrarAviso = () => {
    if (!avisoAberto) return;
    const el = document.getElementById('toast');
    if (el) el.hidden = true;
    avisoAberto = false;
  };

  /**
   * @param {string} url caminho da API, ex.: '/api/sessao'
   * @param {RequestInit & {csrf?: string}} opcoes
   * @returns {Promise<{ok: boolean, status: number, dados: any}>}
   */
  async function requisitar(url, { csrf = '', ...opcoes } = {}) {
    const metodo = (opcoes.method || 'GET').toUpperCase();
    const headers = { ...(opcoes.headers || {}) };
    if (opcoes.body) headers['Content-Type'] = 'application/json';
    if (metodo !== 'GET') headers['X-CSRF-Token'] = csrf;

    for (let tentativa = 0; ; tentativa += 1) {
      let resposta = null;
      try {
        resposta = await fetch(url, { ...opcoes, headers, credentials: 'same-origin' });
      } catch {
        resposta = null; // falha de rede
      }
      const temporaria = resposta === null || STATUS_TEMPORARIOS.has(resposta.status);
      if (temporaria && metodo === 'GET' && tentativa < ESPERAS_MS.length) {
        avisarInicio();
        await dormir(ESPERAS_MS[tentativa]);
        continue;
      }
      encerrarAviso();
      if (resposta === null) {
        throw new Error('Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.');
      }
      let dados;
      try { dados = await resposta.json(); } catch { dados = {}; }
      if (!resposta.ok && resposta.status >= 500 && !dados.detail) {
        dados = { detail: 'O servidor está indisponível no momento. Tente novamente em instantes.' };
      }
      return { ok: resposta.ok, status: resposta.status, dados };
    }
  }

  window.MeritoApi = Object.freeze({ requisitar });
})();
