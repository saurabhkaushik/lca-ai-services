from google.cloud import storage
import os 

class GCP_Storage(object): 
    storage_client = None

    model_folder = './model/'
    seed_folder = './data/'
    model_bucket = 'lca_model'
    seed_bucket = 'lca_seed'

    domains = []

    def __init__(self, domains):
        self.domains = domains
        self.storage_client = storage.Client()
        pass

    def setup_bucket(self):
        storage_client = storage.Client()
        if not storage_client.bucket(self.seed_bucket).exists():
            bucket = storage_client.create_bucket(self.seed_bucket)
            print(f"Bucket {bucket.name} created.")
        if not storage_client.bucket(self.model_bucket).exists():
            bucket = storage_client.create_bucket(self.model_bucket)
            print(f"Bucket {bucket.name} created.")
        return None
    
    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print(f"File {source_file_name} uploaded to {destination_blob_name}.")
        return blob.public_url

    def download_blob(self, bucket_name, source_blob_name, destination_file_name):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        contents = blob.download_as_string()
        print("Downloaded storage object {} from bucket {} to local file {}.".format(
                source_blob_name, bucket_name, destination_file_name
            )
        )
        return contents
    
    def download_models(self):      
        print ('Downloading Models from GCP Bucket.')  
        for domain in self.domains: 
            dest_folder = self.model_folder + domain + '/'
            try: 
                os.makedirs(dest_folder) 
            except OSError as error: 
                print(error) 

        blobs = self.storage_client.list_blobs(self.model_bucket)

        for blob in blobs:                           
            dest_file_url = self.model_folder + blob.name               
            print (self.model_bucket, blob.name, dest_file_url)
            self.download_blob(self.model_bucket, blob.name, dest_file_url)
        return 

    def upload_models(self):     
        print ('Uploading Models to GCP Bucket.')    
        for domain in self.domains: 
            model_domain_folder = self.model_folder + domain + '/'
            filelist = os.listdir(model_domain_folder)            
            for file_name in filelist: 
                src_file_url = model_domain_folder + file_name 
                file_name = domain + '/' + file_name
                self.upload_blob(self.model_bucket, src_file_url, file_name)
                print(f"Uploaded {file_name}.")
    
    def download_seed_data(self):   
        print ('Downloading Seeds from GCP Bucket.')     
        blobs = self.storage_client.list_blobs(self.seed_bucket)
        try: 
            os.makedirs(self.seed_folder) 
        except OSError as error: 
            print(error) 
        for blob in blobs:          
            dest_file_url = self.seed_folder + blob.name 
            self.download_blob(self.seed_bucket, blob.name, dest_file_url)

    def upload_seed_data(self):      
        print ('Uploading Seeds to GCP Bucket.')  
        filelist = os.listdir(self.seed_folder)            
        for file_name in filelist: 
            if file_name.endswith(".csv"):
                src_file_url = self.seed_folder + file_name 
                self.upload_blob(self.seed_bucket, src_file_url, file_name)
                print(f"Uploaded {file_name}.") 
