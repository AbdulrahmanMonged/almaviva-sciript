class Applicant:
    def __init__(
        self,
        birthDate,
        gender,
        residenceAddress,
        passportNumber,
        passportDateOfIssue,
        passportDateOfExpiry,
        visa_id,
    ):
        self.name = ""
        self.surname = ""
        self.birthDate = birthDate
        self.gender = gender
        self.residenceAddress = residenceAddress
        self.passportNumber = passportNumber
        self.passportDateOfIssue = passportDateOfIssue
        self.passportDateOfExpiry = passportDateOfExpiry
        self.phoneNumber = ""
        self.email = ""
        self.visa_id = visa_id
        self.documents = []
        self.bot = None

    def set_new_data(self, incoming_data):
        self.name = incoming_data["name"]
        self.surname = incoming_data["family_name"]
        self.email = incoming_data["email"]
        self.phoneNumber = incoming_data["phone"]

    def set_bot(self, bot):
        self.bot = bot

    def add_document(self, doc):
        self.documents.append(doc)
    
    def remove_documents(self):
        self.documents = []
    
    def set_passport_number(self, passportNumber):
        self.passportNumber = passportNumber

    def get_phone_number(self):
        return self.phoneNumber
    
    def get_applicant_json(self):
        try:
            return {
                "owner": True,
                "visaId": self.visa_id,
                "name": self.name,
                "surname": self.surname,
                "birthDate": self.birthDate,
                "gender": self.gender,
                "nationality": "EGY",
                "residenceAddress": self.residenceAddress,
                "residenceCountry": "EGY",
                "passportNumber": self.passportNumber,
                "passportIssuingState": "EGY",
                "passportDateOfIssue": self.passportDateOfIssue,
                "passportDateOfExpiry": self.passportDateOfExpiry,
                "phoneNumber": self.phoneNumber,
                "email": self.email,
                "services": [],
                "documents": [doc.get_document_json() for doc in self.documents],
            }
        except Exception as e:
            print("Error while trying to get the applicant json: ", e)
