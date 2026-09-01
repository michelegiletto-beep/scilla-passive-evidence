# Publication Handoff - Final DOI-Resolved Workflow

## Chosen primary DOI workflow
Use a **manual Zenodo deposit** for Release 1.0.0. This allows a DOI to be reserved while the record is still a draft, so the real DOI can be inserted into the PDF, `CITATION.cff`, README and metadata before publication.

For the first release, do not use automatic Zenodo-GitHub ingestion as the primary archive if the goal is to pre-print the DOI inside the technical report. Zenodo documents that DOI pre-reservation is not available through its GitHub integration.

## User sequence
1. Open Zenodo and create a new upload/draft.
2. Use the DOI field to reserve a DOI. **Do not publish the Zenodo record yet.**
3. Reserved DOI received: `10.5281/zenodo.22229086`.
4. Release promoted from `1.0.0-rc1` to `1.0.0`; DOI inserted into:
   - technical report PDF/source;
   - industrial brief;
   - `CITATION.cff`;
   - README;
   - publication metadata.
5. Upload the final `1.0.0` ZIP into the same Zenodo draft. Preview and verify metadata, then publish.
6. Create the public GitHub repository from the exact final archive contents.
7. Add the Zenodo DOI as the canonical citation/archive link.
8. Run `make test` and `make quick` once from the public repository.
9. Only after both Zenodo and GitHub resolve correctly, publish the Systems Lab page and LinkedIn technical note.

## Suggested GitHub repository
Name: `scilla-passive-evidence`

Description: `Reproducible public research on cue-driven opportunistic maritime verification using non-cooperative merchant-radar illumination. Simulation evidence only; no measured RF performance claimed.`

Suggested topics: `passive-radar`, `maritime-surveillance`, `bistatic-radar`, `sensor-fusion`, `reproducible-research`, `maritime-domain-awareness`, `kalman-filter`, `simulation`

## Licensing
No open-source license is included in v1.0.0. Keep `LICENSE` and `RIGHTS_AND_DISCLOSURE.md`. Public GitHub hosting remains subject to GitHub platform terms.
