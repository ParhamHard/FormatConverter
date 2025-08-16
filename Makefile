# Media Converter Service Makefile

.PHONY: help install dev test clean docker-build docker-run docker-stop lint format

help: ## Show this help message
	@echo "Media Converter Service - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -e .

dev: ## Start development server
	./start.sh dev

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html

clean: ## Clean up temporary files and directories
	rm -rf uploads/* converted/* temp/* logs/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build: ## Build Docker image
	docker-compose build

docker-run: ## Start Docker services
	docker-compose up -d

docker-stop: ## Stop Docker services
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f converter

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/

check: ## Check system requirements
	python -m src check

convert: ## Convert a file (usage: make convert INPUT=file.mp3 OUTPUT=file.wav FORMAT=wav)
	python -m src convert $(INPUT) $(OUTPUT) --format $(FORMAT)

extract-audio: ## Extract audio from video (usage: make extract-audio INPUT=video.mp4 OUTPUT=audio.mp3)
	python -m src extract-audio $(INPUT) $(OUTPUT)

resize: ## Resize image (usage: make resize INPUT=image.jpg OUTPUT=resized.jpg WIDTH=800 HEIGHT=600)
	python -m src resize $(INPUT) $(OUTPUT) --width $(WIDTH) --height $(HEIGHT)

info: ## Get file info (usage: make info FILE=file.mp3)
	python -m src info $(FILE)

formats: ## Show supported formats
	python -m src formats

setup-dev: ## Setup development environment
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install -e ".[dev]"
	mkdir -p uploads converted temp logs
	chmod 755 uploads converted temp logs

production: ## Start production server
	gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 300 src.wsgi:app
