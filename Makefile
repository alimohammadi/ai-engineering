run-docker-compose:
	uv sync 
	docker compose up --build -d

clean-notebook-outputs:
	jupyter nbconvert --clear-output --inplace notebooks/*/*.ipynb


run-evals-retriever:
	uv sync 
	PYTHONPATH="$(PWD)/apps/api:$(PWD)/apps/api/src:${PYTHONPATH}:$(PWD)" uv run --env-file .env python3 -m evals.evals_retriever