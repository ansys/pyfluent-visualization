style:
	@python -m pip install pre-commit
	@pre-commit run --all-files --show-diff-on-failure

install:
	@pip install -r requirements/requirements_build.txt
	@python -m build
	@pip install dist/*.whl --force-reinstall

docker-pull:
	@pip install docker
	@python .ci/pull_fluent_image.py

unittest:
	@pip install -r requirements/requirements_tests.txt
	@pytest -v --cov=ansys.fluent --cov-report html:cov_html --cov-config=.coveragerc

build-doc:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_doc.txt
	@xvfb-run make -C doc html
	@touch doc/_build/html/.nojekyll
	@echo "$(DOCS_CNAME)" >> doc/_build/html/CNAME
