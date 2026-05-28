"""
IBM Box Integration Module for Certification Workflow
======================================================

This module provides integration with IBM Box for:
- Downloading input files from Box folders
- Uploading output files to Box folders
- Managing Box authentication
- Handling file operations with retry logic

Requirements:
    pip install boxsdk[jwt]

Author: IBM BOB
Date: 2026-05-28
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
import tempfile
from datetime import datetime

try:
    from boxsdk import Client, JWTAuth, OAuth2
    from boxsdk.exception import BoxAPIException
    BOX_SDK_AVAILABLE = True
except ImportError:
    BOX_SDK_AVAILABLE = False
    logging.warning("boxsdk not installed. Install with: pip install boxsdk[jwt]")

logger = logging.getLogger(__name__)


class BoxIntegration:
    """Handle IBM Box file operations for the certification workflow."""
    
    def __init__(self, config_file: Optional[str] = None,
                 auth_method: str = 'jwt',
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 enterprise_id: Optional[str] = None,
                 jwt_key_id: Optional[str] = None,
                 rsa_private_key_file: Optional[str] = None,
                 rsa_private_key_passphrase: Optional[str] = None,
                 access_token: Optional[str] = None,
                 refresh_token: Optional[str] = None,
                 token_file: Optional[str] = None):
        """
        Initialize Box integration.
        
        Args:
            config_file: Path to Box JWT config file (JSON)
            auth_method: Authentication method ('jwt' or 'oauth')
            client_id: Box application client ID
            client_secret: Box application client secret
            enterprise_id: Box enterprise ID (JWT only)
            jwt_key_id: JWT key ID (JWT only)
            rsa_private_key_file: Path to RSA private key file (JWT only)
            rsa_private_key_passphrase: Passphrase for RSA private key (JWT only)
            access_token: OAuth access token (OAuth only)
            refresh_token: OAuth refresh token (OAuth only)
            token_file: Path to store OAuth tokens (OAuth only)
        """
        if not BOX_SDK_AVAILABLE:
            raise ImportError("boxsdk is not installed. Install with: pip install boxsdk[jwt]")
        
        self.client = None
        self.auth_method = auth_method.lower()
        self.temp_dir = Path(tempfile.gettempdir()) / "box_certification_workflow"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize Box client based on auth method
        if self.auth_method == 'jwt':
            if config_file:
                self._init_from_config_file(config_file)
            else:
                self._init_from_credentials(
                    client_id, client_secret, enterprise_id,
                    jwt_key_id, rsa_private_key_file, rsa_private_key_passphrase
                )
        elif self.auth_method == 'oauth':
            self._init_oauth(
                client_id, client_secret, access_token,
                refresh_token, token_file
            )
        else:
            raise ValueError(f"Invalid auth_method: {auth_method}. Must be 'jwt' or 'oauth'")
        
        logger.info(f"Box integration initialized successfully with {self.auth_method.upper()} authentication")
    
    def _init_from_config_file(self, config_file: str):
        """Initialize Box client from JWT config file."""
        try:
            auth = JWTAuth.from_settings_file(config_file)
            self.client = Client(auth)
            
            # Test connection
            user = self.client.user().get()
            logger.info(f"Connected to Box as: {user.name} ({user.login})")
            
        except Exception as e:
            logger.error(f"Error initializing Box client from config file: {e}")
            raise
    
    def _init_from_credentials(self, client_id, client_secret, enterprise_id,
                               jwt_key_id, rsa_private_key_file, rsa_private_key_passphrase):
        """Initialize Box client from individual credentials."""
        try:
            # Read RSA private key
            with open(rsa_private_key_file, 'r') as key_file:
                rsa_private_key = key_file.read()
            
            # Create JWT auth
            auth = JWTAuth(
                client_id=client_id,
                client_secret=client_secret,
                enterprise_id=enterprise_id,
                jwt_key_id=jwt_key_id,
                rsa_private_key_data=rsa_private_key,
                rsa_private_key_passphrase=rsa_private_key_passphrase
            )
            
            self.client = Client(auth)
            
            # Test connection
            user = self.client.user().get()
            logger.info(f"Connected to Box as: {user.name} ({user.login})")
            
        except Exception as e:
            logger.error(f"Error initializing Box client from credentials: {e}")
    def _init_oauth(self, client_id, client_secret, access_token, 
                    refresh_token, token_file):
        """Initialize Box client with OAuth 2.0 authentication."""
        try:
            import json
            
            # Store token callback
            def store_tokens(new_access_token, new_refresh_token):
                """Store tokens to file for persistence."""
                if token_file:
                    tokens = {
                        'access_token': new_access_token,
                        'refresh_token': new_refresh_token
                    }
                    with open(token_file, 'w') as f:
                        json.dump(tokens, f)
                    logger.info(f"Tokens saved to {token_file}")
            
            # Load tokens from file if available
            if token_file and Path(token_file).exists() and not access_token:
                with open(token_file, 'r') as f:
                    tokens = json.load(f)
                    access_token = tokens.get('access_token')
                    refresh_token = tokens.get('refresh_token')
                logger.info(f"Tokens loaded from {token_file}")
            
            # Create OAuth2 object
            oauth = OAuth2(
                client_id=client_id,
                client_secret=client_secret,
                access_token=access_token,
                refresh_token=refresh_token,
                store_tokens=store_tokens
            )
            
            self.client = Client(oauth)
            
            # Test connection
            user = self.client.user().get()
            logger.info(f"Connected to Box via OAuth as: {user.name} ({user.login})")
            
        except Exception as e:
            logger.error(f"Error initializing Box client with OAuth: {e}")
            raise

            raise
    
    def download_file(self, file_id: str, output_path: Optional[Path] = None) -> Path:
        """
        Download a file from Box.
        
        Args:
            file_id: Box file ID
            output_path: Local path to save file (optional)
            
        Returns:
            Path to downloaded file
        """
        try:
            box_file = self.client.file(file_id).get()
            file_name = box_file.name
            
            # Determine output path
            if output_path is None:
                output_path = self.temp_dir / file_name
            else:
                output_path = Path(output_path)
                if output_path.is_dir():
                    output_path = output_path / file_name
            
            # Create parent directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            logger.info(f"Downloading file from Box: {file_name} (ID: {file_id})")
            with open(output_path, 'wb') as output_file:
                self.client.file(file_id).download_to(output_file)
            
            logger.info(f"File downloaded successfully: {output_path}")
            return output_path
            
        except BoxAPIException as e:
            logger.error(f"Box API error downloading file {file_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise
    
    def download_files_from_folder(self, folder_id: str, 
                                   output_dir: Optional[Path] = None,
                                   file_patterns: Optional[List[str]] = None) -> List[Path]:
        """
        Download all files from a Box folder.
        
        Args:
            folder_id: Box folder ID
            output_dir: Local directory to save files
            file_patterns: List of file name patterns to match (e.g., ['*.xlsx', '*.csv'])
            
        Returns:
            List of paths to downloaded files
        """
        try:
            if output_dir is None:
                output_dir = self.temp_dir
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get folder items
            folder = self.client.folder(folder_id).get()
            logger.info(f"Downloading files from Box folder: {folder.name} (ID: {folder_id})")
            
            downloaded_files = []
            items = folder.get_items()
            
            for item in items:
                if item.type == 'file':
                    # Check if file matches patterns
                    if file_patterns:
                        if not any(self._match_pattern(item.name, pattern) for pattern in file_patterns):
                            logger.debug(f"Skipping file (doesn't match patterns): {item.name}")
                            continue
                    
                    # Download file
                    file_path = self.download_file(item.id, output_dir)
                    downloaded_files.append(file_path)
            
            logger.info(f"Downloaded {len(downloaded_files)} files from Box folder")
            return downloaded_files
            
        except BoxAPIException as e:
            logger.error(f"Box API error downloading from folder {folder_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error downloading from folder {folder_id}: {e}")
            raise
    
    def upload_file(self, file_path: Path, folder_id: str, 
                   file_name: Optional[str] = None) -> str:
        """
        Upload a file to Box.
        
        Args:
            file_path: Local file path
            folder_id: Box folder ID to upload to
            file_name: Name for file in Box (optional, uses local filename)
            
        Returns:
            Box file ID of uploaded file
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_name is None:
                file_name = file_path.name
            
            logger.info(f"Uploading file to Box: {file_name} (Folder ID: {folder_id})")
            
            # Upload file
            folder = self.client.folder(folder_id)
            uploaded_file = folder.upload(str(file_path), file_name)
            
            logger.info(f"File uploaded successfully: {file_name} (ID: {uploaded_file.id})")
            return uploaded_file.id
            
        except BoxAPIException as e:
            logger.error(f"Box API error uploading file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            raise
    
    def upload_files(self, file_paths: List[Path], folder_id: str) -> Dict[str, str]:
        """
        Upload multiple files to Box.
        
        Args:
            file_paths: List of local file paths
            folder_id: Box folder ID to upload to
            
        Returns:
            Dictionary mapping local file paths to Box file IDs
        """
        uploaded_files = {}
        
        for file_path in file_paths:
            try:
                file_id = self.upload_file(file_path, folder_id)
                uploaded_files[str(file_path)] = file_id
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")
        
        logger.info(f"Uploaded {len(uploaded_files)} of {len(file_paths)} files")
        return uploaded_files
    
    def get_folder_info(self, folder_id: str) -> Dict:
        """
        Get information about a Box folder.
        
        Args:
            folder_id: Box folder ID
            
        Returns:
            Dictionary with folder information
        """
        try:
            folder = self.client.folder(folder_id).get()
            
            info = {
                'id': folder.id,
                'name': folder.name,
                'type': folder.type,
                'created_at': folder.created_at,
                'modified_at': folder.modified_at,
                'item_count': folder.item_collection['total_count']
            }
            
            return info
            
        except BoxAPIException as e:
            logger.error(f"Box API error getting folder info {folder_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting folder info {folder_id}: {e}")
            raise
    
    def list_folder_contents(self, folder_id: str) -> List[Dict]:
        """
        List contents of a Box folder.
        
        Args:
            folder_id: Box folder ID
            
        Returns:
            List of dictionaries with item information
        """
        try:
            folder = self.client.folder(folder_id).get()
            items = folder.get_items()
            
            contents = []
            for item in items:
                contents.append({
                    'id': item.id,
                    'name': item.name,
                    'type': item.type,
                    'size': getattr(item, 'size', None),
                    'modified_at': getattr(item, 'modified_at', None)
                })
            
            return contents
            
        except BoxAPIException as e:
            logger.error(f"Box API error listing folder {folder_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error listing folder {folder_id}: {e}")
            raise
    
    def create_folder(self, folder_name: str, parent_folder_id: str = '0') -> str:
        """
        Create a new folder in Box.
        
        Args:
            folder_name: Name for new folder
            parent_folder_id: Parent folder ID (default: root folder '0')
            
        Returns:
            Box folder ID of created folder
        """
        try:
            parent_folder = self.client.folder(parent_folder_id)
            new_folder = parent_folder.create_subfolder(folder_name)
            
            logger.info(f"Created Box folder: {folder_name} (ID: {new_folder.id})")
            return new_folder.id
            
        except BoxAPIException as e:
            logger.error(f"Box API error creating folder {folder_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating folder {folder_name}: {e}")
            raise
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        Match filename against pattern (supports * wildcard).
        
        Args:
            filename: Filename to check
            pattern: Pattern with * wildcard
            
        Returns:
            True if filename matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def cleanup_temp_files(self):
        """Clean up temporary downloaded files."""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary files: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")


def create_box_client(config_file: Optional[str] = None, **kwargs) -> BoxIntegration:
    """
    Convenience function to create Box integration client.
    
    Args:
        config_file: Path to Box JWT config file
        **kwargs: Alternative credentials (client_id, client_secret, etc.)
        
    Returns:
        BoxIntegration instance
    """
    return BoxIntegration(config_file=config_file, **kwargs)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Example: Initialize from config file
    # box = BoxIntegration(config_file="box_config.json")
    
    # Example: Download files from folder
    # files = box.download_files_from_folder(
    #     folder_id="123456789",
    #     file_patterns=["*.xlsx", "*.csv"]
    # )
    
    # Example: Upload file
    # file_id = box.upload_file(
    #     file_path=Path("output.xlsx"),
    #     folder_id="987654321"
    # )
    
    print("Box integration module loaded successfully")
    print("Install boxsdk with: pip install boxsdk[jwt]")

# Made with Bob