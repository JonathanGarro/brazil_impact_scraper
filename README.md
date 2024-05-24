# Web Scraper for Brazil Floods (2024) with AWS Lambda Integration

A web scraper that crawls the [Defesa Civil website](https://defesacivil.rs.gov.br/defesa-civil-atualiza-balanco-das-enchentes-no-rs-22-5-18h-664f353266e07), where the Brazilian government is posting daily updates on a number of key impact indicators.

## Prerequisites

This tool is designed to be zipped and uploaded as an AWS Lambda function. I have it triggered by CloudWatch every few hours to account for the update frequency proposed by the ministry of two to three times a day.

To run this in the same way I have it set up in production, you will need:

- An AWS account
- An S3 bucket to store the output CSV
- An AWS Lambda instance configured with IAM permissions
- A CloudWatch rule designed to trigger the script

## Configuration

You'll need to create an S3 bucket. Do not make it publicly accessible! Use IAM permissions to grant specific S3 admin access only for this tool. Save the name of the bucket in a .env file and take advantage of the load_dotenv() function if testing locally or sharing with colleagues. If you're ready to put it into AWS, you can hard code the bucket name.

Install your dependencies:

`pip install requests beautifulsoup4 boto3 python-dotenv -t .`

Zip the file with:

`zip -r lambda_function.zip . `

Create a new Lambda function in AWS using the "Author from Scratch" option. Select Python as the engine and upload the `lambda_function.py` zip file. 

Set up your permissions in IAM with a new role that includes `AmazonS3FullAccess`. Alternatively, you can create a custom policy with Get, Put, and List permissions on s3.

Configure CloudWatch by creating a new rule, using the "Schedule" option and configure it to run as frequently as you need.