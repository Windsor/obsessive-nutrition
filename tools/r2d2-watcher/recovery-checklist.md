# r2d2 Recovery Checklist

*Run through this when server comes back online. Created during Mar 1 night shift.*

## Immediate (run recovery.sh)
```bash
cd ~/tools/r2d2-watcher && bash recovery.sh
```
- Verifies all 5 services (Ghost PT, Ghost Finance, Project Tracker, Quiz Gen, Social Poster)
- Restarts any that are down

## Deploy Pending Changes
```bash
cd ~/tools/r2d2-watcher && bash deploy-pending.sh
```
- Deploys Reddit cross-posting module to social poster
- Runs offsite backup

## Manual Tasks
1. **Update Project Tracker** with all night shift tasks (#287+)
2. **Publish 2 evergreen guides** as drafts:
   - `projects/portugal-news/guides/golden-visa-portugal-2026.md`
   - `projects/portugal-news/guides/d7-visa-portugal-guide.md`
   - Use: `python3 tools/ghost-publisher/publish_guide.py`
3. **Run content audit** to check post health
4. **Run offsite backup** to Mac mini
5. **Check disk usage** (was 84-90%)
6. **Verify cron jobs ran** — morning publishers may have missed editions

## New Tools to Deploy (built locally this shift)
- `tools/news-aggregator/portugal_rss.py` — RSS aggregator (8 feeds)
- `tools/seo/keyword-research.py` — Google autocomplete keyword tool
- `tools/seo/content-gap.py` — content gap analyzer
- `tools/seo/competitor-analysis.py` — RSS competitor tracker
- `tools/editorial-calendar/generate.py` — content calendar generator

## Content Ready to Publish
- Golden Visa 2026 guide (~3,000 words)
- D7 Visa 2026 guide (~2,800 words)
- 4-week editorial calendar (March 2-29)
- Subscriber onboarding email sequence (5 emails)
- Newsletter style guide
