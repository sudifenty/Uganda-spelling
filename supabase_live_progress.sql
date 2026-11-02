-- ============================================================
-- SMART PLE · live topic progress for the owner
-- Run ONCE in the Supabase dashboard → SQL Editor → New query.
-- Safe to run again: every statement is "if not exists" / "drop then create".
-- ============================================================
--
-- Why this exists
-- ---------------
-- A learner finishing a topic now writes one row here the same second it
-- happens. The Owner screen (#admin → PIN) shows those rows on a live board
-- that refreshes itself every 8 seconds.
--
-- Nothing personal beyond the learner's own name, class and topic is stored.
-- No phone numbers, no payments, no answers.

create table if not exists public.smartple_topic_progress (
  id           bigserial primary key,
  user_id      uuid,
  learner      text,
  class_level  text,
  subject      text,
  topic_id     text,
  topic_title  text,
  kind         text,        -- 'read' | 'subtopic' | 'exam' | 'mid'
  sub_index    int,
  sub_title    text,
  subs_done    int,
  subs_total   int,
  pct          int,
  passed       boolean,
  score        int,
  created_at   timestamptz not null default now()
);

create index if not exists smartple_topic_progress_recent
  on public.smartple_topic_progress (created_at desc);

create index if not exists smartple_topic_progress_topic
  on public.smartple_topic_progress (topic_id, kind);

alter table public.smartple_topic_progress enable row level security;

-- 1. A learner may ADD their own progress rows.
drop policy if exists "topic progress insert" on public.smartple_topic_progress;
create policy "topic progress insert"
  on public.smartple_topic_progress
  for insert to anon, authenticated
  with check (true);

-- 2. The owner's board may READ the rows.
--    The Owner screen is behind the PIN, but the PIN is a UI lock, not a
--    database permission — so this policy is what actually allows the board
--    to load. Only progress rows live here; nothing sensitive.
drop policy if exists "topic progress read" on public.smartple_topic_progress;
create policy "topic progress read"
  on public.smartple_topic_progress
  for select to anon, authenticated
  using (true);

-- 3. Nobody may edit or delete progress from the app (no update/delete policy).

-- Optional: a quick look at the last 20 completions from the SQL editor.
-- select created_at, learner, class_level, subject, topic_title, kind, pct, passed, score
-- from public.smartple_topic_progress
-- order by created_at desc limit 20;

-- ------------------------------------------------------------
-- Fallback note
-- ------------------------------------------------------------
-- If this SQL has not been run yet, the app keeps working: it writes the
-- same event into the existing public.learning_events table and the Owner
-- board reads from there instead (fewer columns, same tick marks). Run this
-- file whenever you want the fuller board.
