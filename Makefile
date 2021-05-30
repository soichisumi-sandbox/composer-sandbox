.PHONY: deploy test-list_dags

include .env

DESTINATION=soichisumi-sandbox/
#DESTINATION=test

deploy:
	gcloud composer environments storage dags import \
	--project $(PROJECT_ID) \
	--environment $(ENVIRONMENT_NAME) \
	--location $(LOCATION) \
	--source=./composer_sandbox \
	--destination=$(DESTINATION)

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


## run test は dagrun_conf非対応のため使えない
test-tasktest:
	gcloud composer environments storage data import \
		--project $(PROJECT_ID) \
		--environment $(ENVIRONMENT_NAME) \
		--location $(LOCATION) \
		--source=./composer_sandbox \
		--destination=test

	gcloud composer environments run $(ENVIRONMENT_NAME) \
		--project $(PROJECT_ID) \
		--location $(LOCATION) \
		test -- -sd /home/airflow/gcs/data/test dag_sample_w_template hello 2000-01-01

	gcloud composer environments run $(ENVIRONMENT_NAME) \
		--project $(PROJECT_ID) \
		--location $(LOCATION) \
		test -- -sd /home/airflow/gcs/data/test dag_sample_w_template yo 2000-01-01 -c '{"key":"value"}'

	gcloud composer environments run $(ENVIRONMENT_NAME) \
		--project $(PROJECT_ID) \
		--location $(LOCATION) \
		test -- -sd /home/airflow/gcs/data/test dag_sample_w_template bye 2000-01-01

test-dagloader:
	python ./composer_sandbox/dag-sample.py

test-dag:
	pytest


trigger-dag:
	gcloud composer environments storage dags import \
		--project $(PROJECT_ID) \
		--environment $(ENVIRONMENT_NAME) \
		--location $(LOCATION) \
		--source=./composer_sandbox \
		--destination=$(DESTINATION)
	gcloud composer environments run $(ENVIRONMENT_NAME) \
		--project $(PROJECT_ID) \
		--location $(LOCATION) \
		trigger_dag -- --conf '{"key": "val", "num": 1}' dag_sample_w_template