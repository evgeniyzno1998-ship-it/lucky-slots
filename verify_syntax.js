const fs = require('fs');
const code = fs.readFileSync('index.html', 'utf8');
const regex = /<script>([\s\S]*?)<\/script>/gi;
let match;
let idx = 1;
while ((match = regex.exec(code)) !== null) {
    try {
        new Function(match[1]);
    } catch (e) {
        console.error('Syntax error in block ' + idx + ':', e);
        // Write out the block that failed to debug
        fs.writeFileSync('failed_script_block.js', match[1]);
        console.log('Wrote failed block to failed_script_block.js');
    }
    idx++;
}
