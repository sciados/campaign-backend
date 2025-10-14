-- Check user tier for user_id: 2c3d7631-3d6f-4f3a-bc49-d0ad1e283e0e

SELECT
    u.id as user_id,
    u.email,
    u.company_id,
    c.name as company_name,
    c.subscription_tier,
    u.created_at
FROM users u
LEFT JOIN companies c ON u.company_id = c.id
WHERE u.id = '2c3d7631-3d6f-4f3a-bc49-d0ad1e283e0e';

-- If the tier is not ENTERPRISE, run this update:
-- UPDATE companies
-- SET subscription_tier = 'ENTERPRISE'
-- WHERE id = (
--     SELECT company_id
--     FROM users
--     WHERE id = '2c3d7631-3d6f-4f3a-bc49-d0ad1e283e0e'
-- );
