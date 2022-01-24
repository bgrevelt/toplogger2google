import requests
from datetime import datetime

class TopLogger:
    GYM_ID = 11  # Energiehaven
    RESERVATION_AREA = 15  # Bouldering
    URL_API = "https://api.toplogger.nu"
    URL_SIGN_IN = URL_API + "/users/sign_in.json"
    URL_SIGN_OUT = URL_API + "/users/sign_out.json"
    URL_SLOTS = URL_API + "/v1/gyms/%i/slots?date=%s&reservation_area_id=%i&slim=true"
    URL_RESERVATIONS = URL_API + "/v1/reservations"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self):
        self.request_headers = None

    def login(self, username, password):
        payload = {"user": {"email": username, "password": password}}

        try:
            r = requests.post(self.URL_SIGN_IN, json=payload)
        except Exception as e:
            raise (e)

        token = r.json()['authentication_token']
        userid = r.json()['user_id']
        self.request_headers = {"x-user-email": username, "x-user-token": token}

    def logout(self):
        if not self.request_headers:
            print("Not logged in")
            return
        r = requests.delete(self.URL_SIGN_OUT)

    # Return raw JSON data from slots API.
    def slots(self, date):
        if not self.request_headers:
            print("Not logged in")
            return
        r = requests.get(self.URL_SLOTS % (self.GYM_ID, date.strftime(self.DATE_FORMAT), self.RESERVATION_AREA),
                         headers=self.request_headers)
        return r.json()

    def reservations(self, include_expired=False):
        if not self.request_headers:
            print("Not logged in")
            return
        r = requests.get(self.URL_RESERVATIONS, headers=self.request_headers)
        if include_expired:
            return r.json()
        else:
            non_expireds = []
            now = datetime.utcnow()
            for reservation in r.json():
                start = datetime.fromisoformat(reservation['slot_start_at'][:-1]) # drop the 'Z' that indicates UTC from the timestamp string. fromisoformat doesnt like it.
                if start > now:
                    non_expireds.append(reservation)
            return non_expireds

