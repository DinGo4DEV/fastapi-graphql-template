from app.models.event import CreateEvent, UpdateEvent



class BaseManager:
    @staticmethod
    def create_event_from_arango_result(result,author,operation_type="unknow"):
        new = result.get("new",{})
        old = result.get("old",None)
        operation_type = result.get("type",operation_type)
        if operation_type == "insert":                        
            event = CreateEvent(author=author,new=new)                        
        else: 
            event = UpdateEvent(author=author,new=new,old=old)
        return event