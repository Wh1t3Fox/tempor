export DOCKER_BUILDKIT=1

# include our API tokens
-include $(PWD)/api_tokens.mk

ifneq ("$(do_token)","")
TOKEN := $(do_token)
PROVIDER := digitalocean
else ifneq ("$(li_token)","")
TOKEN := $(li_token)
PROVIDER := linode
else ifneq ("$(vultr_token)","")
TOKEN := $(vultr_token)
PROVIDER := vultr
else
$(error No API Tokens! Define them in $(PWD)/api_tokens.mk)
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
	@test -n "$(shell docker images terraform-deploy | tail -n1 | grep -o terraform-deploy)" || docker build -t terraform-deploy .

.PHONY: build-nc
build-nc:						## Build Docker Containers w/out Cache
	@docker build -t terraform-deploy --no-cache .

.PHONY: clean
clean: destroy					## Cleanup VPS and Files
	@sudo find -name '.terraform' -type d -exec rm -fr {} \; 2>/dev/null || true
	@find -name 'terraform.tfstate*' -type f -exec rm -f {} \; 2>/dev/null || true
	@find -name 'plan' -type f -exec rm -f {} \; 2>/dev/null || true
	@docker rmi terraform-deploy >/dev/null 2>&1 || true

.PHONY: run
run: build					## Run Terraform
	@docker run -it --rm --init -v "$(PWD)/providers/$(PROVIDER):/work" terraform-deploy terraform init
	@docker run -it --rm --init -v "$(PWD)/providers/$(PROVIDER):/work" terraform-deploy terraform plan -var "api_token=$(TOKEN)" -out /work/plan
	@docker run -it --rm --init -v "$(PWD)/providers/$(PROVIDER):/work" terraform-deploy terraform apply /work/plan
	@docker run -it --rm --init -v "$(PWD)/providers/$(PROVIDER):/work" terraform-deploy terraform output -json droplet_ip_address | jq '.'

.PHONY: show
show: build					## Show VPS Options
	@docker run -it --rm --init -v "$(PWD)/providers/$(PROVIDER):/work" terraform-deploy terraform show

.PHONY: test
test: build					## Live Testing with Terraform
	@docker run -it --rm --init -v "$(PWD)/providers/$(PROVIDER):/work" terraform-deploy /bin/bash

.PHONY: destory
destroy: build						## Destroy VPS'
	@docker run -it --rm --init -v "$(PWD)/providers/$(PROVIDER):/work" terraform-deploy terraform destroy -var "api_token=$(TOKEN)"
