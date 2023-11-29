// Building the environnement for AWS BACKUP the lambda function for the webhook to slack, the sns topic and the 

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Location = "Paris"
      Client   = "Claranet"

    }
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }
  }
  required_version = "~> 1.5"
  backend "s3" {
  bucket = "s3-awsbackup-tfstate"
  key    = "athena-report/daily-job-report.tfstate"
  region = "eu-west-1"
  } 
}

data "aws_caller_identity" "current" {}

data "aws_kms_key" "aws-backup-key" {
  key_id = "alias/aws/backup"
}

data "aws_kms_key" "aws-sns-key" {
  key_id = "alias/aws/sns"
}

/*
module "sns_topic" {
  source = "git@ssh.dev.azure.com:v3/lpl-sources/Terraform/mod-aws-sns-topic?ref=1.1.0"

  auto_tag_name = true
  //    display_name    = "aws-backup-minisites-nonprod"
  //  kms_key         = data.aws_kms_key.aws-sns-key.key_id
  name         = var.name
  project_name = var.project_name
  region       = var.region
  stack_name   = "SUPPORT"
  tags = {
    Environment = var.env
    Project     = "topic-leader-backup"
    Role        = "backup"
  }
}
*/

//    Allow lambda to use sts assume role
# Allow lambda to use sts assume role

resource "aws_iam_role" "lambda_role_athena_query" {
  name = "role_lambda_athena_report"

  assume_role_policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Action": "sts:AssumeRole",
			"Principal": {
			"Service": "lambda.amazonaws.com"
		},
		"Effect": "Allow",
		"Sid": ""
		}
	]
  }
EOF
}



# Define the policy to create a logstream in cloudwatch
resource "aws_iam_policy" "lambda_policy_athena_query" {
  name   = "lambda_policy_athena_query"
  path   = "/"
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:*:*:*"
            ],
            "Effect": "Allow",
            "Sid": "logsclaranet"
        }
    ]
}
EOF
}
# attach the previous to a role (i)
resource "aws_iam_role_policy_attachment" "role_lambda_athena_query" {
  role       = aws_iam_role.lambda_role_athena_query.name
  policy_arn = aws_iam_policy.lambda_policy_athena_query.arn
}

resource "aws_lambda_function" "athena_query" {
  filename      = "../my_function/my_deployment_package.zip"
  function_name = "athena_query"
  role          = aws_iam_role.lambda_role_athena_query.arn
  handler       = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("../my_function/my_deployment_package.zip")
  runtime          = "python3.11"
  timeout          = 900
}
# Definition of the event bridge
resource "aws_cloudwatch_event_rule" "every-start-of-day-athena-query" {
    name = "every-start-of-day-athena-query"
    description = "fired very day at 10:45 am"
    schedule_expression = "cron(45 10 ? * MON-FRI *)"
}

# Definition of the Cloudwatch Target
resource "aws_cloudwatch_event_target" "check-every-start-of-day-rds" {
    rule = "${aws_cloudwatch_event_rule.every-start-of-day-athena-query.name}"
    target_id = "athena_query"
    arn = "${aws_lambda_function.athena_query.arn}"
}

resource "aws_lambda_permission" "allow-cloudwatch-to-call-athena_query" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.athena_query.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.every-start-of-day-athena-query.arn}"
}
