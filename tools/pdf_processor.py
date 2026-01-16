#!/usr/bin/env python3
"""
PDF Processor for Direct LLM Input

This module provides functionality to process PDF files for direct input to LLMs
that support multimodal input (like Gemini models). This is particularly useful
for papers with complex mathematical formulas that would lose information in
text conversion.
"""

import base64
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, Union


class PDFProcessor:
    """
    Processes PDF files for direct LLM consumption.
    
    Supports encoding PDFs to base64 for API transmission to models
    like Gemini that can directly process PDF content.
    """
    
    @staticmethod
    def is_pdf(file_path: Union[str, Path]) -> bool:
        """
        Check if a file is a PDF.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is a PDF
        """
        file_path = Path(file_path)
        return file_path.suffix.lower() == '.pdf'
    
    @staticmethod
    def encode_pdf_to_base64(file_path: Union[str, Path]) -> str:
        """
        Encode a PDF file to base64 string.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Base64 encoded string of the PDF content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a PDF
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not PDFProcessor.is_pdf(file_path):
            raise ValueError(f"File is not a PDF: {file_path}")
        
        with open(file_path, 'rb') as f:
            pdf_bytes = f.read()
        
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
    @staticmethod
    def get_pdf_size(file_path: Union[str, Path]) -> int:
        """
        Get the size of a PDF file in bytes.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            File size in bytes
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        return file_path.stat().st_size
    
    @staticmethod
    def prepare_pdf_for_llm(
        file_path: Union[str, Path],
        max_size_mb: float = 20.0
    ) -> Dict[str, Any]:
        """
        Prepare PDF file for LLM API input.
        
        Args:
            file_path: Path to the PDF file
            max_size_mb: Maximum allowed file size in MB
            
        Returns:
            Dictionary with 'mime_type', 'data' (base64), 'size_bytes', 'path'
            
        Raises:
            ValueError: If file exceeds size limit
        """
        file_path = Path(file_path)
        
        # Check file size
        size_bytes = PDFProcessor.get_pdf_size(file_path)
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > max_size_mb:
            raise ValueError(
                f"PDF file too large: {size_mb:.2f}MB exceeds limit of {max_size_mb}MB"
            )
        
        # Encode to base64
        base64_data = PDFProcessor.encode_pdf_to_base64(file_path)
        
        return {
            'mime_type': 'application/pdf',
            'data': base64_data,
            'size_bytes': size_bytes,
            'size_mb': size_mb,
            'path': str(file_path),
            'filename': file_path.name
        }
    
    @staticmethod
    def format_for_openrouter_gemini(
        file_path: Union[str, Path],
        prompt: str,
        max_size_mb: float = 20.0
    ) -> Dict[str, Any]:
        """
        Format PDF + prompt for OpenRouter API call to Gemini models.
        
        OpenRouter supports sending files via content blocks with inline_data.
        
        Args:
            file_path: Path to the PDF file
            prompt: Text prompt to accompany the PDF
            max_size_mb: Maximum file size in MB
            
        Returns:
            Message dictionary formatted for OpenRouter API
        """
        pdf_data = PDFProcessor.prepare_pdf_for_llm(file_path, max_size_mb)
        
        # Format for Gemini via OpenRouter
        # Gemini expects parts: [text_part, inline_data_part]
        message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "inline_data",
                    "inline_data": {
                        "mime_type": pdf_data['mime_type'],
                        "data": pdf_data['data']
                    }
                }
            ]
        }
        
        return message
    
    @staticmethod
    def check_model_supports_pdf(model_name: str) -> bool:
        """
        Check if a model supports PDF input.
        
        Args:
            model_name: Name of the model (e.g., "google/gemini-2.0-flash-exp")
            
        Returns:
            True if the model is known to support PDF input
        """
        # Models known to support PDF input
        pdf_supported_models = [
            'gemini-2.0-flash-exp',
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-3-pro',
            'gemini-flash-exp',
            'claude-3-5-sonnet',  # Claude 3.5 can handle PDF
            'claude-3-opus',
            'claude-3-sonnet',
            'gpt-4o',  # GPT-4o supports PDF via vision
            'gpt-4-turbo',
        ]
        
        # Check if model name contains any of the supported models
        model_lower = model_name.lower()
        return any(supported in model_lower for supported in pdf_supported_models)
    
    @staticmethod
    def get_recommended_pdf_model() -> str:
        """
        Get the recommended model for PDF processing via OpenRouter.
        
        Returns:
            Model identifier for OpenRouter
        """
        # Gemini 2.0 Flash Experimental has excellent PDF support
        return "google/gemini-2.0-flash-exp"


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process PDF files for LLM input"
    )
    parser.add_argument(
        "pdf_path",
        help="Path to PDF file"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check if file is valid PDF"
    )
    
    args = parser.parse_args()
    
    processor = PDFProcessor()
    
    if args.check_only:
        is_pdf = processor.is_pdf(args.pdf_path)
        size = processor.get_pdf_size(args.pdf_path) if is_pdf else 0
        print(f"Is PDF: {is_pdf}")
        if is_pdf:
            print(f"Size: {size / (1024*1024):.2f} MB")
    else:
        try:
            data = processor.prepare_pdf_for_llm(args.pdf_path)
            print(f"✅ PDF prepared successfully:")
            print(f"   File: {data['filename']}")
            print(f"   Size: {data['size_mb']:.2f} MB")
            print(f"   MIME type: {data['mime_type']}")
            print(f"   Base64 length: {len(data['data'])} chars")
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
