# src/storage/document_manager.py
import os
import magic
import PyPDF2
import io
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from fastapi import UploadFile, logger

from .universal_dual_storage import get_storage_manager

class DocumentManager:
    """Manages document uploads, storage, and processing"""
    
    def __init__(self):
        self.storage_manager = get_storage_manager()
        self.supported_formats = {
            "pdf": {
                "mime_types": ["application/pdf"],
                "max_size_mb": 50,
                "preview_generator": self._generate_pdf_preview,
                "text_extractor": self._extract_pdf_text
            },
            "doc": {
                "mime_types": ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
                "max_size_mb": 25,
                "preview_generator": self._generate_doc_preview,
                "text_extractor": self._extract_doc_text
            },
            "txt": {
                "mime_types": ["text/plain"],
                "max_size_mb": 5,
                "preview_generator": self._generate_text_preview,
                "text_extractor": self._extract_text_text
            },
            "md": {
                "mime_types": ["text/markdown"],
                "max_size_mb": 5,
                "preview_generator": self._generate_markdown_preview,
                "text_extractor": self._extract_markdown_text
            }
        }
    
    async def upload_document(
        self,
        file: UploadFile,
        user_id: str,
        campaign_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload document with validation and dual storage"""
        
        # Validate file
        validation_result = await self._validate_document(file)
        if not validation_result["valid"]:
            raise ValueError(f"Document validation failed: {validation_result['error']}")
        
        # Read file content
        content = await file.read()
        
        # Detect file type
        file_type = self._detect_file_type(content, file.filename)
        
        # Extract text content for search
        text_content = await self._extract_text_content(content, file_type)
        
        # Generate preview
        preview_data = await self._generate_document_preview(content, file_type)
        
        #  metadata
        enhanced_metadata = {
            "document_type": file_type,
            "text_content": text_content[:1000],  # First 1000 chars for search
            "page_count": validation_result.get("page_count", 1),
            "word_count": len(text_content.split()) if text_content else 0,
            "has_preview": preview_data is not None,
            "processing_timestamp": datetime.datetime.now(),
            **(metadata or {})
        }
        
        # Save to dual storage
        storage_result = await self.storage_manager.save_content_dual_storage(
            content_data=content,
            content_type="document",
            filename=file.filename,
            user_id=user_id,
            campaign_id=campaign_id,
            metadata=enhanced_metadata
        )
        
        # Save preview if generated
        preview_result = None
        if preview_data:
            preview_filename = f"preview_{os.path.splitext(file.filename)[0]}.jpg"
            preview_result = await self.storage_manager.save_content_dual_storage(
                content_data=preview_data,
                content_type="image",
                filename=preview_filename,
                user_id=user_id,
                campaign_id=campaign_id,
                metadata={"preview_for": storage_result["filename"]}
            )
        
        return {
            "success": True,
            "document": storage_result,
            "preview": preview_result,
            "text_content": text_content,
            "metadata": enhanced_metadata,
            "file_type": file_type
        }
    
    async def _validate_document(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded document"""
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer
        
        file_size_mb = file_size / (1024 * 1024)
        
        # Detect file type
        file_type = self._detect_file_type(content, file.filename)
        
        if file_type not in self.supported_formats:
            return {
                "valid": False,
                "error": f"Unsupported file type: {file_type}",
                "file_type": file_type
            }
        
        # Check size limits
        max_size = self.supported_formats[file_type]["max_size_mb"]
        if file_size_mb > max_size:
            return {
                "valid": False,
                "error": f"File too large: {file_size_mb:.1f}MB > {max_size}MB",
                "file_size_mb": file_size_mb
            }
        
        # Additional validation based on file type
        validation_extras = {}
        
        if file_type == "pdf":
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                validation_extras["page_count"] = len(pdf_reader.pages)
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Invalid PDF file: {str(e)}"
                }
        
        return {
            "valid": True,
            "file_type": file_type,
            "file_size_mb": file_size_mb,
            **validation_extras
        }
    
    def _detect_file_type(self, content: bytes, filename: str) -> str:
        """Detect file type from content and filename"""
        
        # Use python-magic for MIME type detection
        mime_type = magic.from_buffer(content, mime=True)
        
        # Map MIME types to our supported formats
        mime_to_type = {
            "application/pdf": "pdf",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "doc",
            "text/plain": "txt",
            "text/markdown": "md"
        }
        
        detected_type = mime_to_type.get(mime_type)
        if detected_type:
            return detected_type
        
        # Fallback to file extension
        extension = os.path.splitext(filename)[1].lower()
        extension_to_type = {
            ".pdf": "pdf",
            ".doc": "doc",
            ".docx": "doc",
            ".txt": "txt",
            ".md": "md"
        }
        
        return extension_to_type.get(extension, "unknown")
    
    async def _extract_text_content(self, content: bytes, file_type: str) -> str:
        """Extract text content from document"""
        
        if file_type in self.supported_formats:
            extractor = self.supported_formats[file_type]["text_extractor"]
            return await extractor(content)
        
        return ""
    
    async def _generate_document_preview(self, content: bytes, file_type: str) -> Optional[bytes]:
        """Generate preview image for document"""
        
        if file_type in self.supported_formats:
            generator = self.supported_formats[file_type]["preview_generator"]
            return await generator(content)
        
        return None
    
    # Text extraction methods
    async def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
        except Exception as e:
            logger.warning(f"PDF text extraction failed: {str(e)}")
            return ""
    
    async def _extract_doc_text(self, content: bytes) -> str:
        """Extract text from DOC/DOCX"""
        try:
            import docx
            
            doc = docx.Document(io.BytesIO(content))
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return text_content.strip()
        except Exception as e:
            logger.warning(f"DOC text extraction failed: {str(e)}")
            return ""
    
    async def _extract_text_text(self, content: bytes) -> str:
        """Extract text from plain text file"""
        try:
            return content.decode('utf-8')
        except Exception as e:
            logger.warning(f"Text extraction failed: {str(e)}")
            return ""
    
    async def _extract_markdown_text(self, content: bytes) -> str:
        """Extract text from Markdown file"""
        try:
            import markdown
            from bs4 import BeautifulSoup
            
            md_content = content.decode('utf-8')
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        except Exception as e:
            logger.warning(f"Markdown text extraction failed: {str(e)}")
            return content.decode('utf-8', errors='ignore')
    
    # Preview generation methods
    async def _generate_pdf_preview(self, content: bytes) -> Optional[bytes]:
        """Generate preview image for PDF"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(stream=content, filetype="pdf")
            page = doc.load_page(0)  # First page
            
            # Render page to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to bytes
            img_data = pix.tobytes("png")
            doc.close()
            
            return img_data
        except Exception as e:
            logger.warning(f"PDF preview generation failed: {str(e)}")
            return None
    
    async def _generate_doc_preview(self, content: bytes) -> Optional[bytes]:
        """Generate preview for DOC/DOCX (placeholder)"""
        # For now, return None. In production, you'd use LibreOffice headless
        # to convert to PDF, then generate preview
        return None
    
    async def _generate_text_preview(self, content: bytes) -> Optional[bytes]:
        """Generate preview for text files"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create preview image with text
            text_content = content.decode('utf-8')[:500]  # First 500 chars
            
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Use default font
            font = ImageFont.load_default()
            
            # Draw text
            draw.text((20, 20), text_content, fill='black', font=font)
            
            # Save to bytes
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()
        except Exception as e:
            logger.warning(f"Text preview generation failed: {str(e)}")
            return None
    
    async def _generate_markdown_preview(self, content: bytes) -> Optional[bytes]:
        """Generate preview for Markdown files"""
        # Similar to text preview but could render markdown
        return await self._generate_text_preview(content)