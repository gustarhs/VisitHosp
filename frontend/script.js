function maskTel1() {
    var valor = document.getElementById("input1").value
    var letraRegex = /[a-zA-Z]/;
    valor = valor.slice(0, 3)

    if (valor[0] != undefined) {
        if (!letraRegex.test(valor[0])) {
            valor = valor.slice(1);
        }
    }

    var numeroRegex = /[0-9]/;

    if (valor[1] != undefined) {
        if (!numeroRegex.test(valor[1])) {
            valor = valor.slice(0, 1) + valor.slice(2)
        }
    }

    if (valor[2] != undefined) {
        if (!letraRegex.test(valor[2])) {
            valor = valor.slice(0, 2)
        }
    }

    

    document.getElementById("input1").value = valor.toUpperCase();

    if(valor.length===3){
        document.getElementById("input2").focus()
    }
}

function maskTel2() {
    var valor = document.getElementById("input2").value
    var letraRegex = /[a-zA-Z]/
    var numeroRegex = /[0-9]/;
    valor = valor.slice(0, 3)

    if (valor[0] != undefined) {
        if (!numeroRegex.test(valor[0])) {
            valor = valor.slice(1);
        }
    }



    if (valor[1] != undefined) {
        if (!letraRegex.test(valor[1])) {
            valor = valor.slice(0, 1) + valor.slice(2)
        }
    }

    if (valor[2] != undefined) {
        if (!numeroRegex.test(valor[2])) {
            valor = valor.slice(0, 2)
        }
    }

    document.getElementById("input2").value = valor.toUpperCase();

    if(valor.length===3){
        document.getElementById("input3").focus()
    }
}

function maskTel3() {
    var valor = document.getElementById("input3").value
    var letraRegex = /[a-zA-Z]/
    var numeroRegex = /[0-9]/;
    valor = valor.slice(0, 3)

    if (valor[0] != undefined) {
        if (!numeroRegex.test(valor[0])) {
            valor = valor.slice(1);
        }
    }



    if (valor[1] != undefined) {
        if (!letraRegex.test(valor[1])) {
            valor = valor.slice(0, 1) + valor.slice(2)
        }
    }

    if (valor[2] != undefined) {
        if (!letraRegex.test(valor[2])) {
            valor = valor.slice(0, 2)
        }
    }

    document.getElementById("input3").value = valor.toUpperCase();

    if(valor.length===3){
        document.getElementById("button").focus()
    }
}

var tokenCorreto = "A3F7K29MX";

function validarToken() {
    var t1 = document.getElementById("input1").value;
    var t2 = document.getElementById("input2").value;
    var t3 = document.getElementById("input3").value;

    var tokenDigitado = t1 + t2 + t3;

    if (tokenDigitado === tokenCorreto) {
        window.location.href = "inicial.html";
    } else {
        alert("Token inválido. Verifique o código e tente novamente.");
    }
}

function confirmarAgendamento(){
    window.location.href = "token.html"
} 