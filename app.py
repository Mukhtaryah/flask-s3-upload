from flask import Flask, request
import boto3
import os
from botocore.client import Config
from datetime import datetime

app = Flask(__name__)

# Configure S3 client with environment variables
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='eu-north-1',
    endpoint_url='https://s3.eu-north-1.amazonaws.com',
    config=Config(signature_version='s3v4')
)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        campaign_id = request.form['campaign_id']
        if file and campaign_id:
            # Add timestamp to filename to prevent overwriting
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3.upload_fileobj(file, 'your-dverse-wallet-uploads', f'wallet_addresses_{campaign_id}_{timestamp}.csv')
            # Trigger script with campaign_id (script doesn't exist yet, we'll create it later)
            os.system(f"python wallet_script.py {campaign_id}")
            return "File uploaded successfully!"
    return '''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Upload Wallet Addresses</title>
    </head>
    <body>
      <h1>Upload Wallet Addresses CSV</h1>
      <form method="POST" enctype="multipart/form-data">
        <label for="campaign_id">Campaign ID:</label>
        <input type="text" name="campaign_id" placeholder="Enter Campaign ID (e.g., campaign_1)" required>
        <br><br>
        <label for="file">Select CSV File:</label>
        <input type="file" name="file" accept=".csv" required>
        <br><br>
        <input type="submit" value="Upload">
      </form>
    </body>
    </html>
    '''
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
