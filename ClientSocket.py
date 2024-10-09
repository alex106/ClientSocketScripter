import os
import socket
import json
import sys
import argparse
import time
client_file = "ScriptCommander.json"
def send_json_to_server(ip, port, filename, constuid, sum):
    try:
        # Create a socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        if constuid != "":
            uid = constuid
        else:
            # Generate Unique ID for the session
            uid = os.urandom(16).hex()
        # Read the JSON data from the file
        # Check if the file exists
        if not os.path.exists(filename):
            print(f"Error: {os.path.abspath(filename)} not found.")
            sys.exit(1)
        with open(filename, 'r') as json_file:
            json_data = json.load(json_file)
        
        # Check if the JSON data contains the files tag
        if 'files' in json_data:
            # Read list of file names from Json 
            files = json_data['files']
        else:
            if 'CommandList' in json_data:
                files = files = {file: None for file in json_data['CommandList']}
        skip = False
        item_count = len(files)
        # Read each json file and send to server
        for file, timeout in files.items():
            if skip:
                if item_count > 1:
                    item_count -= 1
                    continue
            with open(file, 'r') as json_file:
                json_data = json.load(json_file)
            # Get the First Key of the JSON data
            key = list(json_data.keys())[0]
            # Replace the UID tag with the generated UID            
            json_data[key]['T095'] = uid.upper()
            if json_data[key].get('9F02') is not None:
                json_data[key]['9F02'] = str(sum)
            # Serialize the JSON data
            serialized_json = json.dumps(json_data)
            # Whait for timeout seconds before sending next file
            if timeout:
                time.sleep(timeout)
            # Send the serialized JSON data to the server
            client_socket.sendall(serialized_json.encode())
            # Receive the response from the server
            response = client_socket.recv(3*1024).decode('utf-8')
            # Serialize the response into JSON
            jresponse = json.loads(response)
            # Remove the file extension
            fname = file.split(".")[0]
            #overwrite response to file
            with open(f"{fname}_response.json", 'w', encoding='utf-8') as json_file:
                json.dump(jresponse, json_file, ensure_ascii=False, indent=4)
            # Check the error code tag is exist and contains the response
            
            if 'C004' in jresponse:
                if 'T00A' in jresponse['C004'] and 'T00B' in jresponse['C004']:
                # Check if the error code is not 0
                    if jresponse['C004']['T00A'] != "0":
                        print(f"Error on {file} execution :{jresponse['C004']['T00A']} - {jresponse['C004']['T00B']}")
                        # Run last command in the list by skiping all other commands
                        skip = True
            item_count -= 1
                    

            # print(f"Response from the server: {response}")
        # Close the socket
        client_socket.close()
        successText = "Success"
        if skip:
            successText = "Failed"
        print(f"JSON {filename} executed with {ip}:{port} Execution resolution: {successText}.")
    except Exception as e:
        # Check if client socket is still open and close it
        if client_socket:
            client_socket.close()
        print(f"Error: {e}")
        
def args_explain():
    parser = argparse.ArgumentParser(description="Process data.")
    parser.add_argument('-hst', "--host", default="127.0.0.1", help='host address')
    parser.add_argument('-prt', "--port", default="3000", help='port of server listener')
    parser.add_argument('-dir', "--dir", default=os.getcwd(), help='port of server listener')
    parser.add_argument('-fl', '--file',default=client_file, help='file location')
    parser.add_argument('-cnst', '--constuid',default="", help='file location')
    parser.add_argument('-sm', '--sum',default=100, help='sum in agorot to pay')
    return parser.parse_args()

def main( args_val ):
    ip = args_val.host
    port = int(args_val.port)
    # Check directory exist
    if not os.path.exists(args_val.dir):
        print(f"Error: {args_val.dir} not found.")
        sys.exit(1)
    os.chdir(args_val.dir)
    filename = os.path.join(args_val.dir,args_val.file)

    send_json_to_server(ip, port, filename, args_val.constuid, args_val.sum)
    
if __name__ == "__main__":
    main(args_explain())