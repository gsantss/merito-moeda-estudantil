/** Sprint 03: funções finais de domínio na UI. Reusa o cliente API e a sessão do app.js. */
(() => {
  'use strict';
  const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const $ = q => document.querySelector(q);
  const fmt = v => Number(v).toLocaleString('pt-BR');
  let state = {};
  const msg = (s, error=false) => {const t=$('#toast');t.textContent=s;t.className='toast '+(error?'error':'success');t.hidden=false;setTimeout(()=>t.hidden=true,6000);};
  async function api(url, opt={}) {
    const headers={...(opt.headers||{})};
    if(opt.body) headers['Content-Type']='application/json';
    if((opt.method||'GET').toUpperCase()!=='GET')headers['X-CSRF-Token']=state.csrf_token;
    const r=await fetch(url,{...opt,headers,credentials:'same-origin'});
    const d=await r.json();
    if(!r.ok)throw new Error(typeof d.detail==='string'?d.detail:'Dados inválidos. Verifique os campos.');
    return d;
  }
  const post=(url,data,method='POST')=>api(url,{method,body:JSON.stringify(data)});
  const formData=f=>Object.fromEntries(new FormData(f).entries());
  const card=v=>`<article class="feature perk"><img class="perk-image" src="${esc(v.foto_url)}" alt="Foto: ${esc(v.titulo)}" loading="lazy" onerror="this.style.display='none'"/><div class="perk-body"><small>${esc(v.empresa||'Empresa parceira')}</small><h3>${esc(v.titulo)}</h3><p>${esc(v.descricao)}</p><strong class="coins">✦ ${fmt(v.custo)} moedas</strong> ${state.perfil==='aluno' ? `<button type="button" class="btn btn-primary redeem-btn" data-id="${esc(v.id)}">Resgatar →</button>` : '<a href="/login" class="link-arrow">Entre para resgatar →</a>'}</div></article>`;
  async function catalog() {
    const list=await api('/api/vantagens');
    $('#catalog-list').innerHTML=list.length?list.map(card).join(''):'<p class="empty">Ainda não existem vantagens ativas.</p>';
    document.querySelectorAll('.redeem-btn').forEach(b=>b.addEventListener('click',()=>redeem(b.dataset.id)));
  }
  async function redeem(id) {
    if(!confirm('Confirmar o resgate? As moedas serão descontadas de sua carteira.'))return;
    try {const r=await post('/api/resgates',{vantagem_id:id});msg(`Resgate realizado! Seu cupom é ${r.cupom}`);if($('#wallet-balance')) await refreshFinance();}
    catch(e){msg(e.message,true);}
  }
  async function refreshFinance() {
    if(!['aluno','professor'].includes(state.perfil))return;
    const res=await api('/api/extrato');
    $('#wallet-balance').textContent=fmt(res.saldo);
    $('#extrato-panel').hidden=false;
    $('#extrato-list').innerHTML=res.movimentacoes.length?res.movimentacoes.map(t=>`<div class="list-item"><strong>${t.direcao==='entrada'?'+':'−'} ${fmt(t.quantidade)} moedas · ${esc(t.tipo.replace('_',' '))}</strong><small>${esc(t.motivo||'—')} · ${new Date(t.data_hora).toLocaleString('pt-BR')}</small></div>`).join(''):'<div class="empty">Nenhuma movimentação registrada.</div>';
    if(state.perfil==='aluno'){
      $('#cupons-panel').hidden=false;
      const coupons=await api('/api/cupons');
      $('#cupons-list').innerHTML=coupons.length?coupons.map(c=>`<div class="list-item"><strong>${esc(c.codigo)} · ${esc(c.vantagem)}</strong><small>${c.utilizado_em?'Utilizado':'Disponível para troca'} · ${new Date(c.emitido_em).toLocaleDateString('pt-BR')}</small></div>`).join(''):'<div class="empty">Você ainda não resgatou nenhuma vantagem.</div>';
    }
  }
  async function professor() {
    const p=$('#operations-panel');p.hidden=false;
    $('#operations-title').textContent='Reconhecer mérito';
    $('#operations-subtitle').textContent='Distribua moedas aos estudantes da sua instituição.';
    const alunos=await api('/api/alunos');
    $('#operations-content').innerHTML=`<form id="award-form" class="form-grid"><label class="field full">Aluno da instituição<select name="aluno_id" required><option value="">Selecione um estudante</option>${alunos.map(a=>`<option value="${esc(a.id)}">${esc(a.nome)} · ${esc(a.curso)}</option>`).join('')}</select></label><label class="field">Quantidade<input type="number" name="quantidade" min="1" step="1" required></label><label class="field full">Motivo da recompensa<textarea name="motivo" minlength="3" maxlength="1000" required placeholder="Ex.: Participação exemplar na aula"></textarea></label><button class="btn btn-primary" type="submit">Enviar moedas →</button></form><p class="small-note">O crédito semestral de 1.000 moedas é feito automaticamente pelo sistema no início de cada semestre; o professor não pode acioná-lo.</p>`;
    $('#award-form').addEventListener('submit',async e=>{e.preventDefault();const f=e.currentTarget;if(!f.reportValidity())return;const p=formData(f);p.quantidade=Number(p.quantidade);try{await post('/api/distribuicoes',p);msg('Moedas distribuídas com sucesso. E-mail colocado na fila.');f.reset();await refreshFinance();}catch(ex){msg(ex.message,true);}});
  }
  async function company() {
    $('#operations-panel').hidden=false;
    $('#operations-title').textContent='Gerenciar minhas vantagens';
    $('#operations-subtitle').textContent='Cadastre e edite benefícios, e confira cupons apresentados no balcão.';
    $('#operations-content').innerHTML=`<form id="perk-form" class="form-grid"><input type="hidden" name="id"><label class="field full">Título da vantagem<input name="titulo" minlength="3" maxlength="150" required></label><label class="field full">Descrição<textarea name="descricao" minlength="8" maxlength="1500" required></textarea></label><label class="field full">URL da foto (http/https)<input name="foto_url" type="url" required></label><label class="field">Custo em moedas<input name="custo" type="number" min="1" step="1" required></label><label class="field">Status<select name="ativa"><option value="true">Ativa</option><option value="false">Inativa</option></select></label><div class="full buttons-row"><button class="btn btn-primary" type="submit">Salvar vantagem →</button><button type="button" class="btn btn-outline" id="clear-perk">Novo cadastro</button></div></form><div id="my-perks" class="compact-list"></div><hr class="light-line"><h3>Conferência presencial de cupom</h3><form id="coupon-form" class="form-grid"><label class="field full">Código apresentado pelo aluno<input name="codigo" required placeholder="MER-XXXXXXXX"></label><button class="btn btn-primary" type="submit">Confirmar utilização →</button></form>`;
    $('#perk-form').addEventListener('submit',async e=>{e.preventDefault();const f=e.currentTarget;if(!f.reportValidity())return;const data=formData(f),id=data.id;delete data.id;data.custo=Number(data.custo);data.ativa=data.ativa==='true';try{await post(id?`/api/vantagens/${encodeURIComponent(id)}`:'/api/vantagens',data,id?'PUT':'POST');msg('Vantagem salva.');f.reset();await loadPerks();}catch(ex){msg(ex.message,true);}});
    $('#clear-perk').onclick=()=>$('#perk-form').reset();
    $('#coupon-form').addEventListener('submit',async e=>{e.preventDefault();const f=e.currentTarget;try{const r=await post('/api/cupons/utilizar',formData(f));msg(`Cupom ${r.codigo} validado e utilizado.`);f.reset();}catch(ex){msg(ex.message,true);}});
    await loadPerks();
  }
  async function loadPerks(){
    const list=await api('/api/vantagens/minhas');
    $('#my-perks').innerHTML=list.length?list.map(v=>`<div class="list-item perk-line"><div><strong>${esc(v.titulo)} · ${fmt(v.custo)} moedas</strong><small>${v.ativa?'Ativa':'Inativa'}</small></div><div><button class="btn btn-outline btn-sm edit-perk" data-id="${esc(v.id)}">Editar</button> <button class="btn btn-danger btn-sm remove-perk" data-id="${esc(v.id)}">Desativar</button></div></div>`).join(''):'<p class="empty">Nenhuma vantagem cadastrada.</p>';
    $('.perk-line')?.scrollIntoView({block:'nearest'});
    document.querySelectorAll('.edit-perk').forEach(b=>b.onclick=()=>{const v=list.find(x=>x.id===b.dataset.id),f=$('#perk-form');for(const k of ['id','titulo','descricao','foto_url','custo'])f.elements[k].value=v[k];f.elements['ativa'].value=String(v.ativa);f.scrollIntoView({behavior:'smooth'});});
    document.querySelectorAll('.remove-perk').forEach(b=>b.onclick=async()=>{if(!confirm('Desativar esta vantagem?'))return;try{await api('/api/vantagens/'+b.dataset.id,{method:'DELETE'});msg('Vantagem desativada.');await loadPerks();}catch(e){msg(e.message,true);}});
  }
  async function init(){
    if(!['painel','vantagens'].includes(document.body.dataset.page))return;
    try{if(document.body.dataset.page==='vantagens')await catalog();if(document.body.dataset.page==='painel'&&state.autenticado){
      // app.js também inicializa o painel; extra commands are deliberately independent.
      if(state.perfil==='professor')await professor();
      if(state.perfil==='empresa')await company();
      if(['professor','aluno'].includes(state.perfil))await refreshFinance();
    }}catch(e){msg(e.message,true);}
  }
  window.addEventListener('moeda:ready', async event => {state=event.detail;await init();});
})();
