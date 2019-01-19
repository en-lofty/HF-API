from endpoints.base import BaseEndpoint
from utilities.logger import log


class PrivateMessageEndpoint(BaseEndpoint):
    def __init__(self):
        self.endpoint = "inbox"
        if "inbox" not in super().data:
            super().save_data()

    def update(self):
        super().update()
        response = super().api_query()
        if not response:
            return
        pms = response["result"]
        current_id = pms['pms'][0]["pmid"]
        try:
            last_id = self.json["inbox"]["pmid"]
        except Exception as e:
            self.json["inbox"].update({"pmid": current_id})
            super().save_data()
            return
        self.json["inbox"] = {"pmid": current_id}
        if not current_id == last_id:
            super().pb.push_note("HackForums Alert",
                                 "New Private Message from {}".format(pms["pms"][0]["senderusername"]))
            log(f"New Private message from {pms['pms'][0]['senderusername']}")
            self.json["inbox"].update("pmid", current_id)
            super().save_data()
