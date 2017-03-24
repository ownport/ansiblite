PYTHON ?= /usr/bin/env python
PROJECT_NAME_BIN ?= ansiblite
PROJECT_NAME_SRC ?= ansiblite

clean:
	@ echo "[INFO] Cleaning directory:" $(shell pwd)/.local-ci
	@ rm -rf $(shell pwd)/.local-ci
	@ echo "[INFO] Cleaning directory:" $(shell pwd)/target
	@ rm -rf $(shell pwd)/target
	@ echo "[INFO] Cleaning files: *.pyc"
	@ find . -name "*.pyc" -delete
	@ echo "[INFO] Cleaning files: .coverage"
	@ rm -rf $(shell pwd)/.coverage


compile: clean
	@ echo "[INFO] Compiling to binary, $(PROJECT_NAME_BIN)"
	@ mkdir -p $(shell pwd)/target
	@ cd $(shell pwd)/src/; zip --quiet -r ../target/$(PROJECT_NAME_BIN) *
	@ echo '#!$(PYTHON)' > target/$(PROJECT_NAME_BIN) && \
		cat target/$(PROJECT_NAME_BIN).zip >> target/$(PROJECT_NAME_BIN) && \
		rm target/$(PROJECT_NAME_BIN).zip && \
		chmod a+x target/$(PROJECT_NAME_BIN)
	@ cd target && ln -s $(PROJECT_NAME_BIN) ansiblite-playbook
