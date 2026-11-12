/** Views consumindo controllers JSON via fetch (cliente-api.js). Nenhuma regra de autorização está somente no front-end. */
(() => {
  'use strict';
  const page = document.body.dataset.page;
  let state = { autenticado: false, csrf_token: '' };
  const $ = (sel, root = document) => root.querySelector(sel);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const toast = (message, variant = 'success') => {
    const el = $('#toast');
    el.textContent = message;
    el.className = `toast ${variant}`;
    el.hidden = false;
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => el.hidden = true, 6000);
  };
  const messageFrom = (detail) => {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map(d => `${d.loc?.at(-1) || 'Campo'}: ${d.msg || 'Valor inválido'}`).join(' · ');
    return 'Não foi possível concluir a solicitação.';
  };
  // Cliente HTTP compartilhado (cliente-api.js): mesma origem, CSRF e tolerância ao "despertar" da API na nuvem.
  const api = async (url, options = {}) => {
    const { ok, dados } = await window.MeritoApi.requisitar(url, { ...options, csrf: state.csrf_token });
    if (!ok) throw new Error(messageFrom(dados.detail));
    return dados;
  };
  const toObject = (form) => Object.fromEntries(new FormData(form).entries());
  const valid = (form) => { if (form.reportValidity()) return true; toast('Confira os campos obrigatórios do formulário.', 'error'); return false; };
  const submitting = async (form, action) => {
    if (!valid(form)) return;
    const btn = $('button[type="submit"]', form);
    btn.disabled = true;
    const old = btn.innerHTML;
    btn.textContent = 'Salvando...';
    try { await action(); } catch (err) { toast(err.message, 'error'); }
    finally { btn.disabled = false; btn.innerHTML = old; }
  };
  const instituicoes = async (select, selected = null) => {
    const items = await api('/api/instituicoes');
    select.innerHTML = '<option value="">Selecione sua instituição</option>' + items.map(i => `<option value="${esc(i.id)}" ${selected === i.id ? 'selected' : ''}>${esc(i.nome)}</option>`).join('');
  };
  const updateNav = () => {
    $('.nav-panel').hidden = !state.autenticado;
    $('.nav-logout').hidden = !state.autenticado;
    $('.nav-login').hidden = !!state.autenticado;
  };
  const formRegister = (tipo) => {
    const form = tipo === 'aluno' ? $('#form-aluno') : $('#form-empresa');
    if (tipo === 'aluno') instituicoes($('[name="instituicao_id"]', form)).catch(e => toast(e.message, 'error'));
    form.addEventListener('submit', e => {
      e.preventDefault();
      submitting(form, async () => {
        const values = toObject(form);
        if (tipo === 'empresa' && !values.cnpj) values.cnpj = null;
        const endpoint = tipo === 'aluno' ? 'alunos' : 'empresas';
        await api('/api/' + endpoint, { method: 'POST', body: JSON.stringify(values) });
        window.location.assign('/login?cadastrado=1');
      });
    });
  };
  const formLogin = () => {
    if (new URLSearchParams(location.search).get('cadastrado') === '1') toast('Cadastro realizado! Entre com seu login e senha.');
    const form = $('#form-login');
    form.addEventListener('submit', e => {
      e.preventDefault();
      submitting(form, async () => {
        const result = await api('/api/auth/login', { method: 'POST', body: JSON.stringify(toObject(form)) });
        state.csrf_token = result.csrf_token;
        window.location.assign('/painel');
      });
    });
  };
  const campo = (nome, titulo, valor, extras = '') => `<label class="field">${esc(titulo)}<input name="${nome}" value="${esc(valor)}" ${extras}></label>`;
  const empresasPublicas = async () => {
    const lista = $('#lista-empresas');
    const empresas = await api('/api/empresas');
    lista.innerHTML = empresas.length ? empresas.map(e => `<article class="feature"><span class="partner-icon" aria-hidden="true">⌂</span><h3>${esc(e.nome)}</h3><p>${esc(e.descricao || 'Empresa parceira do programa de reconhecimento estudantil.')}</p><div class="partner-note">PARCEIRA CADASTRADA ✓</div></article>`).join('') : '<div class="empty">Ainda não há empresas cadastradas. Seja a primeira parceira!</div>';
  };
  const initPainel = async () => {
    if (!state.autenticado) { window.location.replace('/login'); return; }
    $('#dash-title').textContent = `Olá, ${state.nome.split(' ')[0]}!`;
    $('#dash-subtitle').textContent = 'Aqui você gerencia seus dados de cadastro.';
    $('#dash-role').textContent = { aluno: 'Estudante', empresa: 'Empresa parceira', professor: 'Professor' }[state.perfil] || state.perfil;
    $('#access-login').textContent = state.login;
    $('#access-type').textContent = `Perfil: ${state.perfil}`;
    const saldo = await api('/api/carteira');
    $('#wallet-balance').textContent = saldo.saldo === null ? '—' : Intl.NumberFormat('pt-BR').format(saldo.saldo);
    const form = $('#form-perfil');
    const deleteBtn = $('#delete-account');
    if (state.perfil === 'professor') {
      deleteBtn.closest('.danger-panel').hidden = true;
      const lista = $('#professor-list'); lista.hidden = false;
      form.innerHTML = '<p class="disabled-notice full">O professor é pré-cadastrado pela instituição. Utilize a seção Reconhecer mérito abaixo para distribuir moedas.</p>';
      const alunos = await api('/api/alunos');
      $('#lista-alunos').innerHTML = alunos.length ? alunos.map(a => `<div class="list-item"><strong>${esc(a.nome)}</strong><small>${esc(a.curso)}</small></div>`).join('') : '<p class="empty">Nenhum estudante da sua instituição se cadastrou ainda.</p>';
      return;
    }
    const tipo = state.perfil;
    const url = tipo === 'aluno' ? `/api/alunos/${encodeURIComponent(state.id)}` : `/api/empresas/${encodeURIComponent(state.id)}`;
    const info = await api(url);
    if (tipo === 'aluno') {
      form.innerHTML = campo('nome','Nome completo',info.nome,'required minlength="3" maxlength="150"')
        + campo('email','E-mail',info.email,'required type="email"')
        + campo('cpf','CPF (não editável)',info.cpf,'disabled')
        + campo('rg','RG',info.rg,'required')
        + campo('curso','Curso',info.curso,'required')
        + campo('login','Login (não editável)',info.login,'disabled')
        + `<label class="field full">Endereço<input name="endereco" required maxlength="240" value="${esc(info.endereco)}"></label>`
        + `<label class="field full">Instituição de ensino<select name="instituicao_id" required></select></label>`
        + campo('senha_nova','Nova senha (opcional)','', 'type="password" minlength="8" placeholder="Deixe vazio para manter a atual"')
        + '<div class="full"><button type="submit" class="btn btn-primary btn-block">Salvar alterações <span>→</span></button></div>';
      await instituicoes($('[name="instituicao_id"]', form), info.instituicao_id);
    } else {
      form.innerHTML = `<label class="field full">Nome da empresa<input name="nome" required minlength="2" maxlength="160" value="${esc(info.nome)}"></label>`
        + campo('email_contato','E-mail de contato',info.email_contato,'type="email" required')
        + campo('cnpj','CNPJ (opcional)',info.cnpj || '','maxlength="18"')
        + `<label class="field full">Descrição (opcional)<textarea name="descricao" maxlength="1000" rows="4">${esc(info.descricao || '')}</textarea></label>`
        + campo('login','Login (não editável)',info.login,'disabled')
        + campo('senha_nova','Nova senha (opcional)','','type="password" minlength="8" placeholder="Deixe vazio para manter a atual"')
        + '<div class="full"><button type="submit" class="btn btn-primary btn-block">Salvar alterações <span>→</span></button></div>';
    }
    form.addEventListener('submit', e => {
      e.preventDefault();
      submitting(form, async () => {
        const values = toObject(form);
        if (!values.senha_nova) values.senha_nova = null;
        if (tipo === 'empresa' && !values.cnpj) values.cnpj = null;
        await api(url, { method: 'PUT', body: JSON.stringify(values) });
        toast('Cadastro atualizado com sucesso.');
      });
    });
    deleteBtn.addEventListener('click', async () => {
      if (!confirm('Deseja realmente excluir sua conta? Esta ação não poderá ser desfeita.')) return;
      try { await api(url, { method: 'DELETE' }); window.location.assign('/?excluido=1'); }
      catch (err) {
        if (err.message.includes('não pode ser excluíd') && confirm('Existem registros vinculados à conta. Deseja desativá-la, preservando o histórico?')) {
          try { await api(url + '/desativar', {method: 'PATCH'}); window.location.assign('/?desativado=1'); }
          catch (exc) { toast(exc.message, 'error'); }
        } else toast(err.message, 'error');
      }
    });
  };
  const main = async () => {
    try { state = await api('/api/sessao'); }
    catch (err) { toast('Não foi possível iniciar a sessão: ' + err.message, 'error'); return; }
    updateNav();
    window.dispatchEvent(new CustomEvent('moeda:ready', { detail: state }));
    $('.nav-logout').addEventListener('click', async () => {
      try { await api('/api/auth/logout', { method: 'POST' }); window.location.assign('/'); }
      catch (e) { toast(e.message, 'error'); }
    });
    if (page === 'cadastro-aluno') formRegister('aluno');
    if (page === 'cadastro-empresa') formRegister('empresa');
    if (page === 'login') formLogin();
    if (page === 'painel') initPainel().catch(e => toast(e.message, 'error'));
    if (page === 'parceiros') empresasPublicas().catch(e => toast(e.message, 'error'));
  };
  main();
})();
