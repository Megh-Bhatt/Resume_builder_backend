"""
Online LaTeX Compiler - Vercel Compatible
Compiles LaTeX using free online APIs - no local dependencies

Supported Services (in priority order):
1. latex.ytotech.com (PRIMARY - JSON POST API)
2. latex.ytotech.com (FALLBACK 1 - GET API)  
3. texlive.net (FALLBACK 2 - if available)
"""
import requests
import time
from typing import Tuple, Optional
import logging
import json
import urllib.parse

logger = logging.getLogger(__name__)


def compile_latex_online(latex_code: str, timeout: int = 45) -> Tuple[bool, Optional[bytes], str]:
    """
    Compile LaTeX code to PDF using online API
    Tries multiple services in order until one succeeds
    
    Args:
        latex_code: Complete LaTeX document as string
        timeout: Max seconds to wait (default 45s for Vercel)
        
    Returns:
        (success, pdf_bytes, error_message)
    """
    services = [
        ("YtoTech JSON POST", _compile_with_ytotech_json),
        ("YtoTech GET", _compile_with_ytotech_get),
    ]
    
    errors = []
    
    for service_name, service_func in services:
        try:
            logger.info(f"Trying {service_name}...")
            success, pdf_bytes, error = service_func(latex_code, timeout)
            if success:
                logger.info(f"✅ {service_name} succeeded!")
                return True, pdf_bytes, ""
            else:
                errors.append(f"{service_name}: {error}")
                logger.warning(f"❌ {service_name} failed: {error}")
        except Exception as e:
            error_msg = str(e)[:100]
            errors.append(f"{service_name}: {error_msg}")
            logger.warning(f"❌ {service_name} error: {error_msg}")
            continue
    
    # All services failed
    combined_errors = "; ".join(errors)
    return False, None, f"All compilation services failed: {combined_errors}"


def _compile_with_ytotech_json(latex_code: str, timeout: int) -> Tuple[bool, Optional[bytes], str]:
    """
    PRIMARY: Compile using latex.ytotech.com with JSON POST
    Most reliable method with full feature support
    """
    logger.info("Attempting compilation with latex.ytotech.com (JSON POST)")
    
    try:
        url = "https://latex.ytotech.com/builds/sync"
        
        # YtoTech expects JSON with resources array
        payload = {
            "compiler": "pdflatex",
            "resources": [
                {
                    "main": True,
                    "content": latex_code
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf'
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        # Check if we got a successful response (200 OK or 201 Created)
        if response.status_code in [200, 201]:
            # Verify it's actually a PDF
            if response.content[:4] == b'%PDF':
                logger.info(f"Successfully compiled PDF ({len(response.content)} bytes)")
                return True, response.content, ""
            else:
                error_text = response.text[:200] if response.text else "Invalid response format"
                return False, None, f"Got non-PDF response: {error_text}"
        else:
            error_text = response.text[:300] if response.text else "Unknown error"
            return False, None, f"HTTP {response.status_code}: {error_text}"
            
    except requests.exceptions.Timeout:
        return False, None, "Request timeout (>45s)"
    except requests.exceptions.RequestException as e:
        return False, None, f"Network error: {str(e)[:100]}"
    except Exception as e:
        return False, None, f"Error: {str(e)[:100]}"


def _compile_with_ytotech_get(latex_code: str, timeout: int) -> Tuple[bool, Optional[bytes], str]:
    """
    FALLBACK 1: Compile using latex.ytotech.com with GET request
    Simpler method, good for basic documents
    """
    logger.info("Attempting compilation with latex.ytotech.com (GET)")
    
    try:
        url = "https://latex.ytotech.com/builds/sync"
        
        params = {
            'content': latex_code,
            'compiler': 'pdflatex'
        }
        
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers={'Accept': 'application/pdf'}
        )
        
        # Check for success (200 OK or 201 Created)
        if response.status_code in [200, 201]:
            if response.content[:4] == b'%PDF':
                logger.info(f"Successfully compiled PDF ({len(response.content)} bytes)")
                return True, response.content, ""
            else:
                return False, None, "Got non-PDF response"
        else:
            error_text = response.text[:200] if response.text else "Unknown error"
            return False, None, f"HTTP {response.status_code}: {error_text}"
            
    except Exception as e:
        return False, None, f"Error: {str(e)[:100]}"


def compile_latex_with_retry(latex_code: str, max_retries: int = 2, timeout: int = 45) -> Tuple[bool, Optional[bytes], str]:
    """
    Compile LaTeX with automatic retry logic for production reliability
    
    Args:
        latex_code: Complete LaTeX document as string
        max_retries: Maximum number of retry attempts
        timeout: Timeout per attempt in seconds
        
    Returns:
        (success, pdf_bytes, error_message)
    """
    for attempt in range(max_retries):
        logger.info(f"Compilation attempt {attempt + 1}/{max_retries}")
        
        success, pdf_bytes, error = compile_latex_online(latex_code, timeout)
        
        if success:
            return True, pdf_bytes, ""
        
        # If not the last attempt, wait before retry
        if attempt < max_retries - 1:
            wait_time = 2 * (attempt + 1)  # Exponential backoff
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    # All attempts failed
    return False, None, f"Compilation failed after {max_retries} attempts: {error}"


def compile_latex_with_retry(latex_code: str, max_retries: int = 2, timeout: int = 45) -> Tuple[bool, Optional[bytes], str]:
    """
    Compile LaTeX with automatic retry logic for production reliability
    
    Args:
        latex_code: Complete LaTeX document as string
        max_retries: Maximum number of retry attempts
        timeout: Timeout per attempt in seconds
        
    Returns:
        (success, pdf_bytes, error_message)
    """
    for attempt in range(max_retries):
        logger.info(f"Compilation attempt {attempt + 1}/{max_retries}")
        
        success, pdf_bytes, error = compile_latex_online(latex_code, timeout)
        
        if success:
            return True, pdf_bytes, ""
        
        # If not the last attempt, wait before retry
        if attempt < max_retries - 1:
            wait_time = 2 * (attempt + 1)  # Exponential backoff
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    # All attempts failed
    return False, None, f"Compilation failed after {max_retries} attempts: {error}"