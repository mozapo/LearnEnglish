# SEO work (Oct 2026)

Read `REPORT.md` first: what the audit claimed, what was verified, what changed, what waits for approval.

**State on 19 Oct 2026:** metadata and content groups A, B and C are on staging and live, verified on both. The section-5 wording in REPORT.md is still open.

```bash
python3 seo/publish.py staging|live meta [--only ID ...] [--rollback] [--yes]   # SureRank titles/descriptions/robots
python3 seo/publish.py staging|live content A|B|C [--rollback] [--yes]          # page text and link fixes
python3 seo/publish.py staging|live restore --only ID ... [--yes]               # page back to the 19 Oct backup
python3 seo/backup.py live|staging                                              # content + SEO settings backup
python3 seo/crawl.py live OUT.json                                              # public crawl (status, meta, hreflang, schema, links)
LH_BIN=.../lighthouse seo/lighthouse.sh OUTDIR URL...; python3 seo/lh_summary.py OUTDIR
```

- `publish.py` writes only when a page or SEO field is in the state recorded on 19 Oct, or already updated. It
  refuses anything changed by someone else, verifies what was saved, and clears the Elementor and LiteSpeed caches.
- Elementor pages: after writing `_elementor_data` over the API, the Elementor cache must be cleared
  (`DELETE /wp-json/elementor/v1/cache`), or the old text keeps showing. `publish.py` does this.
- SureRank per-page settings: `GET/POST /wp-json/surerank/v1/post/settings` (`post_id`, `post_type` / `metaData`).
  Its noindex value must be `"yes"`; `"1"` is ignored.
- Staging is noindexed site-wide on purpose, so compare robots against live, not staging.
- Metadata wording rules: Turkish "sen" on marketing pages, "siz" on legal pages, "rehberlik" not "danışmanlık",
  no outcome promises, and every fact taken from the page itself.
