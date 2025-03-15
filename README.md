# mdx-to-docs

Lightweight Python script to convert directory of mdx files to pdf or docx

## Install required dependencies

```bash
pip install -r requirements.txt
```

## Usage

1. To convert a single MDX file to both formats (default):

    ```bash
    python mdx_converter.py path/to/your-file.mdx output-directory/
    ```

2. To convert a single MDX file to PDF only:

    ```bash
    python mdx_converter.py path/to/your-file.mdx output-directory/ --format pdf
    ```

3. To convert a single MDX file to DOCX only:

    ```bash
    python mdx_converter.py path/to/your-file.mdx output-directory/ --format docx
    ```

4. To convert all MDX files in a directory to a specific format:

    ```bash
    python mdx_converter.py path/to/mdx-directory/ output-directory/ --format pdf
    ```
