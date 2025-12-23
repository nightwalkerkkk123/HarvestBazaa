-- 手动插入违规记录，模拟管理员冻结多次违规用户的功能
-- 注意：请将user_id和specialty_id替换为实际存在的ID值

-- 插入第一条违规记录（警告）
INSERT INTO violation_records (user_id, specialty_id, violation_type, violation_time, process_result)
VALUES (1, 10, '虚假宣传', NOW(), '警告');

-- 插入第二条违规记录（严重警告）
INSERT INTO violation_records (user_id, specialty_id, violation_type, violation_time, process_result)
VALUES (1, 15, '销售过期产品', NOW(), '严重警告');

-- 插入第三条违规记录（冻结账号）
INSERT INTO violation_records (user_id, specialty_id, violation_type, violation_time, process_result)
VALUES (1, 20, '多次投诉未处理', NOW(), '冻结账号');

-- 更新用户状态为冻结
UPDATE users SET status = '冻结' WHERE user_id = 1;

-- 查询该用户的所有违规记录
SELECT * FROM violation_records WHERE user_id = 1 ORDER BY violation_time DESC;

-- 查询该用户的当前状态
SELECT username, role, status FROM users WHERE user_id = 1;