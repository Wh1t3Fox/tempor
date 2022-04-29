export DOCKER_BUILDKIT=1

GIT_NOT_CLEAN_CHECK = $(shell git status --porcelain)

ifeq ($(MAKECMDGOALS),release)

ifneq (x$(GIT_NOT_CLEAN_CHECK), x)
$(error echo You are trying to release a build based on a dirty repo)
endif

endif

all: help

.PHONY: help
help:
	@echo -ne "\033[1mOption\t\t\tDescription\033[0m\n"
	@awk 'BEGIN {FS = ":.*?##"} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo -e "\n\033[1mCurrent Provider:\033[0m $(PROVIDER)"

.DEFAULT_GOAL := help

.PHONY: build
build:						## Build Docker Containers
	@docker build -t tempor-test .

.PHONY: build-nc
build-nc:						## Build Docker Containers w/out Cache
	@docker build -t tempor-test --no-cache .

.PHONY: clean
clean: 					## Cleanup VPS and Files
	@find -name '*.pyc' -type f -exec rm -f {} \; 2>/dev/null || true
	@find -name 'plan' -type f -exec rm -f {} \; 2>/dev/null || true
	@find -name 'terraform.tfstate*' -type f -exec rm -f {} \; 2>/dev/null || true
	@find -name '*.egg-info' -type d -exec rm -fr {} \; 2>/dev/null || true
	@find -name '.ssh' -type d -exec rm -fr {} \; 2>/dev/null || true
	@find -name '__pycache__' -type d -exec rm -fr {} \; 2>/dev/null || true
	@find -name '.terraform' -type d -exec rm -fr {} \; 2>/dev/null || true
	@find -name '.terraform*' -type f -exec rm -fr {} \; 2>/dev/null || true
	@rm -fr dist || true
	@docker rmi tempor-test >/dev/null 2>&1 || true

.PHONY: test
test: build					## Testing with Terraform
	@docker run -it --rm --init -v "$(HOME)/.config/tempor/:/home/user/.config/tempor/:ro" --entrypoint=/bin/bash tempor-test

.PHONY: release
release: clean
	@echo -e "${VER}" > tempor/VERSION
	@git add tempor/VERSION
	@git commit -m "Version ${VER}"
	@git push
	@git tag -a "${VER}" -m "${VER}"
	@git push origin --tags
