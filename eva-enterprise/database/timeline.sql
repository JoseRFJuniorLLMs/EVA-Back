
-- Criar a tabela timeline se não existir (para suportar persistência do que era placeholder)
CREATE TABLE IF NOT EXISTS timeline (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL, -- 'ligacao', 'medicamento', 'alerta', 'equipe'
    subtipo VARCHAR(50),      -- 'emocional', 'critico', 'sucesso', 'normal'
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Script de Povoamento: 3 itens por idoso
INSERT INTO timeline (idoso_id, tipo, subtipo, titulo, descricao, data)
SELECT 
    i.id,
    t.tipo,
    t.subtipo,
    t.titulo,
    t.descricao,
    CURRENT_TIMESTAMP - (random() * interval '7 days') as data
FROM idosos i
CROSS JOIN (
    VALUES 
        ('ligacao', 'sucesso', 'Ligação de Rotina', 'Conversa matinal realizada com sucesso. O idoso relatou estar se sentindo disposto.'),
        ('medicamento', 'sucesso', 'Medicação Confirmada', 'A medicação de pressão das 08:00 foi confirmada pelo idoso.'),
        ('alerta', 'normal', 'Lembrete de Hidratação', 'A EVA sugeriu que o idoso bebesse um copo de água durante a tarde.')
) AS t(tipo, subtipo, titulo, descricao)
WHERE i.ativo = true;
