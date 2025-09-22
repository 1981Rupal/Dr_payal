# utils/backup_system.py - Database and File Backup System

import os
import subprocess
import logging
import boto3
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import json

logger = logging.getLogger(__name__)

class BackupManager:
    """Comprehensive backup management system"""
    
    def __init__(self, app=None):
        self.app = app
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.backup_dir = Path(app.config.get('BACKUP_FOLDER', 'backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
        # AWS S3 configuration
        self.aws_access_key = app.config.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = app.config.get('AWS_SECRET_ACCESS_KEY')
        self.s3_bucket = app.config.get('AWS_S3_BUCKET')
        self.aws_region = app.config.get('AWS_REGION', 'us-east-1')
        
        # Backup retention settings
        self.retention_days = app.config.get('BACKUP_RETENTION_DAYS', 30)
        self.max_local_backups = app.config.get('MAX_LOCAL_BACKUPS', 10)
    
    def create_database_backup(self, compress=True) -> Optional[str]:
        """Create a database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"db_backup_{timestamp}.sql"
            
            if compress:
                backup_filename += '.gz'
            
            backup_path = self.backup_dir / backup_filename
            
            # Get database URL
            database_url = self.app.config.get('SQLALCHEMY_DATABASE_URI')
            if not database_url:
                logger.error("No database URL configured")
                return None
            
            # Parse database URL
            if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
                return self._backup_postgresql(database_url, backup_path, compress)
            elif database_url.startswith('sqlite:///'):
                return self._backup_sqlite(database_url, backup_path, compress)
            else:
                logger.error(f"Unsupported database type: {database_url}")
                return None
        
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return None
    
    def _backup_postgresql(self, database_url: str, backup_path: Path, compress: bool) -> Optional[str]:
        """Backup PostgreSQL database"""
        try:
            # Extract connection details from URL
            # Format: postgresql://user:password@host:port/database
            url_parts = database_url.replace('postgresql://', '').replace('postgres://', '')
            
            if '@' in url_parts:
                auth_part, host_part = url_parts.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    username = auth_part
                    password = ''
            else:
                username = password = ''
                host_part = url_parts
            
            if '/' in host_part:
                host_port, database = host_part.split('/', 1)
            else:
                host_port = host_part
                database = ''
            
            if ':' in host_port:
                host, port = host_port.split(':', 1)
            else:
                host = host_port
                port = '5432'
            
            # Set environment variables for pg_dump
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', host,
                '-p', port,
                '-U', username,
                '-d', database,
                '--no-password',
                '--verbose'
            ]
            
            logger.info(f"Creating PostgreSQL backup: {backup_path}")
            
            if compress:
                # Pipe through gzip
                with gzip.open(backup_path, 'wt') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        text=True,
                        check=True
                    )
            else:
                with open(backup_path, 'w') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        text=True,
                        check=True
                    )
            
            logger.info(f"PostgreSQL backup completed: {backup_path}")
            return str(backup_path)
        
        except subprocess.CalledProcessError as e:
            logger.error(f"pg_dump failed: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            return None
    
    def _backup_sqlite(self, database_url: str, backup_path: Path, compress: bool) -> Optional[str]:
        """Backup SQLite database"""
        try:
            # Extract database path from URL
            db_path = database_url.replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                logger.error(f"SQLite database not found: {db_path}")
                return None
            
            logger.info(f"Creating SQLite backup: {backup_path}")
            
            if compress:
                with open(db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(db_path, backup_path)
            
            logger.info(f"SQLite backup completed: {backup_path}")
            return str(backup_path)
        
        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            return None
    
    def create_files_backup(self, folders: List[str] = None) -> Optional[str]:
        """Create backup of application files"""
        try:
            if folders is None:
                folders = ['uploads', 'static/uploads', 'logs']
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"files_backup_{timestamp}.tar.gz"
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Creating files backup: {backup_path}")
            
            # Create tar.gz archive
            cmd = ['tar', '-czf', str(backup_path)]
            
            # Add existing folders to backup
            for folder in folders:
                if os.path.exists(folder):
                    cmd.append(folder)
            
            if len(cmd) == 3:  # Only tar command, no folders to backup
                logger.warning("No folders found to backup")
                return None
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Files backup completed: {backup_path}")
            return str(backup_path)
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Files backup failed: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Files backup failed: {e}")
            return None
    
    def upload_to_s3(self, local_path: str, s3_key: str = None) -> bool:
        """Upload backup to AWS S3"""
        try:
            if not all([self.aws_access_key, self.aws_secret_key, self.s3_bucket]):
                logger.warning("AWS S3 not configured, skipping upload")
                return False
            
            if s3_key is None:
                s3_key = f"backups/{os.path.basename(local_path)}"
            
            logger.info(f"Uploading to S3: {local_path} -> s3://{self.s3_bucket}/{s3_key}")
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            
            s3_client.upload_file(local_path, self.s3_bucket, s3_key)
            
            logger.info(f"S3 upload completed: {s3_key}")
            return True
        
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Clean up old local backups"""
        try:
            logger.info("Cleaning up old backups")
            
            # Get all backup files
            backup_files = []
            for pattern in ['db_backup_*.sql*', 'files_backup_*.tar.gz']:
                backup_files.extend(self.backup_dir.glob(pattern))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent backups
            files_to_delete = backup_files[self.max_local_backups:]
            
            for file_path in files_to_delete:
                logger.info(f"Deleting old backup: {file_path}")
                file_path.unlink()
            
            # Also delete backups older than retention period
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for file_path in backup_files:
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_date:
                    logger.info(f"Deleting expired backup: {file_path}")
                    file_path.unlink()
        
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def create_full_backup(self, upload_to_s3: bool = True) -> dict:
        """Create a complete backup (database + files)"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'database_backup': None,
            'files_backup': None,
            's3_uploads': [],
            'success': False
        }
        
        try:
            # Create database backup
            db_backup = self.create_database_backup()
            if db_backup:
                results['database_backup'] = db_backup
                
                # Upload to S3 if configured
                if upload_to_s3 and self.upload_to_s3(db_backup):
                    results['s3_uploads'].append(db_backup)
            
            # Create files backup
            files_backup = self.create_files_backup()
            if files_backup:
                results['files_backup'] = files_backup
                
                # Upload to S3 if configured
                if upload_to_s3 and self.upload_to_s3(files_backup):
                    results['s3_uploads'].append(files_backup)
            
            # Clean up old backups
            self.cleanup_old_backups()
            
            results['success'] = bool(db_backup or files_backup)
            
            # Save backup metadata
            self._save_backup_metadata(results)
            
            return results
        
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            results['error'] = str(e)
            return results
    
    def _save_backup_metadata(self, backup_info: dict):
        """Save backup metadata for tracking"""
        try:
            metadata_file = self.backup_dir / 'backup_metadata.json'
            
            # Load existing metadata
            metadata = []
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            # Add new backup info
            metadata.append(backup_info)
            
            # Keep only recent metadata (last 100 backups)
            metadata = metadata[-100:]
            
            # Save updated metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            logger.info(f"Restoring database from: {backup_path}")
            
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            database_url = self.app.config.get('SQLALCHEMY_DATABASE_URI')
            
            if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
                return self._restore_postgresql(database_url, backup_path)
            elif database_url.startswith('sqlite:///'):
                return self._restore_sqlite(database_url, backup_path)
            else:
                logger.error(f"Unsupported database type for restore: {database_url}")
                return False
        
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    def _restore_postgresql(self, database_url: str, backup_path: str) -> bool:
        """Restore PostgreSQL database"""
        # Implementation would go here
        # This is a complex operation that should be done carefully
        logger.warning("PostgreSQL restore not implemented - use manual restore procedures")
        return False
    
    def _restore_sqlite(self, database_url: str, backup_path: str) -> bool:
        """Restore SQLite database"""
        # Implementation would go here
        # This is a complex operation that should be done carefully
        logger.warning("SQLite restore not implemented - use manual restore procedures")
        return False
