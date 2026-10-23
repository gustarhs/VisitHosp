<h1 align="center">🏥 VisitHosp</h1>

<p align="center">
  <em>Transformando a incerteza em cuidado e previsibilidade.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-em%20desenvolvimento-yellow" alt="Status">
  <img src="https://img.shields.io/badge/Python-Flask-000000?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker">
</p>

---

## 📑 Sumário

- [Descrição do Projeto](#-descrição-do-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [Como Executar](#-como-executar)
- [Equipe](#-equipe)

---

## 📝 Descrição do Projeto

O **VisitHosp** é um sistema inteligente de gestão de fluxos para hospitais e seus visitantes.

| | |
|---|---|
| 🎯 **Objetivo** | Sincronizar, em tempo real, a agenda de visitas com o status clínico do paciente e a lotação real da ala. |
| ⚠️ **Problema** | Resolve a "viagem perdida" (visitas em horários de exames ou banho), reduz riscos de infecção (por meio de triagem digital), evita falhas de segurança e protege dados sensíveis, em conformidade com a **LGPD**. |
| 👥 **Público-alvo** | Hospitais de média e alta complexidade (B2B) e familiares que buscam uma jornada de visitação segura e previsível. |

---

## ✨ Funcionalidades

### 🛏️ Pacientes, internações e leitos
1. **Cadastro de pacientes** — registro e gerenciamento dos dados dos pacientes internados.
2. **Cadastro de internações** — registro das internações dos pacientes no hospital.
3. **Controle de leitos** — cadastro e acompanhamento dos leitos disponíveis e ocupados.
4. **Controle de ocupação** — análise da ocupação dos leitos.
5. **Atualização do status clínico em tempo real** — a equipe de enfermagem informa quando o paciente está em exame, banho ou procedimento, bloqueando visitas nesses momentos.

### 📅 Visitas
6. **Triagem de visitantes** — avaliação das condições do visitante antes da visita.
7. **Cadastro e controle de visitas** — registro das informações relacionadas às visitas aos pacientes.
8. **Análise de disponibilidade por horário** — identificação dos horários disponíveis para visitas.
9. **Controle das regras de visita** — verificação das condições que permitem ou impedem uma visita.
10. **Histórico de visitas** — consulta das visitas realizadas por paciente e por visitante.
11. **Notificações ao visitante** — aviso automático sobre confirmação, cancelamento ou mudança de horário da visita.

### 🔳 Acesso e QR Code
12. **Geração de QR Code** — QR Code vinculado à visita para identificação do acesso.
13. **Compartilhamento e impressão do QR Code** — o QR Code gerado pode ser compartilhado ou impresso.
14. **Validação do QR Code na entrada** — leitura do código na recepção para liberar ou negar o acesso.
15. **Rota até o hospital** — integração com a Google Maps API para orientar o visitante até a unidade.

### 🔐 Segurança e conformidade (LGPD)
16. **Login com perfis de acesso** — permissões distintas para administrador, recepção, enfermagem e visitante.
17. **Criptografia de dados sensíveis** — proteção das informações pessoais e clínicas armazenadas.
18. **Registro de auditoria** — log de quem acessou ou alterou dados, apoiando a conformidade com a LGPD.

### 📊 Gestão e automação
19. **Painel de indicadores** — dashboard com taxa de ocupação, volume de visitas e horários de pico.
20. **Automações com N8N** — fluxos automáticos para envio de notificações e integração entre os módulos do sistema.

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologias |
|---|---|
| **Frontend** | HTML, CSS, JavaScript |
| **Backend** | Python, Flask |
| **Banco de Dados** | MySQL (modelagem no MySQL Workbench) |
| **Infraestrutura** | Docker |
| **Integrações** | N8N, Google Maps API |
| **Segurança** | Bibliotecas de criptografia |
| **Design e Documentação** | Figma, Draw.io |

---

## 🚀 Como Executar

> 🚧 **Em construção.** As instruções completas de instalação e execução serão adicionadas em breve.

---

## 👥 Equipe

| Integrante | Função / Responsabilidade | Contato |
|---|---|---|
| **Ana Clara Matias** | Desenvolvedora Backend / DevOps | [@aclarette](https://github.com/aclarette) |
| **Clara Lima** | Analista de Banco de Dados / QA | [@claraliima](https://github.com/claraliima) |
| **Fernanda Pena Barbosa** | Scrum Master / Documentação | Fernanda Barbosa |
| **Gustavo Soares** | Desenvolvedor Frontend / UI Designer | [@gustarhs](https://github.com/gustarhs) |

---

<p align="center">Feito com 💙 pela equipe VisitHosp</p>
