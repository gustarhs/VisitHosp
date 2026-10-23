 -- ============================================================
-- Stored procedures para o VisitHosp
-- Rode este arquivo DEPOIS de create_database.sql, no mesmo banco.
-- Ex.: mysql -u root -p db_visithosp < create_procedures.sql
--
-- ATENÇÃO: 2 procedures (sinalizadas abaixo) usam PLACEHOLDERS
-- porque o schema atual não tem tabelas para "responsável do
-- paciente" nem "regras de acesso por papel". Elas destravam o
-- código, mas a lógica de negócio real precisa ser definida.
-- ============================================================

USE db_visithosp;

-- ------------------------------------------------------------
-- 1. sp_cancelar_acessos_por_alta
--    Encerra a internação ativa do leito e cancela as visitas
--    futuras ligadas a ela.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_cancelar_acessos_por_alta;

DELIMITER $$
CREATE PROCEDURE sp_cancelar_acessos_por_alta(
    IN p_id_leito INT
)
BEGIN
    UPDATE internacao
    SET status = FALSE
    WHERE id_leito = p_id_leito AND status = TRUE;

    UPDATE visita v
    JOIN internacao i ON v.id_internacao = i.id
    SET v.status = FALSE
    WHERE i.id_leito = p_id_leito
      AND v.status = TRUE
      AND v.data_hora > NOW();

    SELECT
        p_id_leito AS id_leito,
        ROW_COUNT() AS visitas_canceladas;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 2. sp_validar_token_acesso
--    Confere se um token de acesso é válido (internação ativa e
--    dentro do período de internação).
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_validar_token_acesso;

DELIMITER $$
CREATE PROCEDURE sp_validar_token_acesso(
    IN p_codigo_token VARCHAR(20)
)
BEGIN
    SELECT
        i.id,
        i.token_acesso,
        i.status,
        i.data_entrada,
        i.data_saida,
        p.nome AS paciente_nome,
        l.numero AS leito_numero,
        (
            i.status = TRUE
            AND NOW() BETWEEN i.data_entrada AND i.data_saida
        ) AS token_valido
    FROM internacao i
    JOIN paciente p ON p.id = i.id_paciente
    JOIN leito l    ON l.id = i.id_leito
    WHERE i.token_acesso = p_codigo_token;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 3. sp_historico_visitas_paciente
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_historico_visitas_paciente;

DELIMITER $$
CREATE PROCEDURE sp_historico_visitas_paciente(
    IN p_id_paciente INT,
    IN p_data_inicio DATETIME,
    IN p_data_fim DATETIME
)
BEGIN
    SELECT
        v.id,
        v.data_hora,
        v.status,
        v.qr_code,
        vi.nome AS visitante_nome,
        vi.tipo AS visitante_tipo
    FROM visita v
    JOIN internacao i ON v.id_internacao = i.id
    JOIN visitante vi ON vi.id = v.id_visitante
    WHERE i.id_paciente = p_id_paciente
      AND (p_data_inicio IS NULL OR v.data_hora >= p_data_inicio)
      AND (p_data_fim    IS NULL OR v.data_hora <= p_data_fim)
    ORDER BY v.data_hora DESC;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 4. sp_relatorio_auditoria_fluxo
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_relatorio_auditoria_fluxo;

DELIMITER $$
CREATE PROCEDURE sp_relatorio_auditoria_fluxo(
    IN p_id_leito INT,
    IN p_periodo_inicio DATETIME,
    IN p_periodo_fim DATETIME
)
BEGIN
    SELECT
        v.id AS id_visita,
        v.data_hora,
        v.status,
        l.numero AS leito_numero,
        l.ala,
        p.nome AS paciente_nome,
        vi.nome AS visitante_nome,
        vi.cpf  AS visitante_cpf
    FROM visita v
    JOIN internacao i ON v.id_internacao = i.id
    JOIN leito l      ON l.id = i.id_leito
    JOIN paciente p   ON p.id = i.id_paciente
    JOIN visitante vi ON vi.id = v.id_visitante
    WHERE v.data_hora BETWEEN p_periodo_inicio AND p_periodo_fim
      AND (p_id_leito IS NULL OR l.id = p_id_leito)
    ORDER BY v.data_hora ASC;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 5. sp_relatorio_gerencial_visitas
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_relatorio_gerencial_visitas;

DELIMITER $$
CREATE PROCEDURE sp_relatorio_gerencial_visitas(
    IN p_periodo_inicio DATETIME,
    IN p_periodo_fim DATETIME,
    IN p_id_paciente INT
)
BEGIN
    SELECT
        DATE(v.data_hora) AS dia,
        COUNT(*) AS total_visitas,
        SUM(v.status = TRUE)  AS visitas_realizadas,
        SUM(v.status = FALSE) AS visitas_canceladas
    FROM visita v
    JOIN internacao i ON v.id_internacao = i.id
    WHERE v.data_hora BETWEEN p_periodo_inicio AND p_periodo_fim
      AND (p_id_paciente IS NULL OR i.id_paciente = p_id_paciente)
    GROUP BY DATE(v.data_hora)
    ORDER BY dia ASC;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 6. sp_verificar_slot_extensao
--    Assume janela mínima de 30 min entre visitas no mesmo leito.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_verificar_slot_extensao;

DELIMITER $$
CREATE PROCEDURE sp_verificar_slot_extensao(
    IN p_id_leito INT,
    IN p_horario_agendado DATETIME
)
BEGIN
    SELECT
        p_id_leito AS id_leito,
        p_horario_agendado AS horario_agendado,
        COUNT(*) AS conflitos,
        (COUNT(*) = 0) AS disponivel
    FROM visita v
    JOIN internacao i ON v.id_internacao = i.id
    WHERE i.id_leito = p_id_leito
      AND v.status = TRUE
      AND ABS(TIMESTAMPDIFF(MINUTE, v.data_hora, p_horario_agendado)) < 30;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 7. sp_validar_janela_qrcode
--    Assume janela de validade: 15 min antes a 30 min depois
--    do horário agendado da visita.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_validar_janela_qrcode;

DELIMITER $$
CREATE PROCEDURE sp_validar_janela_qrcode(
    IN p_id_visita INT
)
BEGIN
    SELECT
        v.id,
        v.qr_code,
        v.data_hora,
        v.status,
        (
            v.status = TRUE
            AND NOW() BETWEEN (v.data_hora - INTERVAL 15 MINUTE) AND (v.data_hora + INTERVAL 30 MINUTE)
        ) AS dentro_da_janela
    FROM visita v
    WHERE v.id = p_id_visita;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 8. sp_validar_entrada_totem
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_validar_entrada_totem;

DELIMITER $$
CREATE PROCEDURE sp_validar_entrada_totem(
    IN p_qr_code VARCHAR(100)
)
BEGIN
    SELECT
        v.id,
        v.qr_code,
        v.data_hora,
        v.status,
        vi.nome AS visitante_nome,
        vi.cpf  AS visitante_cpf,
        (
            v.status = TRUE
            AND NOW() BETWEEN (v.data_hora - INTERVAL 15 MINUTE) AND (v.data_hora + INTERVAL 30 MINUTE)
        ) AS entrada_liberada
    FROM visita v
    JOIN visitante vi ON vi.id = v.id_visitante
    WHERE v.qr_code = p_qr_code;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 9. sp_verificar_disponibilidade_slots
--    Assume slots de 30 min, começando no horario_visita
--    cadastrado no hospital, cobrindo uma janela de 2h.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_verificar_disponibilidade_slots;

DELIMITER $$
CREATE PROCEDURE sp_verificar_disponibilidade_slots(
    IN p_id_leito INT,
    IN p_data_visita DATE
)
BEGIN
    DECLARE v_hora_base TIME;

    SELECT TIME(h.horario_visita) INTO v_hora_base
    FROM hospital h
    LIMIT 1;

    IF v_hora_base IS NULL THEN
        SET v_hora_base = '14:00:00';
    END IF;

    SELECT
        TIMESTAMP(p_data_visita, v_hora_base) + INTERVAL (n.numero * 30) MINUTE AS horario_slot,
        NOT EXISTS (
            SELECT 1
            FROM visita v
            JOIN internacao i ON v.id_internacao = i.id
            WHERE i.id_leito = p_id_leito
              AND v.status = TRUE
              AND v.data_hora = TIMESTAMP(p_data_visita, v_hora_base) + INTERVAL (n.numero * 30) MINUTE
        ) AS disponivel
    FROM (
        SELECT 0 AS numero UNION SELECT 1 UNION SELECT 2 UNION SELECT 3
    ) AS n;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 10. sp_verificar_bloqueio_status_paciente
--     Assume paciente.status = FALSE como "bloqueado/inativo".
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_verificar_bloqueio_status_paciente;

DELIMITER $$
CREATE PROCEDURE sp_verificar_bloqueio_status_paciente(
    IN p_id_paciente INT
)
BEGIN
    SELECT
        p.id,
        p.nome,
        p.status AS ativo,
        (p.status = FALSE) AS bloqueado,
        EXISTS (
            SELECT 1 FROM internacao i
            WHERE i.id_paciente = p.id AND i.status = TRUE
        ) AS possui_internacao_ativa
    FROM paciente p
    WHERE p.id = p_id_paciente;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 11. sp_obter_responsavel_autorizado   [PLACEHOLDER]
--     O schema não tem tabela "responsavel" com prioridade
--     ADM1/ADM2. Esta procedure só retorna os dados do próprio
--     paciente para não quebrar a chamada. Para implementar de
--     verdade, crie algo como:
--       CREATE TABLE responsavel (
--           id INT PRIMARY KEY AUTO_INCREMENT,
--           id_paciente INT NOT NULL,
--           nome VARCHAR(150) NOT NULL,
--           contato VARCHAR(100) NOT NULL,
--           prioridade ENUM('ADM1','ADM2') NOT NULL,
--           FOREIGN KEY (id_paciente) REFERENCES paciente(id)
--       );
--     e então buscar o de prioridade ADM1; se não existir, cair
--     para ADM2.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_obter_responsavel_autorizado;

DELIMITER $$
CREATE PROCEDURE sp_obter_responsavel_autorizado(
    IN p_id_paciente INT
)
BEGIN
    SELECT
        p.id,
        p.nome,
        p.cpf,
        p.tipo,
        'PLACEHOLDER: tabela de responsaveis nao existe no schema atual' AS aviso
    FROM paciente p
    WHERE p.id = p_id_paciente;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 12. sp_obter_regras_acesso_por_papel   [PLACEHOLDER]
--     O schema não tem tabela de regras de acesso. Regras
--     abaixo são fixas (hardcoded) por visitante.tipo, só para
--     destravar o desenvolvimento. Troque por uma tabela
--     "regra_acesso" quando as regras reais forem definidas.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_obter_regras_acesso_por_papel;

DELIMITER $$
CREATE PROCEDURE sp_obter_regras_acesso_por_papel(
    IN p_id_visitante INT
)
BEGIN
    SELECT
        v.id,
        v.nome,
        v.tipo,
        CASE v.tipo
            WHEN 'familiar'     THEN 60
            WHEN 'responsavel'  THEN 60
            WHEN 'amigo'        THEN 30
            WHEN 'profissional' THEN 45
            ELSE 15
        END AS duracao_max_minutos,
        CASE v.tipo
            WHEN 'profissional' THEN TRUE
            ELSE FALSE
        END AS requer_autorizacao_extra
    FROM visitante v
    WHERE v.id = p_id_visitante;
END$$
DELIMITER ;

-- ------------------------------------------------------------
-- 13. sp_listar_cadastros_pendentes
--     Assume visitante.status = FALSE como "pendente de aprovação".
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_listar_cadastros_pendentes;

DELIMITER $$
CREATE PROCEDURE sp_listar_cadastros_pendentes()
BEGIN
    SELECT id, nome, tipo, cpf, data_nascimento, termo_consentimento, status
    FROM visitante
    WHERE status = FALSE
    ORDER BY id ASC;
END$$
DELIMITER ;