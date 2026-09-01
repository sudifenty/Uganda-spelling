# Scale Readiness — Smart PLE at Millions of Learners

This document is the operational plan for growing from thousands of learners to
millions **without the app breaking**. Numbers below are measured from the real
build (27 Aug 2026), not estimates.

---

## 1. The four things that break first at scale (and their status)

| # | What breaks | When it breaks | Status |
|---|---|---|---|
| 1 | **Hosting bandwidth** — the app is one ~1 MB (gzipped) file | ~100,000 loads/month on a 100 GB cap | ✅ Fixed by architecture (below) — pick the right host |
| 2 | **Supabase auth quota** — free tier = 50,000 monthly active users | ~50,000 learners who sign in per month | ⚠️ Paid plan needed — see §3 |
| 3 | **Database flood** — every screen view used to write a row | Days, at scale | ✅ Fixed: batched + 1-in-8 sampled (see §4) |
| 4 | **A single uncaught error freezing a learner's screen** | Random, always | ✅ Fixed: global self-healing safety net |

---

## 2. Content delivery — this part scales for free

The app is **one static file**: 4.78 MB raw, **0.95 MB gzipped** (verified: gzip -9).
Every lesson, note, paper and voice is inside it. No API calls for content.

| Monthly learners | Transfer/month | Vercel Hobby (100 GB) | Vercel Pro (1 TB) | Cloudflare Pages |
|---|---|---|---|---|
| 10,000 | 10 GB | ✅ | ✅ | ✅ |
| 100,000 | 100 GB | ❌ dies at ~100k | ✅ | ✅ (unlimited static) |
| 1,000,000 | 1,000 GB | ❌ | ⚠️ at the edge | ✅ (unlimited static) |
| 3,000,000 | 3,000 GB | ❌ | ❌ overage charges | ✅ (unlimited static) |

**Recommendation: host the static file on Cloudflare Pages** (unlimited bandwidth
for static assets, free tier, and you already use Cloudflare). Vercel Pro works
to ~1M loads then bills overage. GitHub Pages soft-caps at 100 GB.

Repeat visits cost almost nothing: the host sends an ETag and the browser
revalidates instead of re-downloading (only hard refreshes pull the full ~1 MB).

**First-load time on slow networks (typical Uganda):** ~0.95 MB ≈ 3–8 minutes
on 2G, ~30 s on 3G, ~2 s on 4G. Acceptable for a once-only download; after that
it is cached. If this ever becomes the top complaint, the next step is splitting
the class data into per-class files (P4 file, P5 file…) — a bigger change, only
do it when the data says so.

---

## 3. Sign-in (Supabase) — the one part with hard quotas

| Tier | Monthly active users | Database | Cost |
|---|---|---|---|
| Free | 50,000 | 500 MB | $0 — **project pauses after ~1 week of inactivity** |
| Pro | 100,000 (then per-user) | 8 GB | $25/month |

At millions of learners, auth is a real budget line (roughly $0.003–0.01 per
MAU beyond the included 100k). Plan it like server costs.

**Decisions to make in the Supabase dashboard (Dashboard → Authentication):**

1. **Turn OFF "Confirm email".** Young learners often share devices, type
   invented emails, and cannot receive mail. Built-in email is also rate-limited
   hard. The app already handles both settings gracefully — but off is the right
   default for this audience.
2. **Rate limits & shared IPs:** a whole school behind one IP can trip Supabase's
   per-IP auth limits. Mitigations already in the app: sessions persist
   indefinitely (learners stay signed in), and a friendly rate-limit message.
   For launch-day at a big school, have learners sign up on different days or
   contact Supabase to raise the limit.
3. **Password reset** is built in ("Forgot your password?" → email link →
   set-a-new-password screen). Note: reset emails use the same rate-limited
   built-in mail — if resets matter at scale, connect a real SMTP provider
   (Resend, Postmark…) under Authentication → Email Templates/SMTP.

**Never share the service-role key anywhere.** The publishable key in the HTML
is designed to be public — that is safe **only if** Row Level Security is on (§4).

---

## 4. The `learning_events` table — protected, but with limits

The app now **batches** analytics: screen views are sampled 1-in-8, queued in
memory, and flushed as one insert every 45 s / 25 events / when the learner
leaves. Offline drops are silent by design. This cut database writes ~30–240×.

**Do the math before trusting it at full scale:**

| Daily active learners | Rows/day (sampled) | DB growth/month (~150 B/row) | Fits free (500 MB) | Fits Pro (8 GB) |
|---|---|---|---|---|
| 1,000 | ~3,750 | ~17 MB | ✅ ~1 month | ✅ |
| 100,000 | ~375,000 | ~1.7 GB | ❌ | ✅ |
| 1,000,000 | ~3,750,000 | ~17 GB | ❌ | ❌ |

**Required now — run this SQL once in the Supabase SQL editor** (protects the
table from anyone with the public key):

```sql
alter table public.learning_events enable row level security;

create policy "learners insert their own events"
  on public.learning_events for insert to authenticated
  with check (auth.uid() = user_id);

create policy "learners read their own events"
  on public.learning_events for select to authenticated
  using (auth.uid() = user_id);
```

**Required beyond ~50k daily learners — auto-cleanup** (needs the pg_cron
extension, enabled in the dashboard):

```sql
-- add a timestamp first if the table does not have one:
alter table public.learning_events add column if not exists created_at timestamptz default now();

select cron.schedule('prune-learning-events', 'weekly',
  $$delete from public.learning_events where created_at < now() - interval '90 days'$$);
```

Beyond ~100k daily learners, screen-view telemetry is not worth the storage:
change the sampling in `trackActivity` (search for `%8` in index.html) to a
bigger number, or drop screen views entirely and keep the batching for events
that matter (exercise submissions, results).

---

## 5. The natural voice — 60 MB, once per device

The Piper narrator downloads ~60 MB **once per device** and is then fully
offline. At very large scale that traffic hits HuggingFace's CDN, not yours —
it works, but it is someone else's generosity. Watch it; if it ever gets slow
or blocked, options: mirror the voice model on your own Cloudflare CDN, or rely
on the device voice.

**The app never leaves a learner in silence:** if the narrator is not
downloaded yet, it speaks with the phone's built-in voice and says so once
("Using the phone voice for now…"). No download required to hear lessons.

---

## 6. Single points of failure (honest list)

| Failure | Effect today | Learner experience |
|---|---|---|
| jsDelivr CDN down | Login library won't load | Returning learners: straight in (cached session). New learners: "You are offline" message. Content still works. |
| Supabase outage | No new sign-ins | Returning learners unaffected. |
| Supabase project paused (free tier) | No new sign-ins | Same as above — **upgrade to Pro before launch** to remove this risk. |
| HuggingFace slow | 60 MB narrator download slow | Phone voice used meanwhile. |
| One learner hits a bug | Screen would freeze | **Fixed:** the safety net catches the error, returns them to a safe screen. |

---

## 7. Pre-launch checklist

- [ ] Supabase: upgrade to Pro (removes pausing + raises MAU to 100k)
- [ ] Supabase: disable "Confirm email"
- [ ] Supabase: run the RLS SQL from §4
- [ ] Supabase: run the cleanup job from §4
- [ ] Hosting: deploy on Cloudflare Pages (or accept Vercel Pro overage)
- [ ] Verify gzip is actually served: `curl -sI -H 'Accept-Encoding: gzip' <your-url> | grep -i content-encoding` should say `gzip` or `br`
- [ ] Test one real school day: many learners, one network, cheap Android phones
- [ ] Watch for a week: Supabase dashboard (MAU, DB size), host analytics (bandwidth)

---

## 8. What was changed in the app for scale (27 Aug 2026)

1. `supabase-js` pinned to **2.112.4** (a floating `@2` could change the
   session-storage format and break offline sign-in for everyone at once).
2. Activity tracking batched + sampled 1-in-8 (~30–240× fewer DB writes).
3. Global error safety net: any uncaught error returns the learner to a safe
   screen instead of freezing.
4. Voice: informed fallback to the phone voice until the narrator is downloaded.
5. Forgot-password flow end-to-end, including the set-a-new-password screen.
6. Offline: returning learners are let in from their cached session.

All verified by automated boot-simulation tests (offline fresh user, offline
returning user, analytics batching, voice fallback, error recovery).
