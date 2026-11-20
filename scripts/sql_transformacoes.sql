SELECT
    COUNT(*) AS total_registros,
    MIN("DT_INTER") AS primeira_internacao,
    MAX("DT_INTER") AS ultima_internacao,
    ROUND(SUM("VAL_TOT")::NUMERIC, 2) AS valor_total
FROM public.internacoes;