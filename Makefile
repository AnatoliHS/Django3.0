help: 
	@echo "================================================"
	@echo "       Startr/WEB-Django by Startr.Cloud"
	@echo "================================================"
	@echo "This is the default make command."
	@echo "This command lists available make commands."
	@echo ""
	@echo "Usage example:"
	@echo "    make it_run"
	@echo ""
	@echo "Available make commands:"
	@echo ""
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | \
		awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ { \
		if ($$1 !~ "^[#.]") {print $$1}}' | \
		sort | \
		grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'
	@echo ""

# Docker container name
CONTAINER = web-django-develop

# Load environment variables from .env file if it exists
-include .env

# Default values for environment variables (if not set in .env)
SERVER__HOST ?= SERVER_
SERVER__USER ?= root
SERVER__CONTAINER_FILTER ?= name=web-django

# Django management commands
bash:
	docker exec -it $(CONTAINER) bash

ssh_SERVER_:
	@echo "Connecting to SERVER_ server..."
	ssh $(SERVER__USER)@$(SERVER__HOST)

django:
	@if [ "$(cmd)" = "" ]; then \
		echo "Usage: make django cmd='command'"; \
		echo "Example: make django cmd='migrate'"; \
	else \
		docker exec -it $(CONTAINER) bash -c "\
			cd /project/our_site && \
			python manage.py $(cmd)"; \
	fi

it_setup:
	@echo "Initializing git flow with defaults..."
	git flow init -d
	@echo "Setting upstream for develop branch..."
	git branch --set-upstream-to=origin/develop develop
	@echo "Updating submodules..."
	git submodule update --init --recursive

it_run:
	@bash -c 'bash <(curl -sL startr.sh) run'

it_build:
	@bash -c 'bash <(curl -sL startr.sh) build'

it_build_n_run:
	@bash -c 'bash <(curl -sL startr.sh) build && bash <(curl -sL startr.sh) run'

it_startr:
	# @bash -c 'fswatch -r -v -e ".*" ./our_site/django_startr/ | while read changed_path; do \
	# 	echo "Detected change in $$changed_path"; \
	# 	git restore ./our_site/experiences/ && git clean -fd ./our_site/experiences/; \
	# 	docker exec -it web-django-develop bash -c "cd /project/our_site && ./manage.py startr experiences && ./manage.py runserver 0.0.0.0:8000"; \
	# done'
	git restore ./our_site/experiences/ && git clean -fd ./our_site/experiences/; \
	docker exec -it web-django-develop bash -c "cd /project/our_site && ./manage.py startr experiences && ./manage.py runserver 0.0.0.0:8000";

backup:
	@if [ -z "$(container_id)" ]; then \
		echo "Using default container name: $(CONTAINER)"; \
		CONTAINER_TO_BACKUP=$(CONTAINER); \
	else \
		echo "Using specified container ID: $(container_id)"; \
		CONTAINER_TO_BACKUP=$(container_id); \
	fi; \
	\
	echo "Creating backup directory..."; \
	mkdir -p ./backups/$(shell date +%Y-%m-%d_%H-%M-%S); \
	BACKUP_DIR=./backups/$(shell date +%Y-%m-%d_%H-%M-%S); \
	\
	echo "Backing up media files..."; \
	docker cp $$CONTAINER_TO_BACKUP:/project/our_site/media/ $$BACKUP_DIR/media/; \
	\
	echo "Backing up database..."; \
	docker cp $$CONTAINER_TO_BACKUP:/project/our_site/db.sqlite3 $$BACKUP_DIR/db.sqlite3; \
	\
	echo "Backup completed successfully to $$BACKUP_DIR"; \
	echo "Media files: $$BACKUP_DIR/media/"; \
	echo "Database: $$BACKUP_DIR/db.sqlite3"

backup_SERVER_:
	@echo "Creating a remote backup on $(SERVER__HOST) server..."
	@echo "Connecting to $(SERVER__HOST) and creating backup..."
	ssh $(SERVER__USER)@$(SERVER__HOST) "mkdir -p /$(SERVER__USER)/backups/$(shell date +%Y-%m-%d_%H-%M-%S) && \
		CONTAINER_ID=\$$(docker ps -qf $(SERVER__CONTAINER_FILTER)) && \
		echo \"Found container ID: \$$CONTAINER_ID\" && \
		docker cp \$$CONTAINER_ID:/project/our_site/media /$(SERVER__USER)/backups/$(shell date +%Y-%m-%d_%H-%M-%S)/media && \
		docker cp \$$CONTAINER_ID:/project/our_site/db.sqlite3 /$(SERVER__USER)/backups/$(shell date +%Y-%m-%d_%H-%M-%S)/db.sqlite3 && \
		echo \"Backup completed successfully on $(SERVER__HOST)\""

fetch_backup_from_SERVER_:
	@echo "Fetching latest backup from $(SERVER__HOST) server..."
	@if [ -z "$(backup_date)" ]; then \
		echo "No specific backup date provided. Fetching the latest backup..."; \
		REMOTE_BACKUP_DIR=$$(ssh $(SERVER__USER)@$(SERVER__HOST) "ls -td /$(SERVER__USER)/backups/*/ | head -1"); \
	else \
		echo "Fetching backup from date: $(backup_date)"; \
		REMOTE_BACKUP_DIR="/$(SERVER__USER)/backups/$(backup_date)"; \
	fi; \
	\
	echo "Creating local directory for the backup..."; \
	mkdir -p ./backups/from_$(SERVER__HOST)_$(shell date +%Y-%m-%d_%H-%M-%S); \
	LOCAL_BACKUP_DIR=./backups/from_$(SERVER__HOST)_$(shell date +%Y-%m-%d_%H-%M-%S); \
	\
	echo "Downloading backup from $(SERVER__HOST)..."; \
	scp -r $(SERVER__USER)@$(SERVER__HOST):$$REMOTE_BACKUP_DIR/* $$LOCAL_BACKUP_DIR/; \
	\
	echo "Backup fetched successfully to $$LOCAL_BACKUP_DIR"

update_submodules:
	@echo "Developer instructions: Please update your Dockerfile manually to add the appropriate 'RUN' command for installing git (using apt-get or apk) and to include the submodule update command. Then run 'git submodule update --init --recursive'."

# Check if .gitmodules exists (returns 1 if present, empty otherwise)
HAS_SUBMODULE := $(shell [ -f .gitmodules ] && echo 1)

# for deployment to work we need to be logged in to caprover
# and have the caprover CLI installed
# check if caprover is installed
HAS_CAPROVER := $(shell which caprover 2>/dev/null && echo 1)
# check if we are logged in to caprover
HAS_CAPROVER_LOGIN := $(shell caprover ls | grep -q "Logged in" && echo 1)

# Default deploy flags
DEPLOY_FLAGS ?=

# Deploy target that accepts optional parameters
deploy:
	@if [ "$(HAS_CAPROVER)" = "" ]; then \
		echo "CapRover CLI is not installed. Please install it first."; \
		echo "You can install it using npm: npm install -g caprover"; \
		exit 1; \
	elif [ "$(HAS_CAPROVER_LOGIN)" = "" ]; then \
		echo "You are not logged in to CapRover."; \
		echo "Please log in using the command: caprover login"; \
		exit 1; \
	fi
	@if [ "$(HAS_SUBMODULE)" = "1" ]; then \
		echo "Submodules detected."; \
		echo "We will create a tar of the project and deploy it"; \
		echo "Creating tar of project..."; \
		echo -e "\a"; \
		git ls-files --recurse-submodules | tar -czf deploy.tar -T -; \
		echo "Deploying to CapRover using the tar file..."; \
		npx caprover deploy -t ./deploy.tar $(DEPLOY_FLAGS); \
		rm ./deploy.tar; \
	else \
		echo "No submodules detected. Deploying normally..."; \
		npx caprover deploy $(DEPLOY_FLAGS); \
	fi

# Special target for default deployment
default-deploy:
	@$(MAKE) deploy DEPLOY_FLAGS="--default"

minor_release:
	# Start a minor release with incremented minor version
	git flow release start $$(git tag --sort=-v:refname | sed 's/^v//' | head -n 1 | awk -F'.' '{print $$1"."$$2+1".0"}')

patch_release:
	# Start a patch release with incremented patch version
	git flow release start $$(git tag --sort=-v:refname | sed 's/^v//' | head -n 1 | awk -F'.' '{print $$1"."$$2"."$$3+1}')

major_release:
	# Start a major release with incremented major version
	git flow release start $$(git tag --sort=-v:refname | sed 's/^v//' | head -n 1 | awk -F'.' '{print $$1+1".0.0"}')

hotfix:
	# Start a hotfix with incremented n.n.n.n version (incrementing the fourth number)
	git flow hotfix start $$(git tag --sort=-v:refname | sed 's/^v//' | head -n 1 | awk -F'.' '{print $$1"."$$2"."$$3"."$$4+1}')

release_finish:
	git flow release finish "$$(git branch --show-current | sed 's/release\///')" && git push origin develop && git push origin master && git push --tags && git checkout develop

hotfix_finish:
	git flow hotfix finish "$$(git branch --show-current | sed 's/hotfix\///')" && git push origin develop && git push origin master && git push --tags && git checkout develop

things_clean:
	git clean --exclude=!.env -Xdf
