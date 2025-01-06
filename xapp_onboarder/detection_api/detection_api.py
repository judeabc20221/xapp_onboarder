################################################################################
#   Copyright (c) NTUST NGN Lab.                                               #
#                                                                              #
#   Licensed under the Apache License, Version 2.0 (the "License");            #
#   you may not use this file except in compliance with the License.           #
#   You may obtain a copy of the License at                                    #
#                                                                              #
#       http://www.apache.org/licenses/LICENSE-2.0                             #
#                                                                              #
#   Unless required by applicable law or agreed to in writing, software        #
#   distributed under the License is distributed on an "AS IS" BASIS,          #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
#   See the License for the specific language governing permissions and        #
#   limitations under the License.                                             #
################################################################################

import json
import os

class detectionError(Exception):
    def __init__(self, message, status_code):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.status_code = status_code

class detection_api():
    def __init__(self, config_file):
        self.config_file = config_file

        config = self.config_file

        current_directory = os.path.dirname(os.path.abspath(__file__))
        with open(current_directory+'/detection_api.json', 'r') as detection_file:
            detection_api = json.load(detection_file)
            
        messaging_rxMessages = []
        messaging_txMessages = []

        for port in config['messaging']['ports']:
            if 'rxMessages' in port:
                messaging_rxMessages.extend(port['rxMessages'])
            if 'txMessages' in port:
                messaging_txMessages.extend(port['txMessages'])

        # Extract rxMessages and txMessages in rmr
        rmr_rxMessages = config['rmr']['rxMessages']
        rmr_txMessages = config['rmr']['txMessages']

        # Check if each API exists
        results_rmr = []
        error_message = ""
        det_rmr_err = False

        # check rmr
        for api in detection_api['rmr']:
            is_in_messaging_rx = api in messaging_rxMessages
            is_in_messaging_tx = api in messaging_txMessages
            is_in_rmr_rx = api in rmr_rxMessages
            is_in_rmr_tx = api in rmr_txMessages
            
            if is_in_messaging_rx or is_in_messaging_tx or is_in_rmr_rx or is_in_rmr_tx:
                det_rmr_err = True
                results_rmr.append(api)

        results_rest = []
        det_rest_err = False

        # check restapi
        if "restapi" in config:
            for component in config['restapi']:
                if component in detection_api['restapi']:
                    for type in config['restapi'][component]:
                        if type and type in detection_api['restapi'][component]:
                            for detect_api in detection_api['restapi'][component][type]:
                                if detect_api in config['restapi'][component][type]:
                                    det_rest_err = True
                                    results_rest.append( detect_api )
            results_all = [ results_rmr, results_rest ]
        
        if det_rmr_err :
            if det_rest_err:
                raise detectionError( f"There are illegal APIs in the xApp to be deployed.\nCaused RMR API :\n{results_rmr}\nCause Rest API:\n{results_rest}", 400 )
            else:
                raise detectionError( f"There are illegal RMR Message in the xApp to be deployed.\nCaused RMR Message :\n{results_rmr}", 400 )
        elif det_rest_err:
            raise detectionError( f"There are illegal APIs in the xApp to be deployed.\nCause Rest API:\n{results_rest}", 400 )
