import uuid

def get_or_create_lead_key(request):
    key = request.session.get("lead_idemp")
    if not key:
        key = uuid.uuid4().hex
        request.session["lead_idemp"] = key
    return key