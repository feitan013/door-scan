
from twilio.rest import Client

account_sid = 'ACbc32834ae072b569582faf8f5d3e20d7'
auth_token = 'b07e4801f29117aa73e06cf19d6ebcdc'
client = Client(account_sid, auth_token)

message = client.messages.create(
    body="Access Denied! Someone is at the door.",
    from_='+639383196822',  # Replace with your Twilio phone number
    to='+639311496096'
)


print(message.sid)