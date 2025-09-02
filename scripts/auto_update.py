#!/usr/bin/env python3
"""
TechRadar Advanced - Automated Update Script
Runs the complete update pipeline with comprehensive error handling and monitoring
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any
import traceback

# Configure logging
# Ensure logs directory exists before setting up logging
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self):
        self.scripts = [
            'fetch_news.py',
            'process_news.py', 
            'generate_content.py',
            'update_analytics.py'
        ]
        self.max_retries = 3
        self.retry_delay = 30  # seconds
        self.results = {}
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
    def run_script(self, script_name: str, retry_count: int = 0) -> bool:
        """Run a script with retry logic"""
        try:
            logger.info(f"Running {script_name} (attempt {retry_count + 1})")
            
            # Run the script
            result = subprocess.run(
                [sys.executable, f'scripts/{script_name}'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"SUCCESS: {script_name} completed successfully")
                self.results[script_name] = {
                    'status': 'success',
                    'attempts': retry_count + 1,
                    'output': result.stdout
                }
                return True
            else:
                logger.error(f"FAILED: {script_name} failed with return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                
                if retry_count < self.max_retries - 1:
                    logger.info(f"Retrying {script_name} in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    return self.run_script(script_name, retry_count + 1)
                else:
                    self.results[script_name] = {
                        'status': 'failed',
                        'attempts': retry_count + 1,
                        'error': result.stderr
                    }
                    return False
                    
        except subprocess.TimeoutExpired:
            logger.error(f"TIMEOUT: {script_name} timed out after 10 minutes")
            if retry_count < self.max_retries - 1:
                logger.info(f"Retrying {script_name} in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                return self.run_script(script_name, retry_count + 1)
            else:
                self.results[script_name] = {
                    'status': 'timeout',
                    'attempts': retry_count + 1,
                    'error': 'Script timed out after 10 minutes'
                }
                return False
                
        except Exception as e:
            logger.error(f"ERROR: Unexpected error running {script_name}: {e}")
            logger.error(traceback.format_exc())
            
            if retry_count < self.max_retries - 1:
                logger.info(f"Retrying {script_name} in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                return self.run_script(script_name, retry_count + 1)
            else:
                self.results[script_name] = {
                    'status': 'error',
                    'attempts': retry_count + 1,
                    'error': str(e)
                }
                return False
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        try:
            logger.info("Checking dependencies...")
            
            # Check if required files exist
            required_files = [
                'data/news_sources.json',
                'requirements.txt'
            ]
            
            for file_path in required_files:
                if not os.path.exists(file_path):
                    logger.warning(f"Required file not found: {file_path}")
            
            # Check if data directory exists
            os.makedirs('data', exist_ok=True)
            os.makedirs('today', exist_ok=True)
            os.makedirs('analysis', exist_ok=True)
            
            logger.info("SUCCESS: Dependencies check completed")
            return True
            
        except Exception as e:
            logger.error(f"FAILED: Dependencies check failed: {e}")
            return False
    
    def validate_output(self) -> bool:
        """Validate that the update produced valid output"""
        try:
            logger.info("Validating output...")
            
            # Check if key files were created/updated
            key_files = [
                'data/raw-feeds.json',
                'data/processed-articles.json',
                'today/trending.json'
            ]
            
            for file_path in key_files:
                if not os.path.exists(file_path):
                    logger.error(f"FAILED: Required output file missing: {file_path}")
                    return False
                
                # Check if file has content
                if os.path.getsize(file_path) == 0:
                    logger.error(f"FAILED: Output file is empty: {file_path}")
                    return False
            
            # Validate JSON files
            for file_path in key_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"FAILED: Invalid JSON in {file_path}: {e}")
                    return False
            
            logger.info("SUCCESS: Output validation completed")
            return True
            
        except Exception as e:
            logger.error(f"FAILED: Output validation failed: {e}")
            return False
    
    def save_status_report(self):
        """Save a status report of the update"""
        try:
            status_report = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'overall_status': 'success' if all(r['status'] == 'success' for r in self.results.values()) else 'failed',
                'scripts': self.results,
                'summary': {
                    'total_scripts': len(self.scripts),
                    'successful': sum(1 for r in self.results.values() if r['status'] == 'success'),
                    'failed': sum(1 for r in self.results.values() if r['status'] != 'success')
                }
            }
            
            with open('logs/update_status.json', 'w', encoding='utf-8') as f:
                json.dump(status_report, f, indent=2)
            
            logger.info(f"Status report saved: {status_report['summary']}")
            
        except Exception as e:
            logger.error(f"Failed to save status report: {e}")
    
    def run_full_update(self) -> bool:
        """Run the complete update pipeline"""
        logger.info("STARTING: TechRadar Advanced Auto-Update")
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                logger.error("FAILED: Dependencies check failed, aborting update")
                return False
            
            # Run all scripts
            all_successful = True
            for script in self.scripts:
                if not self.run_script(script):
                    all_successful = False
                    logger.error(f"FAILED: Critical script failed: {script}")
                    # Continue with other scripts even if one fails
            
            # Validate output
            if not self.validate_output():
                logger.error("FAILED: Output validation failed")
                all_successful = False
            
            # Save status report
            self.save_status_report()
            
            if all_successful:
                logger.info("SUCCESS: TechRadar Advanced update completed successfully!")
                return True
            else:
                logger.error("FAILED: TechRadar Advanced update completed with errors")
                return False
                
        except Exception as e:
            logger.error(f"FATAL: Fatal error in auto-update: {e}")
            logger.error(traceback.format_exc())
            return False

def main():
    """Main function"""
    updater = AutoUpdater()
    success = updater.run_full_update()
    
    if success:
        logger.info("SUCCESS: Auto-update completed successfully")
        sys.exit(0)
    else:
        logger.error("FAILED: Auto-update failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
