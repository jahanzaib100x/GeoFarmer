import re

file_path = r'f:\.Hackathon\0.GeoFarmer\frontend\lib\main.dart'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

def remove_function(code, func_name):
    # Regex to match the start of the function, including common return types
    pattern = r'(Widget|Future<void>|void)\s+' + func_name + r'\s*\('
    match = re.search(pattern, code)
    if not match:
        return code
    
    start_idx = match.start()
    
    # Find the first opening brace after the function signature
    brace_start = code.find('{', start_idx)
    if brace_start == -1:
        return code
        
    open_braces = 1
    idx = brace_start + 1
    while idx < len(code) and open_braces > 0:
        if code[idx] == '{':
            open_braces += 1
        elif code[idx] == '}':
            open_braces -= 1
        idx += 1
        
    # Return the code with the function body removed
    return code[:start_idx] + code[idx:]

funcs = [
    '_buildInsuranceForm', '_buildDroneStressMapGrid', '_fetchDroneStressData',
    '_buildBypassController', '_buildVoiceNegotiationTrainer', '_evaluateNegotiation',
    '_simulateNegotiationEvaluation', '_buildInputSupplyStore', '_buildSupplyCard',
    '_optimizeMandiRoute', '_buildCreditDirectory', '_buildCreditWebviewTile',
    '_buildNewsFeed', '_buildNewsTile', '_buildDataMarketplace', 
    '_buildWhatsAppStyleDiscussionForum', '_buildCivicComplaintForm'
]

for f in funcs:
    content = remove_function(content, f)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Removed 11 dead features")
