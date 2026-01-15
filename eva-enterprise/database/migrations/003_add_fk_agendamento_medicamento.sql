-- Adiciona coluna medicamento_id como Foreign Key na tabela agendamentos
ALTER TABLE agendamentos ADD COLUMN IF NOT EXISTS medicamento_id INTEGER;

-- Cria a constraint de chave estrangeira
ALTER TABLE agendamentos 
ADD CONSTRAINT fk_agendamento_medicamento 
FOREIGN KEY (medicamento_id) 
REFERENCES medicamentos(id) 
ON DELETE SET NULL;

-- Comentário para registro
COMMENT ON COLUMN agendamentos.medicamento_id IS 'Link Vital (Diagrama): Referência direta ao medicamento prescrito';
