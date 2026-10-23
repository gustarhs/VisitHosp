// ============================================================
// VISITHOSP - VOUCHER / QR CODE (qrcode.html)
// ============================================================
//
// Este arquivo faltava no repositório. Ele lê os dados salvos no
// localStorage (pelas telas de token e agendamento) e dá
// funcionalidade real à tela do voucher: gera o QR code, roda o
// timer de validade, renova o código a cada 8s e liga os botões
// de imprimir/compartilhar.
//
// TODO (integração futura com o backend, quando o fluxo de
// agendamento virar POST /visitas de verdade):
//   - Trocar a geração do QR/hash local por uma chamada real,
//     por exemplo GET /visitas/<id>/pode-gerar-qrcode antes de
//     desenhar o QR, e possivelmente um endpoint que gere um
//     código de uso único no servidor.
//   - O totem de entrada valida o código via
//     POST /totem/validar-entrada { codigo_qrcode }.


const TEMPO_VALIDADE_SEGUNDOS = 15 * 60;
const INTERVALO_RENOVACAO_SEGUNDOS = 8;

let segundosRestantes = TEMPO_VALIDADE_SEGUNDOS;
let segundosParaRenovar = INTERVALO_RENOVACAO_SEGUNDOS;
let qrCodeInstancia = null;
let tokenAcesso = null;


// ============================================================
// INICIALIZAÇÃO
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    const qrDiv = document.getElementById("qrcode");
    if (!qrDiv) {
        return; // essa lógica só roda na tela do voucher
    }

    preencherPacienteVoucher();
    preencherDetalhesVisita();

    tokenAcesso = localStorage.getItem("visitHospToken") || "SEM-TOKEN";

    gerarNovoCodigo();
    iniciarTimers();
    ligarBotoes();
});


// ============================================================
// PACIENTE (mesma fonte que a inicial.html usa)
// ============================================================

function preencherPacienteVoucher() {

    const dadosSalvos = localStorage.getItem("visitHospInternacao");

    const nomeEl = document.getElementById("patient-name");
    const localizacaoEl = document.getElementById("patient-location");
    const avatarEl = document.getElementById("patient-avatar");

    if (!dadosSalvos) {
        if (nomeEl) nomeEl.textContent = "Nenhuma internação encontrada";
        if (localizacaoEl) localizacaoEl.textContent = "Insira um token de acesso válido.";
        if (avatarEl) avatarEl.textContent = "--";
        return;
    }

    let dados;
    try {
        dados = JSON.parse(dadosSalvos);
    } catch (erro) {
        console.error("Erro ao ler dados da internação:", erro);
        return;
    }

    const paciente = dados.paciente;
    const leito = dados.leito;

    if (!paciente) {
        return;
    }

    const nomeCompleto = paciente.nome || "Paciente";

    if (nomeEl) {
        nomeEl.textContent = nomeCompleto;
    }

    if (localizacaoEl && leito) {
        localizacaoEl.textContent =
            `Quarto ${leito.numero} • Leito ${leito.id} • Ala ${leito.ala}`;
    }

    if (avatarEl) {
        const partes = nomeCompleto.trim().split(" ");
        const primeiraLetra = partes[0]?.charAt(0) || "";
        const ultimaLetra = partes.length > 1 ? partes[partes.length - 1].charAt(0) : "";
        avatarEl.textContent = (primeiraLetra + ultimaLetra).toUpperCase();
    }
}


// ============================================================
// DETALHES DA VISITA (data, horário, visitante, protocolo)
// ============================================================

function preencherDetalhesVisita() {

    const visitDateEl = document.getElementById("visit-date");
    const visitTimeEl = document.getElementById("visit-time");
    const visitorNameEl = document.getElementById("visitor-name");
    const protocolEl = document.getElementById("protocol");

    const agendamentoSalvo = localStorage.getItem("visitHospAgendamento");

    if (agendamentoSalvo) {
        try {
            const agendamento = JSON.parse(agendamentoSalvo);

            if (visitDateEl && agendamento.data) {
                const data = new Date(agendamento.data);
                visitDateEl.textContent = data.toLocaleDateString("pt-BR", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric"
                });
            }

            if (visitTimeEl && agendamento.horario) {
                visitTimeEl.textContent = agendamento.horario;
            }

        } catch (erro) {
            console.error("Erro ao ler agendamento salvo:", erro);
        }
    }

    // TODO: ainda não existe uma tela de identificação do visitante
    // (nome/documento de quem está visitando). Quando existir, ler
    // daqui em vez do fallback abaixo.
    if (visitorNameEl) {
        visitorNameEl.textContent = "Visitante não identificado";
    }

    if (protocolEl) {
        protocolEl.textContent = gerarProtocolo();
    }
}

function gerarProtocolo() {
    const agora = new Date();
    const aaaammdd =
        agora.getFullYear().toString() +
        String(agora.getMonth() + 1).padStart(2, "0") +
        String(agora.getDate()).padStart(2, "0");
    const aleatorio = Math.floor(Math.random() * 9000 + 1000);
    return `VH-${aaaammdd}-${aleatorio}`;
}


// ============================================================
// GERAÇÃO DO QR CODE + HASH
// ============================================================

async function gerarNovoCodigo() {

    const conteudo = `${tokenAcesso}|${Date.now()}`;

    desenharQrCode(conteudo);

    const hashEl = document.getElementById("hash");
    if (hashEl) {
        const hash = await calcularSha256(conteudo);
        hashEl.textContent = `SHA256: ${hash.slice(0, 32)}...`;
    }
}

function desenharQrCode(conteudo) {

    const qrDiv = document.getElementById("qrcode");
    if (!qrDiv || typeof QRCode === "undefined") {
        return;
    }

    qrDiv.innerHTML = "";

    qrCodeInstancia = new QRCode(qrDiv, {
        text: conteudo,
        width: 200,
        height: 200,
        colorDark: "#000000",
        colorLight: "#ffffff"
    });
}

async function calcularSha256(texto) {
    try {
        const dados = new TextEncoder().encode(texto);
        const hashBuffer = await crypto.subtle.digest("SHA-256", dados);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
    } catch (erro) {
        // crypto.subtle exige contexto seguro (https ou localhost).
        // Se não estiver disponível, mostra um placeholder em vez de quebrar a tela.
        console.warn("crypto.subtle indisponível, usando hash simulado:", erro);
        return "indisponivel-neste-ambiente".padEnd(64, "0");
    }
}


// ============================================================
// TIMERS (validade + renovação automática)
// ============================================================

function iniciarTimers() {

    atualizarTimerVisual();

    setInterval(function () {

        segundosRestantes--;
        segundosParaRenovar--;

        if (segundosParaRenovar <= 0) {
            segundosParaRenovar = INTERVALO_RENOVACAO_SEGUNDOS;
            gerarNovoCodigo();
        }

        if (segundosRestantes <= 0) {
            segundosRestantes = TEMPO_VALIDADE_SEGUNDOS;
        }

        atualizarTimerVisual();

    }, 1000);
}

function atualizarTimerVisual() {

    const timerEl = document.getElementById("timer");
    const refreshEl = document.getElementById("refresh-timer");
    const progressEl = document.getElementById("progress-bar");

    if (timerEl) {
        const minutos = String(Math.floor(segundosRestantes / 60)).padStart(2, "0");
        const segundos = String(segundosRestantes % 60).padStart(2, "0");
        timerEl.textContent = `${minutos}:${segundos}`;
    }

    if (refreshEl) {
        refreshEl.textContent = `${segundosParaRenovar}s`;
    }

    if (progressEl) {
        const percentual = (segundosParaRenovar / INTERVALO_RENOVACAO_SEGUNDOS) * 100;
        progressEl.style.width = `${percentual}%`;
    }
}


// ============================================================
// BOTÕES: IMPRIMIR E COMPARTILHAR
// ============================================================

function ligarBotoes() {

    const printButton = document.getElementById("print-button");
    const shareButton = document.getElementById("share-button");

    if (printButton) {
        printButton.addEventListener("click", function () {
            window.print();
        });
    }

    if (shareButton) {
        shareButton.addEventListener("click", async function () {

            const protocolo = document.getElementById("protocol")?.textContent || "";
            const texto = `Voucher de visita VisitHosp - Protocolo ${protocolo}`;

            if (navigator.share) {
                try {
                    await navigator.share({ title: "Voucher VisitHosp", text: texto });
                } catch (erro) {
                    console.log("Compartilhamento cancelado:", erro);
                }
                return;
            }

            try {
                await navigator.clipboard.writeText(texto);
                alert("Link copiado para a área de transferência.");
            } catch (erro) {
                console.error("Não foi possível copiar:", erro);
            }
        });
    }
}