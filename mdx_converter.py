#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
import re
import markdown
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import weasyprint
import frontmatter

def mdx_to_html(mdx_content):
    """
    Convert MDX content to HTML.
    This is a simplified conversion and may need enhancements for complex MDX.
    """
    try:
        # Extract frontmatter if present
        post = frontmatter.loads(mdx_content)
        content = post.content
        
        # Remove JSX/React components with a simple regex approach
        # For complex MDX files, a more robust parser would be needed
        content = re.sub(r'<[A-Z][a-zA-Z]*(\s+[a-zA-Z]+="[^"]*")*\s*\/>', '', content)
        content = re.sub(r'<[A-Z][a-zA-Z]*(\s+[a-zA-Z]+="[^"]*")*\s*>.*?<\/[A-Z][a-zA-Z]*>', '', content)
        
        # Replace import statements
        content = re.sub(r'import\s+.*?\s+from\s+[\'"](.*?)[\'"]\s*;?', '', content)
        
        # Replace export statements
        content = re.sub(r'export\s+.*?;?', '', content)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['extra', 'nl2br', 'tables', 'toc'])
        
        return html_content
    except Exception as e:
        print(f"Error converting MDX to HTML: {e}")
        return None

def html_to_docx(html_content, output_path):
    """
    Convert HTML content to DOCX format and save to output_path.
    """
    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Create a new Document
        doc = Document()
        
        # Process HTML elements
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'blockquote']):
            if element.name.startswith('h'):
                level = int(element.name[1])
                paragraph = doc.add_paragraph(element.text)
                paragraph.style = f'Heading {level}'
            elif element.name == 'p':
                doc.add_paragraph(element.text)
            elif element.name == 'blockquote':
                paragraph = doc.add_paragraph(element.text)
                paragraph.style = 'Quote'
            elif element.name == 'ul':
                # Skip the ul tag itself, we'll process the li elements inside
                continue
            elif element.name == 'ol':
                # Skip the ol tag itself, we'll process the li elements inside
                continue
            elif element.name == 'li':
                # Check if this li is inside a ul or ol
                if element.parent.name == 'ul':
                    doc.add_paragraph(element.text, style='List Bullet')
                elif element.parent.name == 'ol':
                    doc.add_paragraph(element.text, style='List Number')
        
        # Save the document
        doc.save(output_path)
        return True
    except Exception as e:
        print(f"Error converting HTML to DOCX: {e}")
        return False

def html_to_pdf(html_content, output_path):
    """
    Convert HTML content to PDF format and save to output_path.
    """
    try:
        # Wrap HTML in proper document structure
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Document</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20mm; }}
                h1 {{ color: #333; }}
                h2 {{ color: #444; }}
                blockquote {{ border-left: 3px solid #ccc; padding-left: 10px; color: #666; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert HTML to PDF using WeasyPrint
        weasyprint.HTML(string=full_html).write_pdf(output_path)
        return True
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")
        return False

def process_mdx_file(input_path, output_dir, output_format='both'):
    """
    Process a single MDX file to convert it to DOCX and/or PDF.
    
    Args:
        input_path: Path to the MDX file
        output_dir: Directory to save output files
        output_format: 'pdf', 'docx', or 'both'
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get filename without extension
        filename = os.path.basename(input_path).rsplit('.', 1)[0]
        
        # Read MDX content
        with open(input_path, 'r', encoding='utf-8') as f:
            mdx_content = f.read()
        
        # Convert MDX to HTML
        html_content = mdx_to_html(mdx_content)
        if not html_content:
            print(f"Failed to convert {input_path} to HTML")
            return
        
        # Convert HTML to DOCX if requested
        if output_format in ['docx', 'both']:
            docx_path = os.path.join(output_dir, f"{filename}.docx")
            if html_to_docx(html_content, docx_path):
                print(f"Successfully converted {input_path} to {docx_path}")
        
        # Convert HTML to PDF if requested
        if output_format in ['pdf', 'both']:
            pdf_path = os.path.join(output_dir, f"{filename}.pdf")
            if html_to_pdf(html_content, pdf_path):
                print(f"Successfully converted {input_path} to {pdf_path}")
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def process_directory(input_dir, output_dir, output_format='both'):
    """
    Process all MDX files in the input directory.
    
    Args:
        input_dir: Directory containing MDX files
        output_dir: Directory to save output files
        output_format: 'pdf', 'docx', or 'both'
    """
    try:
        # Get all MDX files in the directory
        mdx_files = [f for f in os.listdir(input_dir) if f.endswith('.mdx')]
        
        if not mdx_files:
            print(f"No MDX files found in {input_dir}")
            return
        
        print(f"Found {len(mdx_files)} MDX files in {input_dir}")
        
        # Process each file
        for file in mdx_files:
            input_path = os.path.join(input_dir, file)
            process_mdx_file(input_path, output_dir, output_format)
        
        print("All files processed successfully")
    except Exception as e:
        print(f"Error processing directory: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert MDX files to DOCX and PDF formats')
    parser.add_argument('input_path', help='Path to an MDX file or directory containing MDX files')
    parser.add_argument('output_dir', help='Directory where converted files will be saved')
    parser.add_argument('--format', choices=['pdf', 'docx', 'both'], default='both',
                      help='Output format: pdf, docx, or both (default: both)')
    args = parser.parse_args()
    
    input_path = args.input_path
    output_dir = args.output_dir
    output_format = args.format
    
    # Check if input path exists
    if not os.path.exists(input_path):
        print(f"Input path {input_path} does not exist")
        return
    
    # Check if input path is a file or directory
    if os.path.isfile(input_path) and input_path.endswith('.mdx'):
        process_mdx_file(input_path, output_dir, output_format)
    elif os.path.isdir(input_path):
        process_directory(input_path, output_dir, output_format)
    else:
        print("Input path must be an MDX file or a directory containing MDX files")

if __name__ == "__main__":
    main()