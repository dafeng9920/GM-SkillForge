const fs = require('fs');
const path = require('path');

const targetFile = path.join(__dirname, 'src', 'pages', 'execute', 'ImportSkillPage.tsx');

let content = fs.readFileSync(targetFile, 'utf8');

// Pattern 1: style={styles.fooBar} -> className={styles['foo-bar']}
// Helper to convert camelCase to kebab-case
const camelToKebab = (str) => str.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`);

content = content.replace(/style=\{styles\.([a-zA-Z0-9_]+)\}/g, (match, propName) => {
    return `className={styles['${camelToKebab(propName)}']}`;
});

// Pattern 2: style={{ ...styles.foo, ...styles.bar }} -> className={`${styles['foo']} ${styles['bar']}`}
content = content.replace(/style=\{\{\s*\.\.\.styles\.([a-zA-Z0-9_]+),\s*\.\.\.styles\.([a-zA-Z0-9_]+)\s*\}\}/g, (match, prop1, prop2) => {
    return `className={\`\$\{styles['${camelToKebab(prop1)}']\} \$\{styles['${camelToKebab(prop2)}']\}\`}`;
});

// Pattern 3: style={{ ...styles.foo, backgroundColor: 'red' }} 
// We will just blindly map styles.foo to className but this requires manual intervention if it mixes. Let's see if we have simple ones first.

fs.writeFileSync(targetFile, content, 'utf8');
console.log('Styles fixed in', targetFile);
