# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j auto -W --keep-going -w build_errors.txt -N -q
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	python api_rstgen.py;
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@cp -f "$(SOURCEDIR)/_static/sphx_glr_post_processing_exhaust_manifold_011.png" "$(BUILDDIR)/html/_images/"
	@cp -f "$(SOURCEDIR)/_static/sphx_glr_post_processing_exhaust_manifold_012.png" "$(BUILDDIR)/html/_images/"

# customized clean due to examples gallery
clean:
	rm -rf build_errors.txt
	rm -rf $(BUILDDIR)/*
	rm -rf $(SOURCEDIR)/examples
	find . -type d -name "_autosummary" -exec rm -rf {} +
