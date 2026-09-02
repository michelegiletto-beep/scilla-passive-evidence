PYTHON ?= python
REPRO_OUT ?= reproduction_output
STRESS_OUT ?= reproduction_stress
CANDIDATE_NOMINAL_OUT ?= candidate_nominal
CANDIDATE_STRESS_OUT ?= candidate_stress
CANDIDATE_AUDIT_OUT ?= candidate_audit/CORRECTED_MODEL_AUDIT.json

.PHONY: test quick nominal frozen-quick frozen-nominal candidate-stress candidate-audit partner-dossier stress-physics \
	stress-integrity stress-figures stress-verify stress-all manifest manifest-check \
	bootstrap-audit

test:
	$(PYTHON) -m unittest discover -s tests -v

quick:
	$(PYTHON) software/run_release.py --mode quick --model-version 1.1.0-candidate --out $(REPRO_OUT) --force

nominal:
	$(PYTHON) software/run_release.py --mode nominal --model-version 1.1.0-candidate --out $(REPRO_OUT) --force

candidate-stress:
	$(PYTHON) software/run_stress.py --suite all --model-version 1.1.0-candidate --out $(CANDIDATE_STRESS_OUT)

candidate-audit:
	$(PYTHON) software/audit_candidate.py --nominal-dir $(CANDIDATE_NOMINAL_OUT) --stress-dir $(CANDIDATE_STRESS_OUT) --legacy-dir results --out $(CANDIDATE_AUDIT_OUT)

partner-dossier:
	$(PYTHON) software/generate_partner_dossier.py

frozen-quick:
	$(PYTHON) software/run_release.py --mode quick --model-version 1.0.0 --out $(REPRO_OUT) --force

frozen-nominal:
	$(PYTHON) software/run_release.py --mode nominal --model-version 1.0.0 --out $(REPRO_OUT) --force

stress-physics:
	$(PYTHON) software/run_stress.py --suite physics --out $(STRESS_OUT)

stress-integrity:
	$(PYTHON) software/run_stress.py --suite integrity --out $(STRESS_OUT)

stress-figures:
	$(PYTHON) software/generate_stress_figures.py --input $(STRESS_OUT) --out $(STRESS_OUT)/figures

stress-verify:
	$(PYTHON) software/run_stress.py --suite all --out $(STRESS_OUT) --frozen results --verify-only

stress-all:
	$(PYTHON) software/run_stress.py --suite all --out $(STRESS_OUT) --frozen results --verify-frozen
	$(PYTHON) software/generate_stress_figures.py --input $(STRESS_OUT) --out $(STRESS_OUT)/figures

manifest:
	$(PYTHON) software/build_manifest.py

manifest-check:
	$(PYTHON) software/build_manifest.py --check

bootstrap-audit:
	$(PYTHON) software/bootstrap_nominal.py
