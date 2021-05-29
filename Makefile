.PHONY: deploy test-list_dags

include .env

deploy:
	gcloud composer environments storage dags import \
		--project $(PROJECT_ID) \
		--environment $(ENVIRONMENT_NAME) \
		--location $(LOCATION) \
		--source=./composer_sandbox \
		--destination=data/test

test-list_dags:
	gcloud composer environments storage data import \
		--project $(PROJECT_ID) \
		--environment $(ENVIRONMENT_NAME) \
		--location $(LOCATION) \
		--source=./composer_sandbox \
		--destination=test

	gcloud composer environments run $(ENVIRONMENT_NAME) \
		--project $(PROJECT_ID) \
		--location $(LOCATION) \
		list_dags -- -sd /home/airflow/gcs/data/test

test-dagloader:
	python ./composer_sandbox/dag-sample.py