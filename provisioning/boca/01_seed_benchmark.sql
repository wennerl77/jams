-- =============================================================================
-- BOCA Online Contest Administrator - Benchmark Seed Script (PostgreSQL)
-- Generates initial Contest, Site, Problem, Languages, and 100 Competitor Teams
-- =============================================================================

BEGIN;

-- 1. Insert Contest
INSERT INTO contesttable (
    contestnumber, contestname, conteststartdate, contestduration, 
    contestlocalsite, contestpenalty, contestmaxfilesize, contestactive,
    contestmainsite, contestkeys, contestunlockkey, contestmainsiteurl
) VALUES (
    1, 'Benchmark ICPC 2026', EXTRACT(EPOCH FROM TIMESTAMP '2026-09-12 09:00:00')::integer, 
    18000, 1, 1200, 100000, 't',
    1, 'key', 'unlock', 'http://192.168.56.11:8000'
) ON CONFLICT (contestnumber) DO UPDATE SET
    contestname = EXCLUDED.contestname,
    contestduration = EXCLUDED.contestduration,
    contestpenalty = EXCLUDED.contestpenalty,
    contestactive = EXCLUDED.contestactive;

-- 2. Insert Main Site (Site 1)
INSERT INTO sitetable (
    contestnumber, sitenumber, siteip, sitename, siteactive, sitepermitlogins
) VALUES (
    1, 1, '192.168.56.11', 'Site Principal', 't', 't'
) ON CONFLICT (contestnumber, sitenumber) DO NOTHING;

-- 3. Insert Problem A
INSERT INTO problemtable (
    contestnumber, problemnumber, problemname, problemfullname, problembasefilename
) VALUES (
    1, 1, 'A', 'Soma Simples', 'soma'
) ON CONFLICT (contestnumber, problemnumber) DO UPDATE SET
    problemname = EXCLUDED.problemname;

-- 4. Insert Languages (C++17 and Python 3)
INSERT INTO langtable (contestnumber, langnumber, langname, langextension)
VALUES 
    (1, 1, 'C++17 (g++)', 'cpp'),
    (1, 2, 'Python 3', 'py')
ON CONFLICT (contestnumber, langnumber) DO UPDATE SET
    langname = EXCLUDED.langname,
    langextension = EXCLUDED.langextension;

-- 5. Insert 100 Competitor Teams (team1 to team100)
DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..100 LOOP
        INSERT INTO usertable (
            contestnumber, usersitenumber, usernumber, username, 
            userfullname, userpassword, usertype, userenabled
        ) VALUES (
            1, 1, i, 'team' || i, 
            'Team ' || i, 'team123_benchmark', 'team', 't'
        ) ON CONFLICT (contestnumber, usersitenumber, usernumber) DO UPDATE SET
            username = EXCLUDED.username,
            userpassword = EXCLUDED.userpassword;
    END LOOP;
END $$;

COMMIT;
