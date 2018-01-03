#!/usr/bin/env bash

aws iot create-job \
  --job-id "$1" \
  --targets \
    "$(aws iot list-things \
      --query 'things[?contains(thingName,`ota-update-thing`)].thingArn' \
      --output "text")" \
  --document-source \
    "https://$(aws s3api list-buckets \
      --query 'Buckets[?contains(Name,`ota-firmwarebucket`)].Name' \
      --output "text").s3.ap-northeast-1.amazonaws.com/job-document.json" \
  --presigned-url-config \
    roleArn="$(aws iam list-roles \
      --query 'Roles[?contains(RoleName,`ota-IoTJobRole`)].Arn' \
      --output "text")",expiresInSec=1800 \
  --job-executions-rollout-config maximumPerMinute=1000
