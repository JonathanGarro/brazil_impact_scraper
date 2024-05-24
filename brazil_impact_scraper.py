import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime
import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def lambda_handler(event, context):
    """
    AWS Lambda handler function to scrape data from a specified webpage, extract relevant information,
    and append it to a CSV file stored in an S3 bucket.

    This function performs the following steps:
    1. Sends a GET request to the specified webpage URL.
    2. Parses the HTML content using BeautifulSoup.
    3. Extracts specific numeric data related to the current status of municipalities, shelters, displaced people, affected people, injuries, missing persons, confirmed deaths, and rescues.
    4. Appends the extracted data, along with the current datetime, to a CSV file stored in the /tmp directory.
    5. Uploads the updated CSV file to a specified S3 bucket.

    Parameters:
    event (dict): AWS Lambda event data (not used in this function).
    context (object): AWS Lambda context object (not used in this function).

    Returns:
    dict: A dictionary containing the status code and a message indicating the result of the operation.

    Raises:
    Exception: If the webpage cannot be retrieved, the function returns an error message with the status code.
    """
    
    url = "https://defesacivil.rs.gov.br/defesa-civil-atualiza-balanco-das-enchentes-no-rs-22-5-18h-664f353266e07"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        def get_number_after_label(label):
            label_text = f"{label}:"
            element = soup.find(string=lambda text: text and label_text in text)
            if element:
                parent = element.parent
                text = parent.get_text()
                match = re.search(rf"{label_text}\s*([\d.,]+)", text)
                if match:
                    number = match.group(1).replace('.', ',')
                    return number
            return "Not found"
        
        municipios_afetados = get_number_after_label("Municípios afetados")
        pessoas_em_abrigos = get_number_after_label("Pessoas em abrigos")
        desalojados = get_number_after_label("Desalojados")
        afetados = get_number_after_label("Afetados")
        feridos = get_number_after_label("Feridos")
        desaparaceidos = get_number_after_label("Desaparecidos")
        obitos = get_number_after_label("Óbitos confirmados")
        pessoas_resgatadas = get_number_after_label("Pessoas resgatadas")
        
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data = [
            current_datetime,
            municipios_afetados,
            pessoas_em_abrigos,
            desalojados,
            afetados,
            feridos,
            desaparaceidos,
            obitos,
            pessoas_resgatadas
        ]
        
        csv_file = "/tmp/defesa_civil_data.csv" 
        bucket_name = os.environ.get('bucket_name')
        s3_key = 'defesa_civil_data.csv'
        
        s3_client = boto3.client('s3')
        
        # check if the file exists in the bucket
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            file_exists = True
            s3_client.download_file(bucket_name, s3_key, csv_file)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                file_exists = False
            else:
                raise
        
        header = [
            "Datetime",
            "Municipalities affected",
            "People in shelters",
            "Displaced",
            "Affected",
            "Injured",
            "Missing",
            "Dead",
            "Rescued"
        ]
        
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(data)
            
        s3_client.upload_file(csv_file, bucket_name, s3_key)
        
        print(f"Municipalities affected: {municipios_afetados}")
        print(f"People in shelters: {pessoas_em_abrigos}")
        print(f"Displaced: {desalojados}")
        print(f"Affected: {afetados}")
        print(f"Injured: {feridos}")
        print(f"Missing: {desaparaceidos}")
        print(f"Dead: {obitos}")
        print(f"Rescued: {pessoas_resgatadas}")
        
        return {
            'statusCode': 200,
            'body': 'CSV file updated and uploaded to S3 successfully.'
        }
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return {
            'statusCode': response.status_code,
            'body': 'Failed to retrieve the webpage.'
        }