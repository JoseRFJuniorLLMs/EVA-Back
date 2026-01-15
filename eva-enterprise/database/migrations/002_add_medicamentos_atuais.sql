-- Adiciona coluna faltante na tabela idosos
ALTER TABLE idosos ADD COLUMN IF NOT EXISTS medicamentos_atuais JSONB DEFAULT '[]'::jsonb;

-- Comentário para registro
COMMENT ON COLUMN idosos.medicamentos_atuais IS 'Lista JSON dos medicamentos atuais consumidos pelo idoso';
