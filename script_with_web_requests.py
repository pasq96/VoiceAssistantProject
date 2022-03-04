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
    nc_input = input("Please enter an input (name-command): ")
    user, command = nc_input.split("-")  

    # Load a json file in memory
    user_list = None
    with open('users.json', 'r') as f_in:
        user_list = json.load(f_in)

    # Check user type in json loaded file and if user exist in the file. if not exit with error
    
    exist = 0
    user_type = None
    for u in user_list:
        if u['username'] == user:
            user_type = u['type']
            exist = 1
            break
    
    if (exist == 0):
        exit ("The user "+user+" not found in the database. Try again.")

    # caricare i due engine e sottoporre il "command" ad entrambi come query. Il modello che restituirà probabilità maggiore
    # alla query indicherà la tipologia di comando inviato (se di permessi o di comando "semplice")

    ngrok_url = input("Please insert ngrok url: ")
    
    # intent_name, probability, list_slot = load_and_parse("persistent_engine_permissions", command)
    # intent_name2, probability2, list_slot2 = load_and_parse("persistent_engine_commands", command)

    # ngrok_url = "http://05e0-34-135-81-205.ngrok.io"

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

    if (intent_name != "getPermission" and user_type == "user"):
        exit("ERROR! You do not have the privileges to perform the requested action.")

    if choice == 1:

        # add admin aggiunge un nuovo utente come admin oppure modifica il type di un utente già presente in lista in admin 
        # (se è di tipo 'user') altrimenti lascia la lista inalterata
        
        if (intent_name == "addAdmin"):
            user_from_slot = list_slot[0]["rawValue"]
            user_list = None
            # 1. Read file contents
            with open('users.json', "r") as file:
                user_list = json.load(file)
            logging.info(user_list)
            
            # Modified: 0=not modified, 1=modified only type, 2=add new user with admin privileges
            modified = 2
            for u in user_list:
                if u['username'] == user_from_slot:
                    if u['type'] != "admin":
                        u['type'] = "admin"
                        modified = 1
                        break
                    else: 
                        modified = 0
                        break

            logging.info("Modified value: "+str(modified))
            if modified == 2:
                user_list.append({"username": user_from_slot, "type": "admin"})
                logging.info(user_list)
            if modified != 0:
                # 3. Write the updated json file
                with open('users.json', "w") as file:
                    json.dump(user_list, file)

        # removeAdmin si è scelto di implementarlo nel modo seguente: se è presente un utente admin nella lista degli utenti, 
        # questo viene "declassato" in utente semplice ('user') altrimenti la lista rimane inalterata

        elif (intent_name == "removeAdmin"):
            user_from_slot = list_slot[0]["rawValue"]
            user_list = None
            # 1. Read file contents
            with open('users.json', "r") as file:
                user_list = json.load(file)
            logging.info(user_list)
            modified = None
            for u in user_list:
                if u['username'] == user_from_slot:
                    if u['type'] != "user":
                        u['type'] = "user"
                        modified = 1
                        break
                    else: 
                        modified = 0
                        break

            logging.info("Modified value: "+str(modified))
            if modified == 1:
                # 3. Write the updated json file
                with open('users.json', "w") as file:
                    json.dump(user_list, file)

        # Gli intenti setPermission sono stato ideati nel modo seguente: si va ad aggiungere alla lista json dei permessi 
        # (che lavora in blacklist) se è un intent "setPermissionNo". Ragioniamo in ottica blacklist: se è presente una entry 
        # del tipo user-intent_command, allora l'utente "user" non potra' eseguire "intent_command" altrimenti invece non ci sono limitazioni

        elif (intent_name == "setPermissionNo"):
            user_from_slot = list_slot[0]["rawValue"]
            command_from_slot = list_slot[1]["rawValue"]

            # 1. Read file contents
            with open('permissions.json', "r") as file:
                permission_list = json.load(file)

            logging.info(permission_list)
            
            intent_name3, _ , list_slot3 = send_request(url_pec, command_from_slot)
            print("Intent name is "+ str(intent_name3))

            device_from_slot = []
            for i in range(len(list_slot3)):                
                if list_slot3[i]["entity"] == "electronicDevices":

                    # Extract the lemma value
                    device_from_slot.append(list_slot3[i]["value"]["value"])
            
            # modified: 0 = not modified, 1 = add new permission, 2 = append new device to existing list
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
                    # if devices variable is blank (empty list)
                    if not devices:
                        permission_list.append({"username": user_from_slot, "intent_command": intent_name3, "device_list": device_from_slot})
                    else:
                        permission_list.append({"username": user_from_slot, "intent_command": intent_name3, "device_list": devices})
                else:
                    permission_list.append({"username": user_from_slot, "intent_command": intent_name3})
            if modified != 0:
                # 3. Write the updated json file
                with open('permissions.json', "w") as file:
                    json.dump(permission_list, file)
            
            logging.info(permission_list)


        elif (intent_name == "setPermissionYes"):
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
            
            # Modified: 0 = not modified, 1 = remove permission, 
            modified = 0
            devices = []            # old and new added
            for p in permission_list:
                if p['username'] == user_from_slot:
                    if p['intent_command'] == intent_name3:
                        if intent_name3 in {"turnON_ED", "turnOFF_ED"}:
                            devices = p['device_list']
                            for i in range(len(device_from_slot)): 
                                if devices.count(device_from_slot[i]):
                                    devices.remove(device_from_slot[i])
                                    if not devices: # device is empty after remove last device
                                        permission_list.remove(p)
                                    modified = 1
                                    break
                            break
                        else:
                            permission_list.remove(p)
                            modified = 1
                            break
            print (devices)
            logging.info("Modified value: "+str(modified))           
            if modified != 0:
                # 3. Write the updated json file
                with open('permissions.json', "w") as file:
                    json.dump(permission_list, file)
                logging.info(permission_list)

        elif (intent_name == "getPermission"):
            user_from_slot = list_slot[0]["rawValue"]
            # 1. Read file contents
            with open('users.json', "r") as file:
                    user_list = json.load(file)

            modified = 0 
            if (user_from_slot is not None):
                for u in user_list:
                    if (u['username'] == user and u['type'] == "admin") or (user == user_from_slot and user == u['username']):
                        print("List of permission denied (user: "+user_from_slot+"): "+str(getPermissionList(user_from_slot)))
                        modified = 1
                if (modified == 0):
                    exit("You do not have the authorization to request information on the permissions of the user "+user_from_slot)
            else: 
                print("List of permission denied (user: "+user+"): "+str(getPermissionList(user)))


    # Situazione in cui abbiamo come intent COMMAND
    elif choice == 2:
        perm = getPermission(user, intent_name2)
        if (perm is False):
            exit ("The user "+user+ " is not authorized to execute this operation!")
        else:
            print ("SUCCESS! Sending the json file to Alexa...")
            # Crea un file json "fittizio" coi dati dell'intent e degli slots
            json_obj = {}
            json_obj['intent_name'] = intent_name2
            json_obj['slots'] = []
            for i in range(len(list_slot2)):                
                json_obj['slots'].append({
                    'entity' : list_slot2[i]["entity"],
                    'value' : list_slot2[i]["rawValue"]
                    })
            print (json_obj)
    
    
    exit()

if __name__ == "__main__":
    main()
