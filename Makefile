style:
	@python -m pip install pre-commit
	@pre-commit run --all-files --show-diff-on-failure

install:
	@pip install -r requirements/requirements_build.txt
	@python -m build
	@pip install dist/*.whl --force-reinstall

version-info:
	@bash -c "date -u +'Build date: %B %d, %Y %H:%M UTC ShaID: <id>' | xargs -I date sed -i 's/_VERSION_INFO = .*/_VERSION_INFO = \"date\"/g' src/ansys/fluent/visualization/__init__.py"
	@bash -c "git --no-pager log -n 1 --format='%h' | xargs -I hash sed -i 's/<id>/hash/g' src/ansys/fluent/visualization/__init__.py"

docker-pull:
	@pip install docker
	@bash .ci/pull_fluent_image.sh

unittest:
	@pip install -r requirements/requirements_tests.txt
	@pip install cryptography==45.0.7
	@python tests/generate_certs.py
	@pytest -v --cov=ansys.fluent --cov-report=xml:cov_xml.xml --cov-report=html

build-doc:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_doc.txt
	@pip install cryptography==45.0.7
	@python doc/api_rstgen.py
	@python tests/generate_certs.py
	@xvfb-run make -C doc html
	@touch doc/_build/html/.nojekyll
	@echo "$(DOCS_CNAME)" >> doc/_build/html/CNAME

docker-clean-images:
	@docker system prune --volumes -a -f
