from pyDataverse.api import Api

def download_dataset(doi):
    # Initialize the API with the base URL of your Dataverse instance
    api = Api('https://dataverse.no', 'YOUR_API_TOKEN')  # Replace with your actual API token

    # Get the dataset using the DOI
    dataset = api.get_dataset(doi)

    if dataset['status'] == 'OK':
        # Extract the files from the dataset
        files = dataset['data']['latestVersion']['files']
        
        for file in files:
            file_id = file['dataFile']['id']
            file_name = file['dataFile']['filename']
            print(f"Downloading {file_name}...")

            # Download the file
            response = api.download_file(file_id)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                print(f"{file_name} downloaded successfully.")
            else:
                print(f"Failed to download {file_name}. Status code: {response.status_code}")
    else:
        print(f"Failed to retrieve dataset. Status: {dataset['status']}")

if __name__ == "__main__":
    doi = "doi:10.18710/CHMWOB"  # The DOI of the dataset
    download_dataset(doi)
