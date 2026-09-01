# Publication QA Gate - Final v1.0.0

## Scientific QA
- [x] conventional estimator baseline retained;
- [x] same simulated worlds replayed across policies;
- [x] 300 nominal worlds per policy;
- [x] 95% bootstrap CI for nominal medians;
- [x] 54 physics cells x 30 worlds;
- [x] 27 integrity cells x 30 worlds;
- [x] target maneuver stress;
- [x] emitter-association error stress;
- [x] clutter/outlier stress;
- [x] failed original policy preserved;
- [x] physics failure cells preserved;
- [x] no measured claim.

## Editorial / archive QA
- [x] title does not claim novelty;
- [x] abstract labels simulation status;
- [x] optimizer moat explicitly rejected;
- [x] prior-art boundary stated;
- [x] buyer brief separates evidence from target state;
- [x] reserved DOI inserted: `10.5281/zenodo.22229086`;
- [x] `CITATION.cff`, README and Zenodo metadata updated;
- [x] unit tests rerun after DOI injection;
- [x] quick reproduction rerun after DOI injection;
- [x] final technical report rendered and visually inspected;
- [x] final industrial brief rendered and visually inspected;
- [x] PDF preflight: openable, unencrypted, text-based;
- [x] no invented traction/customer claim.

## Zenodo publication gate
- [ ] upload the single final ZIP to the existing Zenodo draft;
- [ ] choose Resource type = Software;
- [ ] set Version = 1.0.0;
- [ ] verify creator/title/date/DOI;
- [ ] replace Zenodo's default CC BY license with the intended custom rights notice if proprietary reuse restrictions are desired;
- [ ] preview the record;
- [ ] publish the Zenodo record.

## Post-Zenodo gate
- [ ] create public repository from the exact v1.0.0 archive;
- [ ] add canonical DOI link;
- [ ] run `make test && make quick` from public repository;
- [ ] only then launch Systems Lab / LinkedIn / targeted industrial distribution.

## Director gate
**FINAL v1.0.0 = ZENODO-READY. Publication itself is the next user action.**
