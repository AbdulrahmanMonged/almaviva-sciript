import os
import requests


class Document:

    def __init__(self, doc_id, file_path):
        self.doc_id = doc_id
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.mime_type = f"image/{self.file_name.split('.')[-1]}"
        if self.file_name.split(".")[-1] == "jpg":
            self.mime_type = "image/jpeg"
        elif self.file_name.split(".")[-1] == "pdf":
            self.mime_type = "application/pdf"
        self.presignedUrl = ""
        self.temporaryKey = ""
        self.applicant = None

    def set_applicant(self, applicant):
        self.applicant = applicant

    def set_presigned_url(self, presigned_url):
        self.presignedUrl = presigned_url

    def set_temporary_key(self, temporary_key):
        self.temporaryKey = temporary_key

    def get_document_json(self):
        try:
            return {
                "documentTypeId": self.doc_id,
                "temporaryKey": self.temporaryKey,
                "fileName": self.file_name,
                "fileSize": self.file_size,
                "mimeType": self.mime_type,
            }
        except Exception as e:
            pass

    def get_presigned_url_json(self):
        try:
            return {
                "fileSize": self.file_size,
                "fileName": self.file_name,
                "mimeType": self.mime_type,
            }
        except Exception as e:
            pass

    def send_presigned_url_request(self, token):
        try:
            api_url = "https://egyapi.almaviva-visa.it/reservation-manager//api/documents/v1/upload-presigned-url"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            }
            data = self.get_presigned_url_json()
            response = requests.post(api_url, headers=headers, json=data)
            if response and response.status_code in [200, 201, 202, 203, 204]:
                self.set_presigned_url(response.json()["presignedUrl"])
                self.set_temporary_key(response.json()["temporaryKey"])
                return True
            return False
        except Exception as e:
            return False

    def send_put_request(self):
        try:
            api_url = self.presignedUrl
            with open(self.file_path, "rb") as file:
                headers = {
                    "Content-Type": self.mime_type,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Origin": "https://egy.almaviva-visa.it",
                    "Referer": "https://egy.almaviva-visa.it/",
                    "Host": "visasys.s3.eu-west-1.amazonaws.com",
                }
                response = requests.put(api_url, headers=headers, data=file)
                if response and response.status_code in [200, 201, 202, 203, 204]:
                    return True
                return False
        except Exception as e:
            return False

    def upload_document(self, token):
        try:
            count = 0
            while not self.presignedUrl and count < 3:
                self.send_presigned_url_request(token)
                count += 1
            if not self.presignedUrl:
                return False
            count = 0
            uploaded = False
            while not uploaded and count < 3:
                uploaded = self.send_put_request()
                count += 1
            if not uploaded:
                return False
            return True
        except Exception as e:
            return False
