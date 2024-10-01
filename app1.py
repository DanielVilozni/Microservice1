from flask import Flask, request, jsonify
import boto3
import os

app = Flask(__name__)

# Initialize AWS clients for SQS and SSM (to retrieve the token)
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')

# SQS queue URL and SSM parameter name for token
QUEUE_URL = os.getenv('QUEUE_URL')  # Set this environment variable
SSM_TOKEN_PARAM = os.getenv('SSM_TOKEN_PARAM', '/myapp/token')

# Function to retrieve the token from SSM Parameter Store
def get_token_from_ssm():
    response = ssm.get_parameter(Name=SSM_TOKEN_PARAM, WithDecryption=True)
    return response['Parameter']['Value']

# Function to validate the token
def validate_token(request_token):
    stored_token = get_token_from_ssm()
    return request_token == stored_token

# Route to receive the POST request
@app.route('/publish', methods=['POST'])
def publish_message():
    data = request.json

    # Validate the token
    token = data.get('token')
    if not validate_token(token):
        return jsonify({"error": "Invalid token"}), 403

    # Validate the email data
    email_data = data.get('data')
    if not all(field in email_data for field in ['email_subject', 'email_sender', 'email_timestream', 'email_content']):
        return jsonify({"error": "Invalid payload"}), 400

    # Send the message to SQS
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=str(email_data)
    )

    return jsonify({"message": "Message published to SQS"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
