const fs = require('fs');
const path = require('path');

const targetFile = path.join(__dirname, 'src', 'pages', 'execute', 'ImportSkillPage.tsx');

let content = fs.readFileSync(targetFile, 'utf8');

// Find 'export default ImportSkillPage;' and slice there
const matchIndex = content.indexOf('export default ImportSkillPage;');
if (matchIndex !== -1) {
    const safeCutoffIndex = matchIndex + 'export default ImportSkillPage;'.length;
    content = content.substring(0, safeCutoffIndex) + '\n';
    fs.writeFileSync(targetFile, content, 'utf8');
    console.log('Successfully removed the legacy styles object.');
} else {
    console.log('Could not find export statement to truncate.');
}
