-- =====================================================================
-- SmartPLE PERMANENT payment fix — run ONCE, top to bottom, in the
-- Supabase SQL editor. Order is fixed vs. the draft:
--   * columns are added FIRST (the draft updated user_id before creating it)
--   * duplicates are deleted BEFORE normalizing (normalizing first would
--     crash on the UNIQUE(phone) constraint when two rows merge)
--   * dedupe uses ctid (always exists) instead of an id column
-- =====================================================================

-- 0) Make sure the needed columns exist (safe to re-run)
ALTER TABLE smartple_profiles ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE smartple_profiles ADD COLUMN IF NOT EXISTS is_paid BOOLEAN DEFAULT false;
ALTER TABLE smartple_profiles ADD COLUMN IF NOT EXISTS paid_until TIMESTAMPTZ;
ALTER TABLE smartple_profiles ADD COLUMN IF NOT EXISTS paid_at TIMESTAMPTZ;
ALTER TABLE smartple_profiles ADD COLUMN IF NOT EXISTS payment_phone TEXT;
ALTER TABLE smartple_profiles ADD COLUMN IF NOT EXISTS payment_txn TEXT;

-- 1) Canonical phone format function (one format forever: +2567XXXXXXXX)
CREATE OR REPLACE FUNCTION normalize_phone(p TEXT)
RETURNS TEXT AS $$
  SELECT
    CASE
      WHEN p LIKE '+256%' THEN p
      WHEN p LIKE '256%'  THEN '+' || p
      WHEN p LIKE '0%'    THEN '+256' || SUBSTRING(p FROM 2)
      ELSE '+256' || p
    END;
$$ LANGUAGE sql IMMUTABLE;

-- 2) Delete duplicates FIRST — keep the best row per normalized phone
--    (row with user_id wins, then paid, then newest paid_until)
WITH ranked AS (
  SELECT ctid,
         row_number() OVER (
           PARTITION BY normalize_phone(phone)
           ORDER BY (user_id IS NOT NULL) DESC, is_paid DESC, paid_until DESC NULLS LAST) AS rn
  FROM smartple_profiles
)
DELETE FROM smartple_profiles
WHERE ctid IN (SELECT ctid FROM ranked WHERE rn > 1);

-- 3) NOW normalize every phone to +256 format (no more collisions)
UPDATE smartple_profiles SET phone = normalize_phone(phone);

-- 4) Backfill user_id from auth.users where the signup phone matches
--    (works for phone signups; email-only accounts get linked by the app
--     itself now — it stamps user_id on signup / payment-form / profile save)
UPDATE smartple_profiles p
SET user_id = u.id
FROM auth.users u
WHERE p.user_id IS NULL
  AND u.phone IS NOT NULL
  AND normalize_phone(u.phone) = p.phone;

-- 5) One row per phone forever (skip if a constraint already exists)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'smartple_profiles_phone_unique') THEN
    ALTER TABLE smartple_profiles ADD CONSTRAINT smartple_profiles_phone_unique UNIQUE (phone);
  END IF;
END $$;

-- 6) One-command verification for ANY future payment:
CREATE OR REPLACE FUNCTION verify_student(p_phone TEXT)
RETURNS VOID AS $$
BEGIN
  UPDATE smartple_profiles
  SET is_paid = true,
      paid_until = NOW() + INTERVAL '30 days',
      paid_at = NOW()
  WHERE phone = normalize_phone(p_phone);
END;
$$ LANGUAGE plpgsql;

-- USAGE from now on, for every payment:
--   SELECT verify_student('0756346788');     -- 07… / 256… / +256… all work
--
-- Verify:
--   SELECT phone, user_id, is_paid, paid_until FROM smartple_profiles ORDER BY phone;
