import firebase_admin

from firebase_admin import messaging
from accounts.models import *




def notification(user_id,title,body,project_name):
   
    app = firebase_admin.get_app(name=project_name)
    token = Send_Notification.objects.filter(user=user_id).values('device_token').get()['device_token']
  
 
    # Notification message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token = token
    )
 
    # Send the message
    
    response = messaging.send(message,app=app)
    print("jjjj",response)
    # Notification.objects.create(user=CustomUser.objects.get(id=user_id),device_token=token,title=title,body=body)