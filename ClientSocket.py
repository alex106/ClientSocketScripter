import os
import socket
import json
import sys
import argparse
import time
client_file = "ScriptCommander.json"
def send_json_to_server(ip, port, filename):
    try:
        # Create a socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        # my = {
        #     "files": {
        #         "a.json":0,
        #         "b.json":0,
        #         "c.json":30
        #     }
        # }
        # with open(filename, "w") as json_file:
        #     json.dump(my, json_file, indent=4)
        # Read the JSON data from the file
        # Check if the file exists
        if not os.path.exists(filename):
            print(f"Error: {os.path.abspath(filename)} not found.")
            sys.exit(1)
        with open(filename, 'r') as json_file:
            json_data = json.load(json_file)
            
        # Read list of file names from Json 
        files = json_data['files']

        # Read each json file and send to server
        for file, timeout in files.items():
            with open(file, 'r') as json_file:
                json_data = json.load(json_file)
            # Serialize the JSON data
            serialized_json = json.dumps(json_data)
            # Whait for timeout seconds before sending next file
            if timeout:
                time.sleep(timeout)
            # Send the serialized JSON data to the server
            client_socket.sendall(serialized_json.encode())
            # Receive the response from the server
            response = client_socket.recv(4096).decode('utf-8')
            # Serialize the response into JSON
            jresponse = json.loads(response)
            # Remove the file extension
            fname = file.split(".")[0]
            #overwrite response to file
            with open(f"{fname}_response.json", 'w', encoding='utf-8') as json_file:
                json.dump(jresponse, json_file, ensure_ascii=False, indent=4)
            # Check the error code tag is exist and contains the response
            
            if 'C004' in jresponse:
                # Check if the error code is not 0
                if jresponse['C004']['T00A'] != "0":
                    print(f"Error on {file} execution :{jresponse['C004']['T00A']} - {jresponse['C004']['T00B']}")
                    break

            # print(f"Response from the server: {response}")
        # Close the socket
        client_socket.close()

        print(f"JSON {filename} executed with {ip}:{port} successfully.")
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

    send_json_to_server(ip, port, filename)
    
if __name__ == "__main__":
    main(args_explain())