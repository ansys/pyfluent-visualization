install:
	@python -m pip install --upgrade pip poetry
	@python -m pip install -r requirements/requirements_build.txt
	@poetry build
	@pip install dist/ansys_fluent_visualization-0.1.dev0-py3-none-any.whl

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
