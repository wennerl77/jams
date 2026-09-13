-- =============================================================================
-- Helium (MicroHelium) - Benchmark Seed Script (MySQL)
-- Generates initial Contest, Problem, Languages, 100 Competitors, and Pivot entries
-- =============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Insert Contest
INSERT INTO contests (
    id, title, start_at, duration_minutes, penalty_minutes, max_file_size_kb, is_active, status
) VALUES (
    1, 'Benchmark ICPC 2026', '2026-09-12 09:00:00', 300, 20, 100, 1, 'active'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    duration_minutes = VALUES(duration_minutes),
    penalty_minutes = VALUES(penalty_minutes),
    is_active = VALUES(is_active);

-- 2. Insert Problem A
INSERT INTO problems (
    id, contest_id, letter, title, time_limit_ms, memory_limit_mb, slug
) VALUES (
    1, 1, 'A', 'Soma Simples', 1000, 256, 'soma-simples'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    time_limit_ms = VALUES(time_limit_ms),
    memory_limit_mb = VALUES(memory_limit_mb);

-- 3. Insert Languages (C++17 and Python 3)
INSERT INTO languages (id, name, extension, compile_command)
VALUES 
    (1, 'C++17 (g++)', 'cpp', 'g++ -O2 -std=c++17'),
    (2, 'Python 3', 'py', 'python3')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    extension = VALUES(extension),
    compile_command = VALUES(compile_command);

-- 4. Insert 100 Competitor Users (team1 to team100) and Contest-User bindings
-- Hash '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi' corresponds to 'team123_benchmark'
DROP PROCEDURE IF EXISTS seed_helium_users;

DELIMITER //
CREATE PROCEDURE seed_helium_users()
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= 100 DO
        INSERT INTO users (id, name, username, password, role, is_active)
        VALUES (
            i, 
            CONCAT('Team ', i), 
            CONCAT('team', i), 
            '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 
            'competitor', 
            1
        ) ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            username = VALUES(username);

        INSERT INTO contest_user (contest_id, user_id)
        VALUES (1, i)
        ON DUPLICATE KEY UPDATE contest_id = VALUES(contest_id);

        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL seed_helium_users();
DROP PROCEDURE IF EXISTS seed_helium_users;

SET FOREIGN_KEY_CHECKS = 1;
