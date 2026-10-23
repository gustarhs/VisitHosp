// ============================================================
// VISITHOSP - SCRIPT PRINCIPAL
// ============================================================


// ============================================================
// CONFIGURAÇÃO DA API
// ============================================================

const API_URL = "http://localhost:8000";


// ============================================================
// MÁSCARA DO TOKEN - BLOCO 1
// LETRA + NÚMERO + LETRA
// ============================================================

function maskTel1() {

    const input = document.getElementById("input1");

    if (!input) return;

    let valor = input.value.toUpperCase();

    valor = valor.replace(/[^A-Z0-9]/g, "");

    valor = valor.slice(0, 3);


    if (valor.length >= 1 && !/[A-Z]/.test(valor[0])) {
        valor = valor.slice(1);
    }


    if (valor.length >= 2 && !/[0-9]/.test(valor[1])) {
        valor = valor[0] + valor.slice(2);
    }


    if (valor.length >= 3 && !/[A-Z]/.test(valor[2])) {
        valor = valor.slice(0, 2);
    }


    input.value = valor;


    if (valor.length === 3) {

        const input2 = document.getElementById("input2");

        if (input2) {
            input2.focus();
        }

    }

}



// ============================================================
// MÁSCARA DO TOKEN - BLOCO 2
// NÚMERO + LETRA + NÚMERO
// ============================================================

function maskTel2() {

    const input = document.getElementById("input2");

    if (!input) return;

    let valor = input.value.toUpperCase();

    valor = valor.replace(/[^A-Z0-9]/g, "");

    valor = valor.slice(0, 3);


    if (valor.length >= 1 && !/[0-9]/.test(valor[0])) {
        valor = valor.slice(1);
    }


    if (valor.length >= 2 && !/[A-Z]/.test(valor[1])) {
        valor = valor[0] + valor.slice(2);
    }


    if (valor.length >= 3 && !/[0-9]/.test(valor[2])) {
        valor = valor.slice(0, 2);
    }


    input.value = valor;


    if (valor.length === 3) {

        const input3 = document.getElementById("input3");

        if (input3) {
            input3.focus();
        }

    }

}



// ============================================================
// MÁSCARA DO TOKEN - BLOCO 3
// NÚMERO + LETRA + LETRA
// ============================================================

function maskTel3() {

    const input = document.getElementById("input3");

    if (!input) return;

    let valor = input.value.toUpperCase();

    valor = valor.replace(/[^A-Z0-9]/g, "");

    valor = valor.slice(0, 3);


    if (valor.length >= 1 && !/[0-9]/.test(valor[0])) {
        valor = valor.slice(1);
    }


    if (valor.length >= 2 && !/[A-Z]/.test(valor[1])) {
        valor = valor[0] + valor.slice(2);
    }


    if (valor.length >= 3 && !/[A-Z]/.test(valor[2])) {
        valor = valor.slice(0, 2);
    }


    input.value = valor;


    if (valor.length === 3) {

        const button = document.getElementById("button");

        if (button) {
            button.focus();
        }

    }

}



// ============================================================
// VALIDAR TOKEN PELO BACKEND
// ============================================================

async function validarToken() {

    const input1 = document.getElementById("input1");
    const input2 = document.getElementById("input2");
    const input3 = document.getElementById("input3");
    const button = document.getElementById("button");


    if (!input1 || !input2 || !input3) {

        console.error("Campos do token não encontrados.");

        return;

    }


    const t1 = input1.value.trim().toUpperCase();
    const t2 = input2.value.trim().toUpperCase();
    const t3 = input3.value.trim().toUpperCase();


    const tokenDigitado = t1 + t2 + t3;


    // ---------------------------------------------
    // Verifica preenchimento
    // ---------------------------------------------

    if (
        t1.length !== 3 ||
        t2.length !== 3 ||
        t3.length !== 3
    ) {

        alert("Digite o token completo antes de continuar.");

        return;

    }


    // ---------------------------------------------
    // Desabilita botão durante a consulta
    // ---------------------------------------------

    if (button) {

        button.disabled = true;

        button.textContent = "Validando...";

    }


    try {

        console.log(
            "Consultando backend com token:",
            tokenDigitado
        );


        // -----------------------------------------
        // ENVIA TOKEN PARA O FLASK
        // -----------------------------------------

        const resposta = await fetch(
            `${API_URL}/internacoes/validar-token`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    codigo_token: tokenDigitado
                })
            }
        );


        const dados = await resposta.json();


        console.log(
            "Resposta do backend:",
            dados
        );


        // -----------------------------------------
        // TOKEN INVÁLIDO
        // -----------------------------------------

        if (!resposta.ok) {

            alert(
                dados.erro ||
                "Token inválido, expirado ou inexistente."
            );

            return;

        }


        // -----------------------------------------
        // TOKEN VÁLIDO
        // -----------------------------------------

        if (!dados.internacao) {

            alert(
                "O backend não retornou os dados da internação."
            );

            return;

        }


        // -----------------------------------------
        // SALVA OS DADOS
        // -----------------------------------------

        localStorage.setItem(
            "visitHospToken",
            tokenDigitado
        );


        localStorage.setItem(
            "visitHospInternacao",
            JSON.stringify(dados)
        );


        // -----------------------------------------
        // VAI PARA A PÁGINA
        // -----------------------------------------

        window.location.href = "inicial.html";

    }

    catch (erro) {

        console.error(
            "Erro ao conectar com o backend:",
            erro
        );


        alert(
            "Não foi possível conectar ao servidor. " +
            "Verifique se o Flask está rodando."
        );

    }

    finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "Verificar Token e Continuar →";

        }

    }

}



// ============================================================
// VARIÁVEIS DO AGENDAMENTO
// ============================================================

let dataSelecionada = null;

let mesAtual = new Date().getMonth();

let anoAtual = new Date().getFullYear();

let horarioSelecionado = null;

let dadosInternacao = null;



// ============================================================
// INICIALIZAÇÃO DA PÁGINA
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {


        // =============================================
        // SE ESTAMOS NO INDEX
        // =============================================

        const input1 =
            document.getElementById("input1");


        if (input1) {

            return;

        }


        // =============================================
        // SE ESTAMOS NA INICIAL
        // =============================================

        const calendarGrid =
            document.getElementById(
                "calendar-grid"
            );


        if (!calendarGrid) {

            return;

        }


        console.log(
            "Inicializando página de agendamento..."
        );


        carregarDadosInternacao();


        configurarCalendario();


        renderizarCalendario();


        selecionarPrimeiroDiaDisponivel();

    }
);



// ============================================================
// CARREGAR DADOS DA INTERNAÇÃO
// ============================================================

function carregarDadosInternacao() {

    const dadosSalvos =
        localStorage.getItem(
            "visitHospInternacao"
        );


    // =============================================
    // NÃO EXISTE DADO
    // =============================================

    if (!dadosSalvos) {

        mostrarEstadoSemInternacao();

        return;

    }


    try {

        dadosInternacao =
            JSON.parse(dadosSalvos);


        console.log(
            "Internação carregada:",
            dadosInternacao
        );


        preencherPaciente();


    }

    catch (erro) {

        console.error(
            "Erro ao ler dados da internação:",
            erro
        );


        mostrarEstadoSemInternacao();

    }

}



// ============================================================
// PREENCHER PACIENTE NA TELA
// ============================================================

function preencherPaciente() {

    if (!dadosInternacao) {

        return;

    }


    const paciente =
        dadosInternacao.paciente;


    const leito =
        dadosInternacao.leito;


    const internacao =
        dadosInternacao.internacao;


    if (!paciente) {

        console.error(
            "Paciente não retornado pelo backend."
        );

        return;

    }


    // =============================================
    // NOME
    // =============================================

    const nome =
        document.getElementById(
            "patient-name"
        );


    if (nome) {

        nome.textContent =
            paciente.nome || "Paciente";

    }


    // =============================================
    // LOCALIZAÇÃO
    // =============================================

    const localizacao =
        document.getElementById(
            "patient-location"
        );


    if (localizacao && leito) {

        localizacao.textContent =
            `Quarto ${leito.numero} • ` +
            `Leito ${leito.id} • ` +
            `Ala ${leito.ala}`;

    }


    // =============================================
    // AVATAR
    // =============================================

    const avatar =
        document.getElementById(
            "patient-avatar"
        );


    if (avatar) {

        const nomeCompleto =
            paciente.nome || "Paciente";


        const partes =
            nomeCompleto
                .trim()
                .split(" ");


        const primeiraLetra =
            partes[0]?.charAt(0) || "";


        const ultimaLetra =
            partes.length > 1
                ? partes[partes.length - 1]
                    .charAt(0)
                : "";


        avatar.textContent =
            (
                primeiraLetra +
                ultimaLetra
            ).toUpperCase();

    }


    // =============================================
    // STATUS
    // =============================================

    const status =
        document.getElementById(
            "patient-status"
        );


    if (status) {

        const ativo =
            internacao &&
            internacao.status === true;


        if (ativo) {

            status.innerHTML =
                `<span class="circle"></span>
                 <span>Disponível</span>`;

        }

        else {

            status.innerHTML =
                `<span class="circle"></span>
                 <span>Indisponível</span>`;

        }

    }


    // =============================================
    // QUARTO NA OCUPAÇÃO
    // =============================================

    const roomNumber =
        document.getElementById(
            "room-number"
        );


    if (roomNumber && leito) {

        roomNumber.textContent =
            leito.numero;

    }

}



// ============================================================
// ESTADO SEM INTERNAÇÃO
// ============================================================

function mostrarEstadoSemInternacao() {

    const nome =
        document.getElementById(
            "patient-name"
        );


    const localizacao =
        document.getElementById(
            "patient-location"
        );


    const avatar =
        document.getElementById(
            "patient-avatar"
        );


    if (nome) {

        nome.textContent =
            "Nenhuma internação encontrada";

    }


    if (localizacao) {

        localizacao.textContent =
            "Insira um token de acesso válido para continuar.";

    }


    if (avatar) {

        avatar.textContent = "--";

    }

}



// ============================================================
// CALENDÁRIO
// ============================================================

function configurarCalendario() {

    const prevMonth =
        document.getElementById(
            "prev-month"
        );


    const nextMonth =
        document.getElementById(
            "next-month"
        );


    if (prevMonth) {

        prevMonth.addEventListener(
            "click",
            function () {

                mesAtual--;

                if (mesAtual < 0) {

                    mesAtual = 11;

                    anoAtual--;

                }

                renderizarCalendario();

            }
        );

    }


    if (nextMonth) {

        nextMonth.addEventListener(
            "click",
            function () {

                mesAtual++;

                if (mesAtual > 11) {

                    mesAtual = 0;

                    anoAtual++;

                }

                renderizarCalendario();

            }
        );

    }

}



// ============================================================
// RENDERIZAR CALENDÁRIO
// ============================================================

function renderizarCalendario() {

    const calendarGrid =
        document.getElementById(
            "calendar-grid"
        );


    const currentMonth =
        document.getElementById(
            "current-month"
        );


    if (!calendarGrid) {

        return;

    }


    calendarGrid.innerHTML = "";


    const nomeMes =
        new Intl.DateTimeFormat(
            "pt-BR",
            {
                month: "long"
            }
        ).format(
            new Date(
                anoAtual,
                mesAtual,
                1
            )
        );


    if (currentMonth) {

        currentMonth.textContent =
            nomeMes.charAt(0).toUpperCase() +
            nomeMes.slice(1) +
            " " +
            anoAtual;

    }


    const primeiroDia =
        new Date(
            anoAtual,
            mesAtual,
            1
        ).getDay();


    const quantidadeDias =
        new Date(
            anoAtual,
            mesAtual + 1,
            0
        ).getDate();


    for (
        let i = 0;
        i < primeiroDia;
        i++
    ) {

        const vazio =
            document.createElement("div");


        vazio.classList.add(
            "calendar-day",
            "empty"
        );


        calendarGrid.appendChild(
            vazio
        );

    }


    for (
        let dia = 1;
        dia <= quantidadeDias;
        dia++
    ) {

        const botao =
            document.createElement(
                "button"
            );


        botao.type = "button";


        botao.classList.add(
            "calendar-day"
        );


        botao.textContent = dia;


        const hoje =
            new Date();

        const dataDoBotao = new Date(anoAtual, mesAtual, dia);
        dataDoBotao.setHours(0, 0, 0, 0);

        const hojeSemHora = new Date();
        hojeSemHora.setHours(0, 0, 0, 0);

        if (dataDoBotao < hojeSemHora) {
            botao.disabled = true;
            botao.style.opacity = "0.35";
            botao.style.cursor = "not-allowed";
        }
        botao.addEventListener(
            "click",
            function () {

                selecionarData(
                    anoAtual,
                    mesAtual,
                    dia,
                    botao
                );

            }
        );


        calendarGrid.appendChild(
            botao
        );

    }

}



// ============================================================
// SELECIONAR DATA
// ============================================================

function selecionarData(
    ano,
    mes,
    dia,
    elemento
) {

    dataSelecionada =
        new Date(
            ano,
            mes,
            dia
        );


    document
        .querySelectorAll(
            ".calendar-day.selected"
        )
        .forEach(
            function (item) {

                item.classList.remove(
                    "selected"
                );

            }
        );


    elemento.classList.add(
        "selected"
    );


    carregarHorarios();

}



// ============================================================
// CARREGAR HORÁRIOS
// ============================================================

async function carregarHorarios() {

    const container = document.getElementById("horarios-disponiveis");

    if (!container) return;

    container.innerHTML = "";

    if (!dataSelecionada) return;

    if (!dadosInternacao || !dadosInternacao.internacao) {
        container.innerHTML = "<p>Nenhuma internação carregada. Valide o token novamente.</p>";
        return;
    }

    container.innerHTML = "<p>Carregando horários...</p>";

    const ano = dataSelecionada.getFullYear();
    const mes = String(dataSelecionada.getMonth() + 1).padStart(2, "0");
    const dia = String(dataSelecionada.getDate()).padStart(2, "0");
    const dataFormatada = `${ano}-${mes}-${dia}`;

    const idInternacao = dadosInternacao.internacao.id;

    let horarios = [];

    try {
        const resposta = await fetch(
            `${API_URL}/internacoes/${idInternacao}/horarios?data=${dataFormatada}`
        );

        if (!resposta.ok) {
            const erro = await resposta.json().catch(() => ({}));
            container.innerHTML = `<p>${erro.erro || "Não foi possível carregar os horários."}</p>`;
            return;
        }

        horarios = await resposta.json();

    } catch (erro) {
        console.error("Erro ao buscar horários:", erro);
        container.innerHTML = "<p>Não foi possível conectar ao servidor. Verifique se o Flask está rodando.</p>";
        return;
    }

    container.innerHTML = "";

    horarios.forEach(function (item) {

        const card = document.createElement("button");
        card.type = "button";
        card.classList.add("style");

        const icon = document.createElement("div");
        icon.classList.add("horario-icon");
        icon.textContent = "⏰";

        const info = document.createElement("div");
        info.classList.add("info-horarios");

        const horario = document.createElement("h1");
        horario.textContent = item.horario;

        const quantidade = document.createElement("p");
        quantidade.textContent = `${item.ocupacao} de ${item.capacidade} visitantes simultâneos`;

        info.appendChild(horario);
        info.appendChild(quantidade);

        const status = document.createElement("span");

        if (item.ocupacao >= item.capacidade) {
            status.classList.add("status-hours-lotado");
            status.textContent = "Lotado";
            card.classList.add("lotado");
            card.disabled = true;
        } else if (item.ocupacao === item.capacidade - 1) {
            status.classList.add("status-hours-quase");
            status.textContent = "Quase cheio";
        } else {
            status.classList.add("status-hours");
            status.textContent = "Disponível";
        }

        card.appendChild(icon);
        card.appendChild(info);
        card.appendChild(status);

        if (!card.disabled) {
            card.addEventListener("click", function () {
                selecionarHorario(item.horario, card);
            });
        }

        container.appendChild(card);
    });

}



// ============================================================
// SELECIONAR HORÁRIO
// ============================================================

function selecionarHorario(
    horario,
    elemento
) {

    horarioSelecionado =
        horario;


    document
        .querySelectorAll(
            ".style.selected"
        )
        .forEach(
            function (item) {

                item.classList.remove(
                    "selected"
                );

            }
        );


    elemento.classList.add(
        "selected"
    );


    const confirmar =
        document.getElementById(
            "confirma"
        );


    if (confirmar) {

        confirmar.disabled = false;

    }

}



// ============================================================
// SELECIONAR PRIMEIRO DIA
// ============================================================

function selecionarPrimeiroDiaDisponivel() {

    const primeiroDia =
        document.querySelector(
            ".calendar-day:not(.empty)"
        );


    if (primeiroDia) {

        primeiroDia.click();

    }

}



// ============================================================
// CONFIRMAR AGENDAMENTO
// ============================================================

async function obterIdPadrao(endpoint, nomeEntidade) {

    const resposta = await fetch(`${API_URL}/${endpoint}`);

    if (!resposta.ok) {
        throw new Error(`Não foi possível consultar ${nomeEntidade}.`);
    }

    const lista = await resposta.json();

    if (!Array.isArray(lista) || lista.length === 0) {
        throw new Error(`Nenhum ${nomeEntidade} cadastrado no banco ainda.`);
    }

    return lista[0].id;
}

async function confirmarAgendamento() {

    if (!dataSelecionada) {
        alert("Selecione uma data.");
        return;
    }

    if (!horarioSelecionado) {
        alert("Selecione um horário.");
        return;
    }

    if (!dadosInternacao || !dadosInternacao.internacao) {
        alert("Nenhuma internação carregada. Valide o token novamente.");
        return;
    }

    const botaoConfirmar = document.getElementById("confirma");
    const textoOriginal = botaoConfirmar ? botaoConfirmar.textContent : "Confirmar Visita";

    if (botaoConfirmar) {
        botaoConfirmar.disabled = true;
        botaoConfirmar.textContent = "Agendando...";
    }

    try {

        const horaInicio = horarioSelecionado.split(" - ")[0];
        const [hora, minuto] = horaInicio.split(":").map(Number);

        const ano = dataSelecionada.getFullYear();
        const mes = String(dataSelecionada.getMonth() + 1).padStart(2, "0");
        const dia = String(dataSelecionada.getDate()).padStart(2, "0");
        const horaFormatada = String(hora).padStart(2, "0");
        const minutoFormatado = String(minuto).padStart(2, "0");

        const dataHoraISO = `${ano}-${mes}-${dia}T${horaFormatada}:${minutoFormatado}:00`;

        const idVisitante = await obterIdPadrao("visitantes", "visitante");
        const idHospital = await obterIdPadrao("hospitais", "hospital");

        const qrCode = `VH-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;

        const resposta = await fetch(`${API_URL}/visitas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                data_hora: dataHoraISO,
                status: true,
                qr_code: qrCode,
                id_visitante: idVisitante,
                id_hospital: idHospital,
                id_internacao: dadosInternacao.internacao.id
            })
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro || "Não foi possível confirmar o agendamento.");
            return;
        }

        localStorage.setItem(
            "visitHospAgendamento",
            JSON.stringify({
                data: dataSelecionada,
                horario: horarioSelecionado,
                id_visita: dados.id,
                qr_code: dados.qr_code
            })
        );

        window.location.href = "token.html";

    } catch (erro) {
        console.error("Erro ao confirmar agendamento:", erro);
        alert(erro.message || "Não foi possível conectar ao servidor. Verifique se o Flask está rodando.");

    } finally {
        if (botaoConfirmar) {
            botaoConfirmar.disabled = false;
            botaoConfirmar.textContent = textoOriginal;
        }
    }
}


// ============================================================
// TELA DE TRIAGEM SANITÁRIA (token.html)
// ============================================================

function inicializarTriagem() {

    var perguntas = document.querySelectorAll("[data-pergunta]");
    if (perguntas.length === 0) return; // essa lógica só roda na tela de triagem

    perguntas.forEach(function (pergunta) {
        var botoes = pergunta.querySelectorAll(".opcao-btn");

        botoes.forEach(function (botao) {
            botao.addEventListener("click", function () {
                botoes.forEach(function (b) {
                    b.classList.remove("selecionada");
                });
                botao.classList.add("selecionada");

                pergunta.dataset.resposta = botao.dataset.valor;

                pergunta.classList.remove("respondida-sim", "respondida-nao");
                pergunta.classList.add(
                    botao.dataset.valor === "sim" ? "respondida-sim" : "respondida-nao"
                );

                atualizarProgressoPerguntas();
            });
        });
    });

    atualizarProgressoPerguntas();
}

function atualizarProgressoPerguntas() {

    var progresso = document.getElementById("progressoPerguntas");
    if (!progresso) return;

    var todasPerguntas = document.querySelectorAll("[data-pergunta]");
    var respondidas = document.querySelectorAll("[data-pergunta][data-resposta]");

    progresso.textContent = respondidas.length + " de " + todasPerguntas.length + " perguntas respondidas";
}

async function enviarDocumento(input) {

    const arquivo = input.files[0];
    if (!arquivo) return;

    const documento = input.closest(".documento");
    const badge = documento.querySelector(".doc-badge");
    const botao = documento.querySelector(".btn-upload");

    const textoOriginal = botao.textContent;
    botao.disabled = true;
    botao.textContent = "Enviando...";

    const formData = new FormData();
    formData.append("arquivo", arquivo);

    try {
        const resposta = await fetch(`${API_URL}/uploads`, {
            method: "POST",
            body: formData
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            alert(dados.erro || "Não foi possível enviar o documento.");
            botao.disabled = false;
            botao.textContent = textoOriginal;
            return;
        }

        documento.dataset.arquivo = dados.arquivo;

        badge.textContent = "Enviado";
        badge.classList.remove("badge-pendente");
        badge.classList.add("badge-enviado");

        botao.textContent = "✓ Enviado";
        botao.classList.add("btn-upload-feito");
        botao.disabled = true;

        atualizarProgressoPerguntas();

    } catch (erro) {
        console.error("Erro ao enviar documento:", erro);
        alert("Não foi possível conectar ao servidor. Verifique se o Flask está rodando.");
        botao.disabled = false;
        botao.textContent = textoOriginal;
    }
}

function alternarDeclaracao() {

    var checkbox = document.getElementById("declCheckbox");
    checkbox.classList.toggle("marcado");
    checkbox.textContent = checkbox.classList.contains("marcado") ? "✓" : "";
}

function enviarTriagem() {

    var todasPerguntas = document.querySelectorAll("[data-pergunta]");
    var perguntasRespondidas = document.querySelectorAll("[data-pergunta][data-resposta]");

    if (perguntasRespondidas.length < todasPerguntas.length) {
        alert("Responda todas as " + todasPerguntas.length + " perguntas do questionário antes de continuar.");
        return;
    }

    var declaracaoAceita = document.getElementById("declCheckbox").classList.contains("marcado");
    if (!declaracaoAceita) {
        alert("Você precisa concordar com a Declaração de Saúde para continuar.");
        return;
    }

    var botaoEnviar = document.getElementById("enviarTriagem");
    var resultadoSucesso = document.getElementById("resultadoSucesso");
    var resultadoErro = document.getElementById("resultadoErro");
    var resultadoErroTexto = document.getElementById("resultadoErroTexto");

    // Regra de reprovação: qualquer pergunta marcada como disqualificante
    // ("data-disqualifica=sim") respondida com "Sim" reprova a visita.
    // Quando integrar com o backend, essa checagem deve virar uma resposta
    // vinda de POST /triagens (o servidor decide, o front só exibe o resultado).
    var perguntasReprovadas = [];

    todasPerguntas.forEach(function (pergunta) {
        var disqualifica = pergunta.dataset.disqualifica === "sim";
        var resposta = pergunta.dataset.resposta;

        if (disqualifica && resposta === "sim") {
            perguntasReprovadas.push(pergunta.querySelector(".pergunta-texto").textContent);
        }
    });

    if (perguntasReprovadas.length > 0) {
        resultadoErroTexto.textContent =
            "🚫 Você está impossibilitado de realizar a visita no momento, devido a " +
            perguntasReprovadas.length + " critério(s) de risco identificado(s) no questionário. " +
            "Procure a equipe de enfermagem para mais orientações.";

        resultadoErro.classList.remove("escondido");
        resultadoSucesso.classList.add("escondido");
        botaoEnviar.disabled = true;
        botaoEnviar.textContent = "Triagem reprovada";
        return;
    }

    resultadoSucesso.classList.remove("escondido");
    resultadoErro.classList.add("escondido");
    botaoEnviar.disabled = true;
    botaoEnviar.textContent = "Triagem aprovada ✓";

    // TODO: integrar com o backend real, por exemplo:
    // POST /triagens { id_visitante, respostas: [...], declaracao_aceita: true }
    // e só redirecionar depois que a resposta confirmar aprovação.
    setTimeout(function () {
        window.location.href = "qrcode.html";
    }, 1800);
}

document.addEventListener("DOMContentLoaded", function () {
    inicializarTriagem();
});