const fs = require('fs');
const path = require('path');
const base = 'C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera';

// Fix the version in agnt_bridge.py
let bridge = fs.readFileSync(path.join(base, 'src/tessera/agnt_bridge.py'), 'utf8');
bridge = bridge.replace('TESSERA_VERSION = "0.4.2"', 'TESSERA_VERSION = "0.4.5"');
fs.writeFileSync(path.join(base, 'src/tessera/agnt_bridge.py'), bridge);
console.log('Fixed bridge version to 0.4.5');

// Commit and push
const { execSync } = require('child_process');
execSync('git add -A', { cwd: base, encoding: 'utf8' });
execSync('git commit -m "fix: update agnt_bridge.py version to 0.4.5"', { cwd: base, encoding: 'utf8' });
const push = execSync('git push origin main', { cwd: base, encoding: 'utf8', timeout: 60000 });
console.log('Pushed:', push.trim());
