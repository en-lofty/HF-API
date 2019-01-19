from endpoints.base import BaseEndpoint
from utilities.logger import log


class ThreadEndpoint(BaseEndpoint):

    def __init__(self):
        self.endpoint = "thread"
        self.thread_list = ["5930716"]
        if "threads" not in super().data:
            super().save_data()

    def update(self):
        super().update()
        # grab current data
        json_data = super().data
        # loop through thread list and update the thread counts
        for ID in self.thread_list:
            if ID not in json_data["threads"]:
                super().data["threads"][ID] = 0
                super().save_data()
                continue
            # make the api call and collect data
            response = super().api_query(ID)
            if not response:
                return
            result = response["result"]
            # get the current number of replies
            current_count = result['numreplies']
            old_count = json_data["threads"][ID]
            if current_count > old_count:
                # todo add reply content
                log(f"Thread ID {ID}: New reply.")
                super().pb.push_note("New Thread Reply", "https://hackforums.net/showthread.php?tid=" + ID)
                # update our data to reflect current reply count
                super().data["threads"][ID] = current_count
                super().save_data()
