from cogs.login_gui import App
from cogs import secretvars

app = App()
app.mainloop()

secretvars.MAIN_FLAG = 0
if len(secretvars.Thread_Pool):
    for i in secretvars.Thread_Pool:
        print("Thread Terminated")
        i.join()


# {
#     "officeId": 1,
#     "tripDate": "2024-04-30",
#     "tripDestination": "roma",
#     "termandcond": true,
#     "idServiceLevel": 1,
#     "applicants": [
#         {
#             "owner": true,
#             "visaId": 20,
#             "name": "abdo",
#             "surname": "allam",
#             "birthDate": "2024-04-24",
#             "gender": "M",
#             "nationality": "EGY",
#             "residenceAddress": "menofia",
#             "residenceCountry": "EGY",
#             "passportNumber": "A35530496",
#             "passportIssuingState": "EGY",
#             "passportDateOfIssue": "2024-04-24",
#             "passportDateOfExpiry": "2024-05-30",
#             "phoneNumber": "+201010990178",
#             "email": "b3aa019163@emailbbox.pro",
#             "documents": [
#                 {
#                     "documentTypeId": 100,
#                     "temporaryKey": "Tmp/IDX_1713947973121_3922067/WhatsApp Image 2024-04-17 at 10.29.25_1ac455b5.jpg",
#                     "fileName": "WhatsApp Image 2024-04-17 at 10.29.25_1ac455b5.jpg",
#                     "fileSize": 12632,
#                     "mimeType": "image/jpeg",
#                 }
#             ],
#             "services": [],
#         }
#     ],
#     "slotStartDate": "2024-05-15T13:00:00+02:00",
#     "source": "WEB",
#     "otp": "121511",
# }
