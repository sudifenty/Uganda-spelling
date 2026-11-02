-- SmartPLE: clean duplicate profile rows for the same phone (run in Supabase SQL editor)
-- Example case: 4 rows for one student (0756346788 / +256756346788 / 256756346788 / dup)

-- 1) Delete duplicates FIRST: keep the best row per normalized phone
--    (is_paid TRUE wins, then the newest paid_until)
WITH ranked AS (
  SELECT ctid,
         row_number() OVER (
           PARTITION BY regexp_replace(phone, '\D', '', 'g')
           ORDER BY is_paid DESC, paid_until DESC NULLS LAST) AS rn
  FROM smartple_profiles
)
DELETE FROM smartple_profiles
WHERE ctid IN (SELECT ctid FROM ranked WHERE rn > 1);

-- 2) THEN normalize every remaining phone to one format: 07XXXXXXXX
UPDATE smartple_profiles
SET phone = '0' || right(regexp_replace(phone, '\D', '', 'g'), 9)
WHERE regexp_replace(phone, '\D', '', 'g') ~ '^(256)?7[0-9]{8}$';

-- 3) Optional: link the existing student's paid row to their email login,
--    so the app finds it by user_id immediately (table needs a user_id column):
-- UPDATE smartple_profiles
-- SET user_id = (SELECT id FROM auth.users WHERE email = 'sudaissenyonga44@gmail.com')
-- WHERE phone = '0756346788';

-- Verify:
-- SELECT phone, is_paid, paid_until FROM smartple_profiles ORDER BY phone;
