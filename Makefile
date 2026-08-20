.PHONY: help install quick test metric-robustness public-context public-figures public-validate public rebuild-included full clean-outputs

help:
	@printf '%s\n' \
	  'make install          Install analysis and test dependencies' \
	  'make quick            Regenerate all n=10 trajectories and run tests' \
	  'make test             Run the consolidated scientific test suite' \
	  'make metric-robustness Recompute the central robustness analysis' \
	  'make public-context   Rebuild llms-full.txt from canonical documents' \
	  'make public-figures   Rebuild the five public figures from included inputs' \
	  'make public-validate  Validate links, metadata, file count, and claim qualifiers' \
	  'make public           Rebuild context/figures, run tests, and validate' \
	  'make rebuild-included Recompute analyses from included trajectories and spectra' \
	  'make full             Regenerate n=10,...,20 dense-state-vector trajectories'

install:
	python -m pip install -e '.[analysis,test]'

quick:
	bash scripts/run_quick.sh

test:
	pytest -q

metric-robustness:
	bash scripts/rebuild_all_from_included_data.sh

public-context:
	python scripts/build_llms_full.py

public-figures:
	python scripts/build_public_figures.py

public-validate:
	python analysis/validate_public_repository.py

public: public-context public-figures test public-validate

rebuild-included:
	bash scripts/rebuild_all_from_included_data.sh

full:
	bash scripts/run_full.sh

clean-outputs:
	rm -rf outputs
