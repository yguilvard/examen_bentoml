.PHONY: init init-jwt-secret prepare train serve test clean all bento-build bento-list bento-serve bento-export bento-containerize archive

BENTO_NAME := admission_service
BENTO_TAG := $(BENTO_NAME):latest
TEST_PORT ?= 3000
DATA_DIRECTORY ?= $(PWD)/data
JWT_SECRET_FILE := $(PWD)/.jwt_secret
SUBMISSION_DIR := dist/submission
SUBMISSION_ARCHIVE := dist/$(BENTO_NAME)_submission.tar.gz
DOCKER_IMAGE_ARCHIVE := $(SUBMISSION_DIR)/$(BENTO_NAME)_docker_image.tar.gz

init: init-jwt-secret
	uv run python -m src.data.import_raw_dataset

init-jwt-secret:
	@uv run python -m src.api.create_jwt_secret_file -o $(JWT_SECRET_FILE)

init-jwt-secret-force:
	@uv run python -m src.api.create_jwt_secret_file -o $(JWT_SECRET_FILE) --force

init_force: init-jwt-secret
	@uv run python -m src.data.import_raw_dataset --force

prepare:
	uv run python -m src.data.prepare_data

train:
	@uv run python -m src.models.train_model
	@uv run bentoml models list 

serve:
	@ADMISSION_DATA_DIRECTORY=$(DATA_DIRECTORY) JWT_SECRET_KEY=$$(cat "$(JWT_SECRET_FILE)") uv run python -m src.adapters.users_fs --user admin --password admin
	@ADMISSION_DATA_DIRECTORY=$(DATA_DIRECTORY) JWT_SECRET_KEY=$$(cat "$(JWT_SECRET_FILE)") uv run bentoml serve service:AdmissionService --port $(TEST_PORT)

test:
	@TEST_API_USERNAME=admin TEST_API_PASSWORD=admin TEST_API_PORT=$(TEST_PORT) JWT_SECRET_KEY=$$(cat "$(JWT_SECRET_FILE)") uv run pytest -v -s tests/
	@echo "TOKEN=$$(curl -s -X POST http://localhost:$(TEST_PORT)/login -H \"Content-Type: application/json\" -d '{\"username\":\"admin\",\"password\":\"admin\"}' | python3 -c \"import sys, json; print(json.load(sys.stdin)['access_token'])\")"
	@echo "curl -s -X POST http://localhost:$(TEST_PORT)/predict -H \"Content-Type: application/json\" -H \"Authorization: Bearer \$$TOKEN\" -d '{\"request\":{\"gre_score\":0.95,\"toefl_score\":0.9,\"rating\":0.8,\"sop\":0.8,\"lor\":0.8,\"cgpa\":0.85,\"research_xp\":1.0}}'"
	@TOKEN=$$(curl -s -X POST http://localhost:$(TEST_PORT)/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])"); \
	curl -s -X POST http://localhost:$(TEST_PORT)/predict \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $$TOKEN" \
		-d '{"request":{"gre_score":0.95,"toefl_score":0.9,"rating":0.8,"sop":0.8,"lor":0.8,"cgpa":0.85,"research_xp":1.0}}'

bento-build:
	@uv run bentoml build -f bentofile.yaml --name $(BENTO_NAME)


bento-list:
	@uv run bentoml list

bento: bento-build
	@ADMISSION_DATA_DIRECTORY=$(DATA_DIRECTORY) JWT_SECRET_KEY=$$(cat "$(JWT_SECRET_FILE)") uv run python -m src.adapters.users_fs --user admin --password admin
	@ADMISSION_DATA_DIRECTORY=$(DATA_DIRECTORY) JWT_SECRET_KEY=$$(cat "$(JWT_SECRET_FILE)") uv run bentoml serve $(BENTO_TAG) --port $(TEST_PORT)

bento-export:
	@mkdir -p dist
	@uv run bentoml export $(BENTO_TAG) ./dist/$(BENTO_NAME).bento

bento-containerize:
	@uv run bentoml containerize $(BENTO_TAG) --image-tag $(BENTO_NAME):latest

bento-container-serve: bento-build bento-containerize
	@ADMISSION_DATA_DIRECTORY=$(DATA_DIRECTORY) JWT_SECRET_KEY=$$(cat "$(JWT_SECRET_FILE)") uv run python -m src.adapters.users_fs --user admin --password admin
	@JWT_SECRET_KEY=$$(cat "$(JWT_SECRET_FILE)") docker-compose up

archive: bento-containerize
	@mkdir -p $(SUBMISSION_DIR)
	@rm -rf $(SUBMISSION_DIR)/tests
	@cp README.md $(SUBMISSION_DIR)/README.md
	@cp requirements.txt $(SUBMISSION_DIR)/requirements.txt
	@cp -R tests $(SUBMISSION_DIR)/tests
	@find $(SUBMISSION_DIR)/tests -name '__pycache__' -type d -exec rm -rf {} +
	@docker save $(BENTO_NAME):latest | gzip > $(DOCKER_IMAGE_ARCHIVE)
	@rm -f $(SUBMISSION_ARCHIVE)
	@tar -czf $(SUBMISSION_ARCHIVE) -C $(SUBMISSION_DIR) .
	@echo "Submission archive created at $(SUBMISSION_ARCHIVE)"

clean:
	-@rm -v -- ./data/processed/*
	-@rm -v -- ./data/raw/*
	-@uv run bentoml models delete admission_ridge -y
	-@uv run bentoml delete $(BENTO_TAG) -y
	-@docker-compose down
	-@rm -v -- $(DOCKER_IMAGE_ARCHIVE)
	-@rm -v -- $(SUBMISSION_ARCHIVE)
	-@rm -v -- $(SUBMISSION_DIR)/tests/*
	-@rm -v -- $(SUBMISSION_DIR)/*
	-@rm -v -- $(JWT_SECRET_FILE)
	-@rm -v -- $(DATA_DIRECTORY)/api/*
	@echo "Cleanup done."

local: clean init prepare train serve
bento-serve: clean init prepare train bento-build bento
container-serve: clean init prepare train bento-container-serve
