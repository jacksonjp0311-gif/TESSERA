
import sys, os, json, time
sys.path.insert(0, 'src')
os.chdir('C:/Users/jacks/OneDrive/Desktop/Tessera')

# Load the existing result
result_file = os.path.join('outputs', 'transfers', 'nab', 'machine_temperature_result.json')
if os.path.exists(result_file):
    with open(result_file) as f:
        old = json.load(f)
    print("Old result:", json.dumps(old.get('metrics', {}), indent=2))
else:
    print("No existing result, need to run training first")
