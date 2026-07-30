# Design — Sistem Cuti Online Dishub Kota Bogor

Locked design system. Every page reads this before emitting code.

## Genre
modern-minimal

## Tone
utilitarian · trustworthy · institutional

## Audience
PNS (pegawai negeri sipil) Dinas Perhubungan Kota Bogor. Ages 25-55. Mixed digital literacy. Mobile-first (many access from HP).

## Use case
Submit and track leave requests. Admin reviews/approves.

## Theme (OKLCH)
```
--color-paper:    oklch(97%  0.004 250);   /* blue-tinted off-white */
--color-paper-2:  oklch(94%  0.006 250);   /* slightly darker surface */
--color-paper-3:  oklch(91%  0.007 250);   /* elevated surface */
--color-rule:     oklch(85%  0.006 250);   /* borders, dividers */
--color-muted:    oklch(52%  0.008 250);   /* secondary text */
--color-ink:      oklch(18%  0.010 250);   /* primary text — not pure black */
--color-accent:   oklch(42%  0.14  250);   /* institutional navy */
--color-accent-2: oklch(50%  0.12  250);   /* lighter navy for hover */
--color-success:  oklch(62%  0.16  155);   /* green — approved */
--color-warning:  oklch(78%  0.14  80);    /* amber — pending */
--color-error:    oklch(58%  0.18  25);    /* red — rejected */
--color-focus:    oklch(55%  0.16  250);   /* focus ring */
```

## Typography
- Display: **DM Serif Display** (Google Fonts) — roman only, weight 400
- Body: **Geist** (Google Fonts) — weight 400/500/600
- Mono: **Geist Mono** — NIP, no surat, code only

Scale (major third 1.25):
- text-display: clamp(1.75rem, 4vw, 2.25rem)
- text-h1: 1.5rem
- text-h2: 1.25rem
- text-h3: 1rem
- text-body: 0.875rem
- text-small: 0.8125rem
- text-xs: 0.75rem

Line-height: 1.15 for display, 1.5 for body.

## Spacing
4-point scale:
- --space-xs: 0.25rem
- --space-sm: 0.5rem
- --space-md: 1rem
- --space-lg: 1.5rem
- --space-xl: 2rem
- --space-2xl: 3rem

## Motion
- Easing: cubic-bezier(0.22, 1, 0.36, 1)
- Duration: 150ms for micro, 250ms for transitions
- Reduced-motion: opacity only, 150ms max

## CTA voice
- Primary: solid accent fill, rounded-md, font-weight 600, verb-first ("Kirim Pengajuan", "Cek Status")
- Secondary: outline, same shape
- Danger: outline-error, same shape

## Nav archetype
N1b — institutional: wordmark + section links + auth action. No floating pill, no brutal slab. Clean, predictable, trustworthy.

## Footer archetype
Ft2 — inline single line. One line: institution name + copyright. No sitemap columns (this is an internal app).
