// ============================================================
// VISITHOSP - TELAS "SERVIÇOS DO VISITANTE" E "PAINEL DE GESTÃO"
// ============================================================
//
// servicos.html (lado do visitante, usa o token validado no login):
//   1. Regulamento e horários oficiais      GET  /regulamento
//   2. Status do paciente                   GET  /pacientes/<id>/status
//   3. Localização do leito                 GET  /leitos/<id>/localizacao
//   5. Alterar ou cancelar agendamento      GET  /internacoes/<id>/visitas
//                                           POST /visitas/<id>/reagendar
//                                           POST /visitas/<id>/cancelar
//   6. Horários ocupados do mesmo leito     GET  /leitos/<id>/horarios-ocupados
//   7. Cadastro de visitante com vínculo    POST /visitantes/cadastro-vinculado
//
// painel.html (lado da gestão/enfermagem):
//   4. Revogar acesso do visitante          GET  /pacientes/<id>/visitantes
//                                           POST /visitantes/<id>/revogar-acesso
//   8. Relatório de histórico de visitas    GET  /relatorios/historico-visitas
//   9. Auditoria de check-in e check-out    GET  /relatorios/auditoria-acessos
//                                           POST /visitas/<id>/checkin | /checkout
//  10. Visitantes por turno                 GET  /relatorios/visitantes-por-turno
//
// API_URL vem do config.js.


// ============================================================
// UTILITÁRIOS
// ============================================================

function esc(valor) {
    return String(valor === null || valor === undefined ? "" : valor)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

async function api(caminho, opcoes) {
    const config = Object.assign({ headers: { "Content-Type": "application/json" } }, opcoes || {});
    if (config.body && typeof config.body !== "string") {
        config.body = JSON.stringify(config.body);
    }

    let resposta;
    try {
        resposta = await fetch(`${API_URL}${caminho}`, config);
    } catch (erro) {
        throw new Error("Não foi possível conectar ao servidor. Verifique se o Flask está rodando.");
    }

    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
        throw new Error(dados.erro || `Erro ${resposta.status} ao consultar o servidor.`);
    }
    return dados;
}

function dataHora(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleDateString("pt-BR") + " " + d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function soData(iso) {
    return iso ? new Date(iso).toLocaleDateString("pt-BR") : "—";
}

function soHora(iso) {
    return iso ? new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : "—";
}

function hojeISO(deslocamentoDias) {
    const d = new Date();
    d.setDate(d.getDate() + (deslocamentoDias || 0));
    const mes = String(d.getMonth() + 1).padStart(2, "0");
    const dia = String(d.getDate()).padStart(2, "0");
    return `${d.getFullYear()}-${mes}-${dia}`;
}

function mensagem(idContainer, tipo, texto) {
    const el = document.getElementById(idContainer);
    if (!el) return;
    el.innerHTML = texto ? `<div class="sv-msg ${tipo}">${esc(texto)}</div>` : "";
}

function carregando(el) {
    if (el) el.innerHTML = '<p class="sv-vazio">Carregando...</p>';
}

function erroEm(el, erro) {
    if (el) el.innerHTML = `<div class="sv-msg erro">${esc(erro.message || erro)}</div>`;
}

const BADGE_SITUACAO = {
    agendada: "info",
    em_andamento: "warn",
    concluida: "ok",
    cancelada: "neutro",
    nao_compareceu: "danger",
};

function badgeSituacao(item) {
    return `<span class="sv-badge ${BADGE_SITUACAO[item.situacao] || "neutro"}">${esc(item.situacao_texto)}</span>`;
}

function configurarAbas(aoAbrir) {
    const abas = document.querySelectorAll(".sv-tab");
    abas.forEach(function (aba) {
        aba.addEventListener("click", function () {
            abas.forEach(a => a.classList.remove("ativa"));
            document.querySelectorAll(".sv-panel").forEach(p => p.classList.remove("ativa"));
            aba.classList.add("ativa");
            const painel = document.getElementById(`aba-${aba.dataset.aba}`);
            if (painel) painel.classList.add("ativa");
            if (aoAbrir) aoAbrir(aba.dataset.aba);
        });
    });
}


// ============================================================
// INICIALIZAÇÃO
// ============================================================

document.addEventListener("DOMContentLoaded", function () {
    const tela = document.body.dataset.tela;
    if (tela === "servicos") iniciarServicos();
    if (tela === "painel") iniciarPainel();
});


// ############################################################
// TELA: SERVIÇOS DO VISITANTE (servicos.html)
// ############################################################

let sessao = null;          // { internacao, leito, paciente } salvo pelo login
const abasCarregadas = {};

function iniciarServicos() {
    try {
        sessao = JSON.parse(localStorage.getItem("visitHospInternacao") || "null");
    } catch (e) {
        sessao = null;
    }

    preencherCabecalhoPaciente();

    configurarAbas(function (aba) {
        if (!abasCarregadas[aba]) {
            abasCarregadas[aba] = true;
            carregarAba(aba);
        }
    });

    abasCarregadas.regulamento = true;
    carregarRegulamento();

    const btnStatus = document.getElementById("btn-atualizar-status");
    if (btnStatus) btnStatus.addEventListener("click", carregarStatus);

    const campoData = document.getElementById("ocupados-data");
    if (campoData) {
        campoData.value = hojeISO(0);
        campoData.addEventListener("change", carregarOcupados);
    }

    const cpf = document.getElementById("cad-cpf");
    if (cpf) cpf.addEventListener("input", mascaraCpf);

    const form = document.getElementById("form-cadastro");
    if (form) form.addEventListener("submit", enviarCadastro);

    if (sessao && sessao.paciente && sessao.leito) {
        document.getElementById("cad-paciente").value = sessao.paciente.nome;
        document.getElementById("cad-leito").value =
            `Leito ${sessao.leito.numero} • Ala ${sessao.leito.ala} • Bloco ${sessao.leito.bloco}`;
    }
}

function temSessao() {
    return sessao && sessao.internacao && sessao.paciente && sessao.leito;
}

function avisoSemToken(el) {
    if (!el) return;
    el.innerHTML = `
        <div class="sv-aviso">
            <span>Esta funcionalidade precisa dos dados da internação.</span>
            <a class="sv-btn" href="index.html">Inserir token de acesso</a>
        </div>`;
}

function carregarAba(aba) {
    if (aba === "status") carregarStatus();
    if (aba === "localizacao") carregarLocalizacao();
    if (aba === "agendamentos") carregarAgendamentos();
    if (aba === "ocupados") carregarOcupados();
    if (aba === "cadastro" && !temSessao()) {
        mensagem("cadastro-msg", "info", "Valide o token de acesso na tela inicial para vincular o visitante ao paciente.");
        document.getElementById("btn-cadastrar").disabled = true;
    }
}

function preencherCabecalhoPaciente() {
    const nome = document.getElementById("patient-name");
    const local = document.getElementById("patient-location");
    const avatar = document.getElementById("patient-avatar");
    const status = document.getElementById("patient-status");

    if (!temSessao()) {
        nome.textContent = "Nenhuma internação encontrada";
        local.textContent = "Insira um token de acesso válido para continuar.";
        return;
    }

    const paciente = sessao.paciente;
    const leito = sessao.leito;
    nome.textContent = paciente.nome;
    local.textContent = `Quarto ${leito.numero} • Leito ${leito.id} • Ala ${leito.ala}`;

    const partes = paciente.nome.trim().split(" ");
    avatar.textContent = ((partes[0] || "").charAt(0) + (partes.length > 1 ? partes[partes.length - 1].charAt(0) : "")).toUpperCase();

    // Status real do paciente (requisito 2) também aparece no cabeçalho
    api(`/pacientes/${paciente.id}/status`).then(function (dados) {
        status.classList.toggle("restrito", !dados.liberado_para_visitas);
        status.innerHTML = `<span class="circle"></span><span>${dados.liberado_para_visitas ? "Disponível" : "Indisponível"}</span>`;
    }).catch(function () { /* mantém "--" */ });
}


// ------------------------------------------------------------
// 1. REGULAMENTO E HORÁRIOS OFICIAIS
// ------------------------------------------------------------

async function carregarRegulamento() {
    const el = document.getElementById("regulamento-conteudo");
    carregando(el);
    try {
        const d = await api("/regulamento");

        const janelas = d.horarios_oficiais.map(j => `
            <div class="sv-card">
                <div class="sv-card-titulo">${esc(j.periodo)}</div>
                <div class="sv-card-valor">${esc(j.inicio)} às ${esc(j.fim)}</div>
                <div class="sv-card-texto">${j.quantidade_horarios} horários de ${d.duracao_slot_minutos} minutos</div>
            </div>`).join("");

        const hospital = d.hospital ? `
            <div class="sv-card">
                <div class="sv-card-titulo">Hospital</div>
                <div class="sv-card-valor">${esc(d.hospital.nome)}</div>
                <div class="sv-card-texto">${esc(d.hospital.endereco)}</div>
            </div>` : "";

        const capacidade = `
            <div class="sv-card">
                <div class="sv-card-titulo">Limites por visita</div>
                <div class="sv-card-valor">${d.capacidade_por_horario} visitantes por horário</div>
                <div class="sv-card-texto">Permanência máxima de ${d.permanencia_maxima_minutos} minutos</div>
            </div>`;

        const horarios = d.horarios.map(h => `<span class="sv-chip">${esc(h.inicio)} - ${esc(h.fim)}</span>`).join("");

        const regras = d.regras.map(r => `
            <div class="sv-regra"><strong>${esc(r.titulo)}</strong><span>${esc(r.descricao)}</span></div>`).join("");

        const nomesPapel = { visitante: "Visitante", acompanhante: "Acompanhante" };
        const papeis = Object.keys(d.regras_por_papel).map(function (papel) {
            const r = d.regras_por_papel[papel];
            const horas = r.duracao_maxima_minutos >= 60 ? `${r.duracao_maxima_minutos / 60}h` : `${r.duracao_maxima_minutos} min`;
            return `
                <div class="sv-card">
                    <div class="sv-card-titulo">${esc(nomesPapel[papel] || papel)}</div>
                    <div class="sv-card-valor">Até ${esc(horas)} por acesso</div>
                    <div class="sv-card-texto">Áreas: ${esc(r.areas_permitidas.join(", ").replace(/_/g, " "))} • Acesso ${esc(r.tipo_acesso)}</div>
                </div>`;
        }).join("");

        el.innerHTML = `
            <div class="sv-grid">${hospital}${janelas}${capacidade}</div>
            <h3>Horários oficiais</h3>
            <div class="sv-chips">${horarios}</div>
            <h3>Regras de visitação</h3>
            <div class="sv-lista">${regras}</div>
            <h3>Regras por tipo de acesso</h3>
            <div class="sv-grid">${papeis}</div>`;
    } catch (erro) {
        erroEm(el, erro);
    }
}


// ------------------------------------------------------------
// 2. STATUS DO PACIENTE
// ------------------------------------------------------------

async function carregarStatus() {
    const el = document.getElementById("status-conteudo");
    if (!temSessao()) return avisoSemToken(el);
    carregando(el);
    try {
        const d = await api(`/pacientes/${sessao.paciente.id}/status`);
        const badge = d.situacao === "liberado" ? "ok" : (d.situacao === "restrito" ? "danger" : "neutro");
        const texto = { liberado: "Liberado para visitas", restrito: "Visitas suspensas", sem_internacao: "Sem internação ativa" }[d.situacao];

        el.innerHTML = `
            <div class="sv-card" style="margin-bottom:14px">
                <span class="sv-badge ${badge}">${esc(texto)}</span>
                <div class="sv-card-valor" style="margin-top:10px">${esc(d.nome)}</div>
                <div class="sv-card-texto">${esc(d.mensagem)}</div>
            </div>
            <div class="sv-grid">
                <div class="sv-card">
                    <div class="sv-card-titulo">Leito</div>
                    <div class="sv-card-valor">${d.leito ? `Leito ${esc(d.leito.numero)} • Ala ${esc(d.leito.ala)}` : "—"}</div>
                </div>
                <div class="sv-card">
                    <div class="sv-card-titulo">Internado desde</div>
                    <div class="sv-card-valor">${d.internacao ? soData(d.internacao.data_entrada) : "—"}</div>
                </div>
                <div class="sv-card">
                    <div class="sv-card-titulo">Alta prevista</div>
                    <div class="sv-card-valor">${d.internacao ? soData(d.internacao.data_saida_prevista) : "—"}</div>
                </div>
                <div class="sv-card">
                    <div class="sv-card-titulo">Visitas agendadas hoje</div>
                    <div class="sv-numero">${d.visitas_agendadas_hoje}</div>
                </div>
            </div>
            <p class="sv-sub" style="margin:12px 0 0 0">Consultado em ${dataHora(d.consultado_em)}</p>`;
    } catch (erro) {
        erroEm(el, erro);
    }
}


// ------------------------------------------------------------
// 3. LOCALIZAÇÃO DO LEITO
// ------------------------------------------------------------

async function carregarLocalizacao() {
    const el = document.getElementById("localizacao-conteudo");
    if (!temSessao()) return avisoSemToken(el);
    carregando(el);
    try {
        const d = await api(`/leitos/${sessao.leito.id}/localizacao`);
        const passos = d.orientacoes.map(p => `<li>${esc(p)}</li>`).join("");
        const mapa = d.mapa_url
            ? `<a class="sv-btn secundario" href="${esc(d.mapa_url)}" target="_blank" rel="noopener">📍 Abrir no mapa</a>`
            : "";

        el.innerHTML = `
            <div class="sv-grid">
                <div class="sv-card"><div class="sv-card-titulo">Bloco</div><div class="sv-card-valor">${esc(d.leito.bloco)}</div></div>
                <div class="sv-card"><div class="sv-card-titulo">Andar</div><div class="sv-card-valor">${d.leito.andar === 0 ? "Térreo" : esc(d.leito.andar) + "º andar"}</div></div>
                <div class="sv-card"><div class="sv-card-titulo">Ala</div><div class="sv-card-valor">${esc(d.leito.ala)}</div></div>
                <div class="sv-card"><div class="sv-card-titulo">Leito / Quarto</div><div class="sv-card-valor">${esc(d.leito.numero)}</div></div>
            </div>
            <h3>Passo a passo</h3>
            <ol class="sv-passos">${passos}</ol>
            <div style="margin-top:20px">${mapa}</div>`;
    } catch (erro) {
        erroEm(el, erro);
    }
}


// ------------------------------------------------------------
// 5. ALTERAR OU CANCELAR AGENDAMENTO
// ------------------------------------------------------------

let horariosOficiais = null;

async function carregarAgendamentos() {
    const el = document.getElementById("agendamentos-conteudo");
    document.getElementById("agendamentos-editor").innerHTML = "";
    if (!temSessao()) return avisoSemToken(el);
    carregando(el);
    try {
        const lista = await api(`/internacoes/${sessao.internacao.id}/visitas`);
        if (lista.length === 0) {
            el.innerHTML = '<p class="sv-vazio">Nenhum agendamento encontrado para esta internação.</p>';
            return;
        }

        const linhas = lista.map(v => `
            <tr>
                <td>${soData(v.data_hora)}<small>${soHora(v.data_hora)}</small></td>
                <td>${esc(v.visitante ? v.visitante.nome : "—")}</td>
                <td>${badgeSituacao(v)}</td>
                <td>
                    ${v.pode_alterar ? `
                    <div class="sv-acoes">
                        <button class="sv-btn secundario pequeno" data-alterar="${v.id}" data-atual="${esc(v.data_hora)}">Alterar</button>
                        <button class="sv-btn perigo pequeno" data-cancelar="${v.id}">Cancelar</button>
                    </div>` : '<small>—</small>'}
                </td>
            </tr>`).join("");

        el.innerHTML = `
            <div class="sv-tabela-wrap">
                <table class="sv-tabela">
                    <thead><tr><th>Data / hora</th><th>Visitante</th><th>Situação</th><th>Ações</th></tr></thead>
                    <tbody>${linhas}</tbody>
                </table>
            </div>`;

        el.querySelectorAll("[data-cancelar]").forEach(b => b.addEventListener("click", () => cancelarAgendamento(b.dataset.cancelar)));
        el.querySelectorAll("[data-alterar]").forEach(b => b.addEventListener("click", () => abrirEditor(b.dataset.alterar, b.dataset.atual)));
    } catch (erro) {
        erroEm(el, erro);
    }
}

async function cancelarAgendamento(id) {
    if (!confirm("Deseja realmente cancelar este agendamento?")) return;
    try {
        await api(`/visitas/${id}/cancelar`, { method: "POST" });
        mensagem("agendamentos-msg", "ok", "Agendamento cancelado com sucesso.");
        carregarAgendamentos();
    } catch (erro) {
        mensagem("agendamentos-msg", "erro", erro.message);
    }
}

async function abrirEditor(id, dataAtual) {
    const editor = document.getElementById("agendamentos-editor");
    if (!horariosOficiais) {
        try {
            horariosOficiais = (await api("/regulamento")).horarios;
        } catch (erro) {
            mensagem("agendamentos-msg", "erro", erro.message);
            return;
        }
    }

    editor.innerHTML = `
        <div class="sv-editor">
            <h3>Alterar agendamento de ${dataHora(dataAtual)}</h3>
            <div class="sv-filtros" style="margin-bottom:0">
                <div class="sv-campo">
                    <label for="edit-data">Nova data</label>
                    <input type="date" id="edit-data" min="${hojeISO(0)}" value="${hojeISO(1)}">
                </div>
                <div class="sv-campo">
                    <label for="edit-hora">Novo horário</label>
                    <select id="edit-hora"></select>
                </div>
                <button class="sv-btn" id="edit-salvar">Salvar alteração</button>
                <button class="sv-btn secundario" id="edit-fechar">Fechar</button>
            </div>
        </div>`;

    const campoData = document.getElementById("edit-data");
    const campoHora = document.getElementById("edit-hora");

    async function atualizarHorarios() {
        campoHora.innerHTML = "<option>Carregando...</option>";
        try {
            const d = await api(`/leitos/${sessao.leito.id}/horarios-ocupados?data=${campoData.value}`);
            campoHora.innerHTML = d.horarios.map(h => {
                const inicio = h.horario.split(" - ")[0];
                const lotado = h.situacao === "lotado";
                return `<option value="${inicio}" ${lotado ? "disabled" : ""}>${esc(h.horario)} — ${lotado ? "lotado" : h.vagas + " vaga(s)"}</option>`;
            }).join("");
        } catch (erro) {
            campoHora.innerHTML = horariosOficiais.map(h => `<option value="${h.inicio}">${h.inicio} - ${h.fim}</option>`).join("");
        }
    }

    campoData.addEventListener("change", atualizarHorarios);
    await atualizarHorarios();

    document.getElementById("edit-fechar").addEventListener("click", () => { editor.innerHTML = ""; });
    document.getElementById("edit-salvar").addEventListener("click", async function () {
        if (!campoData.value || !campoHora.value) return;
        try {
            await api(`/visitas/${id}/reagendar`, {
                method: "POST",
                body: { data_hora: `${campoData.value}T${campoHora.value}:00` },
            });
            mensagem("agendamentos-msg", "ok", "Agendamento alterado com sucesso.");
            carregarAgendamentos();
        } catch (erro) {
            mensagem("agendamentos-msg", "erro", erro.message);
        }
    });
}


// ------------------------------------------------------------
// 6. HORÁRIOS OCUPADOS DO MESMO LEITO
// ------------------------------------------------------------

async function carregarOcupados() {
    const el = document.getElementById("ocupados-conteudo");
    if (!temSessao()) return avisoSemToken(el);
    const data = document.getElementById("ocupados-data").value || hojeISO(0);
    carregando(el);
    try {
        const d = await api(`/leitos/${sessao.leito.id}/horarios-ocupados?data=${data}`);
        const textos = { livre: ["ok", "Livre"], parcial: ["warn", "Parcialmente ocupado"], lotado: ["danger", "Lotado"] };

        const linhas = d.horarios.map(h => {
            const pct = Math.round((h.ocupacao / h.capacidade) * 100);
            const [cls, texto] = textos[h.situacao];
            return `
                <div class="sv-slot">
                    <div class="sv-slot-hora">${esc(h.horario)}</div>
                    <div class="occupancy-bar"><div class="occupancy-fill ${h.situacao}" style="width:${pct}%"></div></div>
                    <div class="sv-slot-qtd">${h.ocupacao} de ${h.capacidade}</div>
                    <span class="sv-badge ${cls}">${texto}</span>
                </div>`;
        }).join("");

        const resumo = d.ocupados.length === 0
            ? "Nenhum horário ocupado neste dia."
            : `${d.ocupados.length} horário(s) com visitas já agendadas neste dia.`;

        el.innerHTML = `
            <div class="sv-msg info">Leito ${esc(d.leito.numero)} • Ala ${esc(d.leito.ala)} — ${resumo}</div>
            <div class="sv-lista">${linhas}</div>`;
    } catch (erro) {
        erroEm(el, erro);
    }
}


// ------------------------------------------------------------
// 7. CADASTRO DE VISITANTE COM VÍNCULO A PACIENTE E LEITO
// ------------------------------------------------------------

function mascaraCpf(evento) {
    let v = evento.target.value.replace(/\D/g, "").slice(0, 11);
    if (v.length > 9) v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
    else if (v.length > 6) v = v.replace(/(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
    else if (v.length > 3) v = v.replace(/(\d{3})(\d{1,3})/, "$1.$2");
    evento.target.value = v;
}

async function enviarCadastro(evento) {
    evento.preventDefault();
    if (!temSessao()) {
        mensagem("cadastro-msg", "erro", "Valide o token de acesso antes de cadastrar um visitante.");
        return;
    }
    if (!document.getElementById("cad-termo").checked) {
        mensagem("cadastro-msg", "erro", "É necessário aceitar o termo de consentimento (LGPD).");
        return;
    }

    const botao = document.getElementById("btn-cadastrar");
    botao.disabled = true;
    botao.textContent = "Cadastrando...";

    try {
        const d = await api("/visitantes/cadastro-vinculado", {
            method: "POST",
            body: {
                nome: document.getElementById("cad-nome").value.trim(),
                cpf: document.getElementById("cad-cpf").value,
                data_nascimento: document.getElementById("cad-nascimento").value,
                tipo: document.getElementById("cad-tipo").value,
                parentesco: document.getElementById("cad-parentesco").value.trim(),
                termo_consentimento: true,
                id_paciente: sessao.paciente.id,
                id_leito: sessao.leito.id,
            },
        });
        mensagem("cadastro-msg", "ok",
            `${d.visitante.nome} foi ${d.reutilizado ? "vinculado(a)" : "cadastrado(a) e vinculado(a)"} ao paciente ` +
            `${d.paciente.nome} (leito ${d.leito.numero}).`);
        document.getElementById("form-cadastro").reset();
        document.getElementById("cad-paciente").value = sessao.paciente.nome;
        document.getElementById("cad-leito").value =
            `Leito ${sessao.leito.numero} • Ala ${sessao.leito.ala} • Bloco ${sessao.leito.bloco}`;
    } catch (erro) {
        mensagem("cadastro-msg", "erro", erro.message);
    } finally {
        botao.disabled = false;
        botao.textContent = "Cadastrar e vincular";
    }
}


// ############################################################
// TELA: PAINEL DE GESTÃO (painel.html)
// ############################################################

let ultimoHistorico = null;

async function iniciarPainel() {
    configurarAbas(function (aba) {
        if (aba === "historico" && !ultimoHistorico) carregarHistorico();
        if (aba === "auditoria") carregarAuditoria();
        if (aba === "turnos") carregarTurnos();
    });

    ["hist", "aud", "turno"].forEach(function (prefixo) {
        document.getElementById(`${prefixo}-inicio`).value = hojeISO(-30);
        document.getElementById(`${prefixo}-fim`).value = hojeISO(0);
    });

    document.getElementById("btn-historico").addEventListener("click", carregarHistorico);
    document.getElementById("btn-historico-csv").addEventListener("click", exportarHistoricoCsv);
    document.getElementById("btn-auditoria").addEventListener("click", carregarAuditoria);
    document.getElementById("btn-turnos").addEventListener("click", carregarTurnos);
    document.getElementById("acessos-paciente").addEventListener("change", carregarVinculos);

    await carregarPacientes();
    carregarVinculos();
}

async function carregarPacientes() {
    let pacientes = [];
    try {
        pacientes = await api("/pacientes");
    } catch (erro) {
        mensagem("acessos-msg", "erro", erro.message);
    }

    document.querySelectorAll(".sel-paciente").forEach(function (select) {
        const todos = select.dataset.todos ? '<option value="">Todos os pacientes</option>' : "";
        select.innerHTML = todos + pacientes.map(p => `<option value="${p.id}">${esc(p.nome)}</option>`).join("");
    });
}


// ------------------------------------------------------------
// 4. REVOGAR ACESSO DO VISITANTE
// ------------------------------------------------------------

async function carregarVinculos() {
    const el = document.getElementById("acessos-conteudo");
    const idPaciente = document.getElementById("acessos-paciente").value;
    if (!idPaciente) {
        el.innerHTML = '<p class="sv-vazio">Nenhum paciente cadastrado.</p>';
        return;
    }
    carregando(el);
    try {
        const lista = await api(`/pacientes/${idPaciente}/visitantes`);
        if (lista.length === 0) {
            el.innerHTML = '<p class="sv-vazio">Nenhum visitante vinculado a este paciente.</p>';
            return;
        }

        const linhas = lista.map(v => `
            <tr>
                <td><strong>${esc(v.nome)}</strong><small>CPF ${esc(v.cpf)}</small></td>
                <td>${esc(v.tipo)}<small>${esc(v.parentesco || "—")}</small></td>
                <td>Leito ${esc(v.leito.numero)}<small>Ala ${esc(v.leito.ala)}</small></td>
                <td>${v.visitas_futuras}</td>
                <td>${v.ativo
                    ? '<span class="sv-badge ok">Acesso ativo</span>'
                    : `<span class="sv-badge danger">Revogado</span><small>${dataHora(v.revogado_em)}${v.motivo_revogacao ? " • " + esc(v.motivo_revogacao) : ""}</small>`}</td>
                <td>${v.ativo ? `<button class="sv-btn perigo pequeno" data-revogar="${v.id_visitante}" data-nome="${esc(v.nome)}">Revogar acesso</button>` : "—"}</td>
            </tr>`).join("");

        el.innerHTML = `
            <div class="sv-tabela-wrap">
                <table class="sv-tabela">
                    <thead><tr><th>Visitante</th><th>Tipo / parentesco</th><th>Leito</th><th>Visitas futuras</th><th>Situação</th><th>Ação</th></tr></thead>
                    <tbody>${linhas}</tbody>
                </table>
            </div>`;

        el.querySelectorAll("[data-revogar]").forEach(b =>
            b.addEventListener("click", () => revogarAcesso(b.dataset.revogar, b.dataset.nome, idPaciente)));
    } catch (erro) {
        erroEm(el, erro);
    }
}

async function revogarAcesso(idVisitante, nome, idPaciente) {
    const motivo = prompt(`Revogar o acesso de ${nome}?\nAs visitas futuras dele(a) serão canceladas.\n\nMotivo (opcional):`);
    if (motivo === null) return;
    try {
        const d = await api(`/visitantes/${idVisitante}/revogar-acesso`, {
            method: "POST",
            body: { id_paciente: Number(idPaciente), motivo: motivo },
        });
        mensagem("acessos-msg", "ok", `Acesso de ${d.nome} revogado. ${d.visitas_canceladas} visita(s) futura(s) cancelada(s).`);
        carregarVinculos();
    } catch (erro) {
        mensagem("acessos-msg", "erro", erro.message);
    }
}


// ------------------------------------------------------------
// 8. RELATÓRIO DE HISTÓRICO DE VISITAS
// ------------------------------------------------------------

function filtrosPeriodo(prefixo, nomeInicio, nomeFim) {
    const params = new URLSearchParams();
    const inicio = document.getElementById(`${prefixo}-inicio`).value;
    const fim = document.getElementById(`${prefixo}-fim`).value;
    const paciente = document.getElementById(`${prefixo}-paciente`);
    if (inicio) params.set(nomeInicio, inicio);
    if (fim) params.set(nomeFim, fim);
    if (paciente && paciente.value) params.set("id_paciente", paciente.value);
    return params.toString();
}

async function carregarHistorico() {
    const el = document.getElementById("historico-conteudo");
    carregando(el);
    try {
        const d = await api(`/relatorios/historico-visitas?${filtrosPeriodo("hist", "data_inicio", "data_fim")}`);
        ultimoHistorico = d;
        const r = d.resumo;

        const cards = [
            ["Total de visitas", r.total],
            ["Concluídas", r.concluida],
            ["Agendadas", r.agendada],
            ["Não compareceram", r.nao_compareceu],
            ["Canceladas", r.cancelada],
        ].map(([t, n]) => `<div class="sv-card"><div class="sv-card-titulo">${t}</div><div class="sv-numero">${n}</div></div>`).join("");

        const linhas = d.visitas.length === 0
            ? '<tr><td colspan="7" class="sv-vazio">Nenhuma visita no período.</td></tr>'
            : d.visitas.map(v => `
                <tr>
                    <td>${soData(v.data_hora)}<small>${soHora(v.data_hora)}</small></td>
                    <td>${esc(v.paciente.nome)}</td>
                    <td>${esc(v.visitante.nome)}<small>${esc(v.visitante.tipo)}</small></td>
                    <td>Leito ${esc(v.leito.numero)}<small>${esc(v.leito.ala)}</small></td>
                    <td>${soHora(v.checkin)}</td>
                    <td>${soHora(v.checkout)}</td>
                    <td>${badgeSituacao(v)}</td>
                </tr>`).join("");

        el.innerHTML = `
            <div class="sv-grid" style="margin-bottom:20px">${cards}</div>
            <div class="sv-tabela-wrap">
                <table class="sv-tabela">
                    <thead><tr><th>Data / hora</th><th>Paciente</th><th>Visitante</th><th>Leito</th><th>Entrada</th><th>Saída</th><th>Situação</th></tr></thead>
                    <tbody>${linhas}</tbody>
                </table>
            </div>`;
    } catch (erro) {
        erroEm(el, erro);
    }
}

function exportarHistoricoCsv() {
    if (!ultimoHistorico || ultimoHistorico.visitas.length === 0) {
        alert("Gere o relatório antes de exportar.");
        return;
    }
    const cabecalho = ["Data", "Hora", "Paciente", "Visitante", "Tipo", "Leito", "Ala", "Entrada", "Saída", "Permanência (min)", "Situação"];
    const linhas = ultimoHistorico.visitas.map(v => [
        soData(v.data_hora), soHora(v.data_hora), v.paciente.nome, v.visitante.nome, v.visitante.tipo,
        v.leito.numero, v.leito.ala, v.checkin ? dataHora(v.checkin) : "", v.checkout ? dataHora(v.checkout) : "",
        v.permanencia_minutos === null ? "" : v.permanencia_minutos, v.situacao_texto,
    ]);
    const csv = [cabecalho].concat(linhas)
        .map(l => l.map(c => `"${String(c).replace(/"/g, '""')}"`).join(";"))
        .join("\r\n");

    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `historico-visitas-${hojeISO(0)}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
}


// ------------------------------------------------------------
// 9. AUDITORIA DE CHECK-IN E CHECK-OUT
// ------------------------------------------------------------

async function carregarAuditoria() {
    const el = document.getElementById("auditoria-conteudo");
    carregando(el);
    try {
        const d = await api(`/relatorios/auditoria-acessos?${filtrosPeriodo("aud", "periodo_inicio", "periodo_fim")}`);
        const r = d.resumo;

        const cards = [
            ["Visitas no período", r.total_visitas],
            ["Check-ins", r.total_checkins],
            ["Check-outs", r.total_checkouts],
            ["Sem check-out", r.sem_checkout],
            ["Com alerta", r.com_alerta],
            ["Permanência média", r.permanencia_media_minutos === null ? "—" : r.permanencia_media_minutos + " min"],
        ].map(([t, n]) => `<div class="sv-card"><div class="sv-card-titulo">${t}</div><div class="sv-numero">${n}</div></div>`).join("");

        const linhas = d.registros.length === 0
            ? '<tr><td colspan="8" class="sv-vazio">Nenhum registro no período.</td></tr>'
            : d.registros.map(v => {
                let acao = "—";
                if (v.situacao === "agendada") {
                    acao = `<button class="sv-btn secundario pequeno" data-checkin="${v.id_visita}">Registrar entrada</button>`;
                } else if (v.situacao === "em_andamento") {
                    acao = `<button class="sv-btn secundario pequeno" data-checkout="${v.id_visita}">Registrar saída</button>`;
                }
                const alertas = v.alertas.length
                    ? v.alertas.map(a => `<span class="sv-badge danger">${esc(a.texto)}</span>`).join(" ")
                    : '<span class="sv-badge ok">OK</span>';
                return `
                    <tr>
                        <td>${soData(v.data_hora)}<small>${soHora(v.data_hora)}</small></td>
                        <td>${esc(v.visitante.nome)}<small>${esc(v.paciente.nome)}</small></td>
                        <td>Leito ${esc(v.leito.numero)}</td>
                        <td>${dataHora(v.checkin)}<small>${esc(v.checkin_origem || "")}</small></td>
                        <td>${dataHora(v.checkout)}<small>${esc(v.checkout_origem || "")}</small></td>
                        <td>${v.permanencia_minutos === null ? "—" : v.permanencia_minutos + " min"}</td>
                        <td>${badgeSituacao(v)}<div style="margin-top:6px">${alertas}</div></td>
                        <td>${acao}</td>
                    </tr>`;
            }).join("");

        el.innerHTML = `
            <div class="sv-grid" style="margin-bottom:20px">${cards}</div>
            <div class="sv-tabela-wrap">
                <table class="sv-tabela">
                    <thead><tr><th>Agendada</th><th>Visitante / paciente</th><th>Leito</th><th>Check-in</th><th>Check-out</th><th>Permanência</th><th>Situação / alertas</th><th>Ação</th></tr></thead>
                    <tbody>${linhas}</tbody>
                </table>
            </div>`;

        el.querySelectorAll("[data-checkin]").forEach(b => b.addEventListener("click", () => registrarAcesso(b.dataset.checkin, "checkin")));
        el.querySelectorAll("[data-checkout]").forEach(b => b.addEventListener("click", () => registrarAcesso(b.dataset.checkout, "checkout")));
    } catch (erro) {
        erroEm(el, erro);
    }
}

async function registrarAcesso(idVisita, tipo) {
    try {
        await api(`/visitas/${idVisita}/${tipo}`, { method: "POST" });
        mensagem("auditoria-msg", "ok", tipo === "checkin" ? "Entrada registrada." : "Saída registrada.");
        carregarAuditoria();
    } catch (erro) {
        mensagem("auditoria-msg", "erro", erro.message);
    }
}


// ------------------------------------------------------------
// 10. ESTATÍSTICA DE VISITANTES POR TURNO
// ------------------------------------------------------------

async function carregarTurnos() {
    const el = document.getElementById("turnos-conteudo");
    carregando(el);
    try {
        const d = await api(`/relatorios/visitantes-por-turno?${filtrosPeriodo("turno", "periodo_inicio", "periodo_fim")}`);
        const maior = Math.max(1, ...d.turnos.map(t => t.total_visitantes));

        const cards = d.turnos.map(t => `
            <div class="sv-card">
                <div class="sv-card-titulo">${esc(t.turno)} • ${esc(t.faixa)}</div>
                <div class="sv-numero">${t.total_visitantes}</div>
                <div class="sv-card-texto">${t.visitantes_unicos} visitante(s) diferente(s) • ${t.checkins} check-in(s) • ${t.canceladas} cancelada(s)</div>
                <div class="sv-barra"><div style="width:${Math.round((t.total_visitantes / maior) * 100)}%"></div></div>
            </div>`).join("");

        const g = d.total_geral;
        el.innerHTML = `
            <div class="sv-grid">${cards}</div>
            <h3>Total do período</h3>
            <div class="sv-grid">
                <div class="sv-card"><div class="sv-card-titulo">Total de visitantes</div><div class="sv-numero">${g.total_visitantes}</div></div>
                <div class="sv-card"><div class="sv-card-titulo">Visitantes diferentes</div><div class="sv-numero">${g.visitantes_unicos}</div></div>
                <div class="sv-card"><div class="sv-card-titulo">Check-ins</div><div class="sv-numero">${g.checkins}</div></div>
                <div class="sv-card"><div class="sv-card-titulo">Canceladas</div><div class="sv-numero">${g.canceladas}</div></div>
            </div>`;
    } catch (erro) {
        erroEm(el, erro);
    }
}
