-- 查询 specialties 表中的所有产品数据
SELECT 
    specialty_id AS '产品ID',
    name AS '产品名称',
    category AS '产品类别',
    price AS '价格',
    status AS '状态',
    create_time AS '创建时间',
    publisher_id AS '发布者ID'
FROM specialties
ORDER BY create_time DESC;

-- 查询产品详细信息（包括发布者和产地信息）
SELECT 
    s.specialty_id AS '产品ID',
    s.name AS '产品名称',
    s.category AS '产品类别',
    s.price AS '价格',
    s.status AS '状态',
    s.create_time AS '创建时间',
    s.sale_start_time AS '销售开始时间',
    s.sale_end_time AS '销售结束时间',
    u.username AS '发布者',
    o.origin_name AS '产地名称',
    o.province AS '省份',
    o.city AS '城市',
    o.district AS '区县'
FROM specialties s
LEFT JOIN users u ON s.publisher_id = u.user_id
LEFT JOIN origins o ON s.origin_id = o.origin_id
ORDER BY s.create_time DESC;

-- 查询产品总数
SELECT COUNT(*) AS '产品总数' FROM specialties;

-- 查询上架状态的产品数量
SELECT COUNT(*) AS '上架产品数量' FROM specialties WHERE status = '上架';

-- 查询最近发布的5个产品
SELECT 
    specialty_id AS '产品ID',
    name AS '产品名称',
    category AS '产品类别',
    price AS '价格',
    status AS '状态',
    create_time AS '创建时间'
FROM specialties
ORDER BY create_time DESC
LIMIT 5;