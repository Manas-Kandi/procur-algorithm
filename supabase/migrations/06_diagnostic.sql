-- Check for duplicate users
SELECT email, COUNT(*) as count
FROM user_accounts
GROUP BY email
HAVING COUNT(*) > 1;

-- Check all users
SELECT id, email, username, organization_id, deleted_at
FROM user_accounts
ORDER BY email;

-- Check if buyer exists
SELECT id, email FROM user_accounts WHERE email = 'buyer@demo-org.com';

-- Check if acme admin exists
SELECT id, email FROM user_accounts WHERE email = 'admin@acme-corp.com';
