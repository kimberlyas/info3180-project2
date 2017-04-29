import smtplib


def sendemail(to_addr,from_addr,from_name,subject,msg):
    to_name = 'My favorite person via WishList Inc.'
    
    message = """From: {} <{}>\nTo: {} <{}>\nSubject: {}\n\n{}"""
    # Format message to be sent
    message_to_send = message.format(from_name, from_addr, to_name,
                                     to_addr, subject, msg)
    
    # Credentials (if needed)
    username = 'wishlistservice@gmail.com'
    password = 'jpemcvauomqjffsk'

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(from_addr, to_addr, message_to_send)
    server.quit()
    
    return