IMAGE_NAME=juiz-slack-bot-with-env
AWS_ACCOUNT_ID=248189937351
AWS_REGION=ap-northeast-1
REPO_NAME=juiz

push:
	docker build -t $(IMAGE_NAME) . && \
	docker tag $(IMAGE_NAME):latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPO_NAME):latest && \
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPO_NAME):latest

run:
	docker run --rm -p 8080:8080 $(IMAGE_NAME)

.PHONY: build run tag push
