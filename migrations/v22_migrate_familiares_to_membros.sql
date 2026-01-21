-- Migration: Consolidate familiares table into membros_familia
-- Date: 2026-01-21
-- Purpose: Eliminate duplicate tables and standardize family member management

-- Step 1: Add email column to membros_familia if not exists
ALTER TABLE membros_familia 
ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Step 2: Migrate data from familiares to membros_familia
-- Note: familiares table doesn't have idoso_id, so we can't migrate directly
-- This migration will only work if there's a way to link familiares to idosos
-- For now, we'll create a backup and mark for manual review

-- Create backup of familiares table
CREATE TABLE IF NOT EXISTS familiares_backup_20260121 AS 
SELECT * FROM familiares;

-- Step 3: Add migration status column to track which records were migrated
ALTER TABLE familiares 
ADD COLUMN IF NOT EXISTS migrated_to_membros BOOLEAN DEFAULT FALSE;

-- Step 4: Log migration attempt
INSERT INTO audit_logs (usuario_email, acao, recurso, detalhes, criado_em)
VALUES (
    'system',
    'MIGRATION_STARTED',
    'familiares_to_membros_familia',
    'Started migration of familiares table to membros_familia. Manual review required due to missing idoso_id foreign key.',
    NOW()
);

-- Step 5: Create view for unmigrated familiares
CREATE OR REPLACE VIEW familiares_pending_migration AS
SELECT 
    f.id,
    f.nome,
    f.parentesco,
    f.telefone,
    f.email,
    f.eh_responsavel,
    f.criado_em,
    'PENDING: No idoso_id - requires manual assignment' as migration_status
FROM familiares f
WHERE f.migrated_to_membros = FALSE OR f.migrated_to_membros IS NULL;

-- Step 6: Add deprecation notice
COMMENT ON TABLE familiares IS 'DEPRECATED: Use membros_familia instead. This table is scheduled for removal after data migration is complete.';

-- Migration Notes:
-- ================
-- 1. The familiares table lacks idoso_id foreign key
-- 2. Manual intervention required to assign each familiar to an idoso
-- 3. After manual assignment, update migrated_to_membros = TRUE
-- 4. Once all records are migrated, drop familiares table
-- 5. Update scheduler_api.py to use membros_familia endpoints

-- Example manual migration query (run for each familiar):
-- INSERT INTO membros_familia (idoso_id, nome, parentesco, telefone, email, is_responsavel)
-- SELECT 
--     <IDOSO_ID_HERE>,  -- Must be manually determined
--     nome,
--     parentesco,
--     telefone,
--     email,
--     eh_responsavel
-- FROM familiares
-- WHERE id = <FAMILIAR_ID_HERE>;
-- 
-- UPDATE familiares SET migrated_to_membros = TRUE WHERE id = <FAMILIAR_ID_HERE>;
