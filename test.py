import io
import json
import os
os.chdir("Z:\Drive condivisi\Tesi\File progetto\TEST SCRIPTS")

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def getPermission(user, intent_name):
    # 1. Read file contents
    with open('permissions.json', "r") as file:
        permission_list = json.load(file)

    permission_status = True
    logging.info(permission_list)
    for p in permission_list:
        if p['username'] == user and p['intent_command'] == intent_name:
            permission_status = False
    return permission_status

def getPermissionList(user):
    # 1. Read file contents
    with open('permissions.json', "r") as file:
        permission_list = json.load(file)
    logging.info(permission_list)
    permissions_user = []
    for p in permission_list:
        if p['username'] == user:
            permissions_user.append(p['intent_command'])
    return permissions_user 

import requests
def send_request(url, command):
      parameters = {'q': command}
      r = requests.get(url = url, params = parameters)
      data = r.json()
      # intent_name , probability, slots
      return data[0], data[1], data[2]     



def main():
    command = "nicola is denied to call help"

    #ngrok_url = input("Please insert ngrok url: ")
        
    # intent_name, probability, list_slot = load_and_parse("persistent_engine_permissions", command)
    # intent_name2, probability2, list_slot2 = load_and_parse("persistent_engine_commands", command)

    ngrok_url = "http://ed70-34-91-30-169.ngrok.io/"

    url_pec = ngrok_url+"/engine/commands"
    url_pep = ngrok_url+"/engine/permissions"

    intent_name, probability, list_slot = send_request(url_pep, command)
    logging.info("PEP: intent = "+str(intent_name))
    intent_name2, probability2, list_slot2 = send_request(url_pec, command)
    logging.info("PEC: intent = "+str(intent_name2))
        


    choice = None
    if (probability > probability2):
        logging.info("Command type: PERMISSION with intent: "+intent_name)
        choice = 1
    else: 
        logging.info("Command type: SIMPLE COMMAND with intent: "+intent_name2)
        choice = 2

    # Uscita con errore se si vogliono svolgere azioni da admin ma si è utenti semplici ('user').

    if choice == 1:
        if (intent_name == "setPermissionNo"):
            user_from_slot = list_slot[0]["rawValue"]
            command_from_slot = list_slot[1]["rawValue"]
            # 1. Read file contents
            with open('permissions.json', "r") as file:
                permission_list = json.load(file)

            logging.info(permission_list)
            
            # intent_name3 = load_and_parse("persistent_engine_commands", command_from_slot)[0]   # Return only the first value
            intent_name3, _ , list_slot3 = send_request(url_pec, command_from_slot)
            print("Intent name is "+ str(intent_name3))

            device_from_slot = []
            for i in range(len(list_slot3)):                
                if list_slot3[i]["entity"] == "electronicDevices":
                    device_from_slot.append(list_slot3[i]["value"]["value"])
            
            # print (device)
            # Modified: 0=not modified, 1=add new permission, 2=append new device to existing list
            modified = 1
            devices = []            # old and new added
            for p in permission_list:
                if p['username'] == user_from_slot:
                    if p['intent_command'] == intent_name3:
                        if intent_name3 in {"turnON_ED", "turnOFF_ED"}:
                            devices = p['device_list']
                            for i in range(len(device_from_slot)): 
                                if p['device_list'].count(device_from_slot[i]):
                                    modified = 0
                                    break
                                else: 
                                    devices.append(device_from_slot[i])
                                    modified = 2
                            break
                        else:
                            modified = 0
                            break
            print (devices)
            logging.info("Modified value: "+str(modified))
            if modified == 1:
                if intent_name3 in {"turnON_ED", "turnOFF_ED"}:
                    # devices is blank
                    if not devices:
                        permission_list.append({"username": user_from_slot, "intent_command": intent_name3, "device_list": device_from_slot})
                    else:
                        permission_list.append({"username": user_from_slot, "intent_command": intent_name3, "device_list": devices})
                else:
                    permission_list.append({"username": user_from_slot, "intent_command": intent_name3})
                logging.info(permission_list)
           
            if modified != 0:
                # 3. Write the updated json file
                with open('permissions.json', "w") as file:
                    json.dump(permission_list, file)
                logging.info(permission_list)


if __name__ == "__main__":
    main()