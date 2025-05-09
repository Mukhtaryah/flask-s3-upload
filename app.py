from flask import Flask, render_template_string
import boto3
from botocore.client import Config
import os

app = Flask(__name__)

# AWS S3 client setup
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='eu-north-1',
    endpoint_url='https://s3.eu-north-1.amazonaws.com',
    config=Config(signature_version='s3v4')
)

# HTML template for the upload page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload CSV to S3</title>
</head>
<body>
    <h2>Upload Your CSV File</h2>
    <form action="{{ post_url }}" method="POST" enctype="multipart/form-data" onsubmit="alert('Upload initiated. If successful, you will see the file in the S3 bucket.');">
        <input type="hidden" name="acl" value="{{ fields['acl'] }}">
        <input type="hidden" name="Content-Type" value="{{ fields['Content-Type'] }}">
        <input type="hidden" name="key" value="{{ fields['key'] }}">
        <input type="hidden" name="x-amz-algorithm" value="{{ fields['x-amz-algorithm'] }}">
        <input type="hidden" name="x-amz-credential" value="{{ fields['x-amz-credential'] }}">
        <input type="hidden" name="x-amz-date" value="{{ fields['x-amz-date'] }}">
        <input type="hidden" name="policy" value="{{ fields['policy'] }}">
        <input type="hidden" name="x-amz-signature" value="{{ fields['x-amz-signature'] }}">
        <input type="file" name="file" accept=".csv">
        <input type="submit" value="Upload">
    </form>
    <p>The URL expires in 1 hour. Refresh the page to get a new URL if needed.</p>
</body>
</html>
"""

@app.route('/')
def upload_page():
    # Generate a pre-signed POST URL
    bucket_name = 'your-dverse-wallet-uploads'
    fields = {
        "acl": "private",
        "Content-Type": "text/csv",
        "key": "client_upload_${filename}"  # Allows dynamic file names
    }
    conditions = [
        {"acl": "private"},
        {"Content-Type": "text/csv"},
        ["starts-with", "$key", "client_upload_"]
    ]

    post_url_data = s3.generate_presigned_post(
        Bucket=bucket_name,
        Key='client_upload_${filename}',
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600  # 1 hour expiry
    )

    return render_template_string(
        HTML_TEMPLATE,
        post_url=post_url_data['url'],
        fields=post_url_data['fields']
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
