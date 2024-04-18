from pathlib import Path

from google.cloud import storage

from airflow.models import Variable


GCP_CREDENTIALS_FILE_PATH = Variable.get("GCP_CREDENTIALS_FILE_PATH")
GCP_PROJECT_ID = Variable.get('GCP_PROJECT_ID')
BUCKET_NAME = Variable.get('BUCKET_NAME')
BUCKET_CLASS = Variable.get('BUCKET_CLASS')
BUCKET_LOCATION = Variable.get('BUCKET_LOCATION')

class GCSTools():
    def __init__(self, credentials_file=GCP_CREDENTIALS_FILE_PATH):
        self.client = storage.Client.from_service_account_json(credentials_file)

    def info(self):
        print(f"This is a GCSTools with gcp_credentials_file locates in {GCP_CREDENTIALS_FILE_PATH}")

    def list_buckets(self):
        """ Lists all buckets. """
        for bucket in self.client.list_buckets():
            print(bucket.name)
    
    def create_bucket(self, bucket_name):
        bucket = self.client.bucket(bucket_name)
        bucket.storage_class = BUCKET_CLASS
        new_bucket = self.client.create_bucket(bucket, location=BUCKET_LOCATION)

        print(f"Created bucket {new_bucket.name} in {new_bucket.location} with storage class {new_bucket.storage_class}")
        
        return new_bucket


class GCSBucket(GCSTools):
    def __init__(self, bucket_name=BUCKET_NAME, credentials_file=GCP_CREDENTIALS_FILE_PATH):
        super().__init__(credentials_file)
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)
    
    def info(self):
        print(f"This is a GCSBucket under GCSTools with bucket name: {self.bucket_name}")
    
    def set_bucket_name(self, name):
        """ Change the target bucket """
        self.bucket_name = name
        self.bucket = self.client.bucket(name)
    
    def upload_file(self, local_file_path, remote_file_name):
        """ Upload the file to self.bucket """
        blob = self.bucket.blob(remote_file_name)
        blob.upload_from_filename(local_file_path)
        print(f"File {local_file_path} uploaded to gs://{self.bucket_name}/{remote_file_name}")

    def upload_directory(self, source_directory, prefix):
        # First, recursively get all files in `directory` as Path objects.
        directory_as_path_obj = Path(source_directory)
        paths = directory_as_path_obj.rglob("*")

        # Filter so the list only includes files, not directories themselves.
        file_paths = [path for path in paths if path.is_file()]

        # These paths are relative to the current working directory. Next, make them
        # relative to `directory`
        relative_paths = [path.relative_to(source_directory) for path in file_paths]

        # Finally, convert them all to strings.
        string_paths = [f"{prefix}/{str(path)}" for path in relative_paths]

        print(f"Found {len(string_paths)} files.")

        # Start the upload.
        for local_file_path, remote_file_name in zip(file_paths, string_paths):
            self.upload_file(local_file_path, remote_file_name)

