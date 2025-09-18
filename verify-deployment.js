#!/usr/bin/env node

/**
 * Railway Deployment Verification Script
 * Checks if the project is ready for clean Node.js deployment
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 RAILWAY DEPLOYMENT VERIFICATION');
console.log('===================================\\n');

let errors = 0;
let warnings = 0;

// Check 1: Procfile exists and has correct content
try {
  const procfileContent = fs.readFileSync('Procfile', 'utf8').trim();
  if (procfileContent === 'web: node server.js') {
    console.log('✅ Procfile: Correct Node.js configuration');
  } else {
    console.error('❌ Procfile: Wrong content -', procfileContent);
    errors++;
  }
} catch (error) {
  console.error('❌ Procfile: Missing or unreadable');
  errors++;
}

// Check 2: package.json has start script
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  
  if (packageJson.scripts && packageJson.scripts.start === 'node server.js') {
    console.log('✅ package.json: Correct start script');
  } else {
    console.error('❌ package.json: Missing or wrong start script');
    errors++;
  }
  
  if (packageJson.engines && packageJson.engines.node) {
    console.log('✅ package.json: Node.js version specified');
  } else {
    console.warn('⚠️  package.json: Node.js version not specified');
    warnings++;
  }
  
  if (packageJson.main === 'server.js') {
    console.log('✅ package.json: Correct main entry point');
  } else {
    console.error('❌ package.json: Wrong main entry point');
    errors++;
  }
} catch (error) {
  console.error('❌ package.json: Missing or invalid JSON');
  errors++;
}

// Check 3: server.js exists
if (fs.existsSync('server.js')) {
  console.log('✅ server.js: Main application file exists');
} else {
  console.error('❌ server.js: Missing main application file');
  errors++;
}

// Check 4: No Python files in root
const pythonFiles = ['app.py', 'requirements.txt'].filter(file => fs.existsSync(file));
if (pythonFiles.length === 0) {
  console.log('✅ Clean: No Python files in root directory');
} else {
  console.error('❌ Python files found in root:', pythonFiles.join(', '));
  errors++;
}

// Check 5: .env.example exists
if (fs.existsSync('.env.example')) {
  console.log('✅ .env.example: Environment template exists');
} else {
  console.warn('⚠️  .env.example: Missing environment template');
  warnings++;
}

// Check 6: Node.js dependencies
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const requiredDeps = ['express', 'cors', 'multer', 'axios', 'dotenv'];
  const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep]);
  
  if (missingDeps.length === 0) {
    console.log('✅ Dependencies: All required packages present');
  } else {
    console.error('❌ Dependencies: Missing packages -', missingDeps.join(', '));
    errors++;
  }
} catch (error) {
  console.error('❌ Dependencies: Cannot verify package.json');
  errors++;
}

// Check 7: .gitignore is Node.js focused
try {
  const gitignoreContent = fs.readFileSync('.gitignore', 'utf8');
  if (gitignoreContent.includes('node_modules/') && gitignoreContent.includes('.env')) {
    console.log('✅ .gitignore: Node.js configuration detected');
  } else {
    console.warn('⚠️  .gitignore: May not be optimized for Node.js');
    warnings++;
  }
} catch (error) {
  console.warn('⚠️  .gitignore: Missing or unreadable');
  warnings++;
}

// Summary
console.log('\\n📊 VERIFICATION SUMMARY');
console.log('========================');

if (errors === 0) {
  console.log('🎉 SUCCESS: Project is ready for Railway deployment!');
  console.log('📋 Next steps:');
  console.log('   1. Commit and push to GitHub');
  console.log('   2. Connect repository to Railway');
  console.log('   3. Set environment variables in Railway dashboard');
  console.log('   4. Deploy!');
} else {
  console.error(`💥 FAILED: ${errors} error(s) must be fixed before deployment`);
  process.exit(1);
}

if (warnings > 0) {
  console.warn(`⚠️  ${warnings} warning(s) - deployment should work but consider fixing`);
}

console.log('\\n🚀 Happy deploying!');