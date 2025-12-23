#!/usr/bin/env node
/**
 * Docker Backup Script for PrismWeave
 * Backs up ChromaDB volume to timestamped archive
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const BACKUP_DIR = path.join(__dirname, '..', 'backups');
const VOLUME_NAME = 'prismweave_chroma-data';
const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('.')[0];
const backupFile = `chroma-backup-${timestamp}.tar.gz`;

function ensureBackupDir() {
  if (!fs.existsSync(BACKUP_DIR)) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
    console.log(`✓ Created backup directory: ${BACKUP_DIR}`);
  }
}

function checkVolumeExists() {
  try {
    const volumes = execSync('docker volume ls -q', { encoding: 'utf8' });
    if (!volumes.includes(VOLUME_NAME)) {
      console.error(`✗ Volume ${VOLUME_NAME} not found`);
      console.log('Available volumes:');
      execSync('docker volume ls', { stdio: 'inherit' });
      process.exit(1);
    }
  } catch (error) {
    console.error('✗ Failed to check volumes:', error.message);
    process.exit(1);
  }
}

function createBackup() {
  try {
    console.log(`\n📦 Creating backup of ${VOLUME_NAME}...`);

    const cmd = `docker run --rm \
      -v ${VOLUME_NAME}:/data \
      -v ${BACKUP_DIR}:/backup \
      alpine tar czf /backup/${backupFile} -C /data .`;

    execSync(cmd, { stdio: 'inherit' });

    const backupPath = path.join(BACKUP_DIR, backupFile);
    const stats = fs.statSync(backupPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);

    console.log(`\n✓ Backup created successfully!`);
    console.log(`  File: ${backupPath}`);
    console.log(`  Size: ${sizeMB} MB`);
  } catch (error) {
    console.error('✗ Backup failed:', error.message);
    process.exit(1);
  }
}

function listBackups() {
  if (!fs.existsSync(BACKUP_DIR)) {
    console.log('No backups found.');
    return;
  }

  const backups = fs
    .readdirSync(BACKUP_DIR)
    .filter((f) => f.startsWith('chroma-backup-'))
    .sort()
    .reverse();

  if (backups.length === 0) {
    console.log('No backups found.');
    return;
  }

  console.log('\n📋 Available backups:');
  backups.forEach((backup, index) => {
    const stats = fs.statSync(path.join(BACKUP_DIR, backup));
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    const date = stats.mtime.toISOString().split('T')[0];
    console.log(`  ${index + 1}. ${backup} (${sizeMB} MB, ${date})`);
  });
}

// Main execution
console.log('🐳 PrismWeave Docker Backup Tool\n');

ensureBackupDir();
checkVolumeExists();
createBackup();
listBackups();

console.log('\n✅ Done!\n');
