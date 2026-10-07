-- =============================================================================
-- Helium (MicroHelium) - Benchmark Seed Script (MySQL)
-- Generates initial Contest, Site, Problem, Languages, and 100 Competitors
-- =============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 0. Clean previous runs
DELETE FROM runs;

-- 1. Insert Contest
INSERT INTO contests (
    id, name, start_time, duration, penalty, max_file_size, is_active
) VALUES (
    1, 'Benchmark ICPC 2026', NOW(), 864000, 20, 100, 1
) ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    start_time = VALUES(start_time),
    duration = VALUES(duration),
    penalty = VALUES(penalty),
    is_active = VALUES(is_active);

-- 2. Insert Site
INSERT INTO sites (
    id, contest_id, name, is_active, permit_logins
) VALUES (
    1, 1, 'Site Principal', 1, 1
) ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    is_active = VALUES(is_active),
    permit_logins = VALUES(permit_logins);

-- 3. Insert Problem A
INSERT INTO problems (
    id, contest_id, short_name, name, basename, time_limit, memory_limit, auto_judge
) VALUES (
    1, 1, 'A', 'Soma Simples', 'soma', 1, 256, 1
) ON DUPLICATE KEY UPDATE
    short_name = VALUES(short_name),
    name = VALUES(name),
    basename = VALUES(basename),
    time_limit = VALUES(time_limit),
    memory_limit = VALUES(memory_limit);

-- 4. Insert Languages (C++17 and Python 3)
DELETE FROM languages WHERE contest_id = 1;
INSERT INTO languages (id, contest_id, name, extension, compile_command, run_command, is_active)
VALUES 
    (1, 1, 'C++17 (g++)', 'cpp', 'g++ -O2 -std=c++17 -o {output} {source}', './{executable}', 1),
    (2, 1, 'Python 3', 'py', 'python3 -m py_compile {source}', 'python3 {source}', 1);

-- 5. Insert 100 Competitor Users (team1 to team100)
-- Hash '$2y$10$9aOv4hJcDRSfUwOTzYuNneVjg50Vjx6uJPLsHTlAfkqcYwBzAoYPy' corresponds to 'team123_benchmark'
DROP PROCEDURE IF EXISTS seed_helium_users;

DELIMITER //
CREATE PROCEDURE seed_helium_users()
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= 100 DO
        INSERT INTO users (contest_id, site_id, fullname, username, password, user_type, is_enabled)
        VALUES (
            1,
            1,
            CONCAT('Team ', i), 
            CONCAT('team', i), 
            '$2y$10$9aOv4hJcDRSfUwOTzYuNneVjg50Vjx6uJPLsHTlAfkqcYwBzAoYPy', 
            'team', 
            1
        ) ON DUPLICATE KEY UPDATE
            fullname = VALUES(fullname),
            password = VALUES(password),
            user_type = VALUES(user_type),
            is_enabled = VALUES(is_enabled),
            contest_id = VALUES(contest_id),
            site_id = VALUES(site_id);

        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL seed_helium_users();
DROP PROCEDURE IF EXISTS seed_helium_users;

SET FOREIGN_KEY_CHECKS = 1;
