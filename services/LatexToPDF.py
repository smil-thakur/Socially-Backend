import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import  Union, List
from starlette.datastructures import UploadFile


# THIS IS THE CORRECTED CLASS:
class TexToPdfConverter:
    """
    A class to convert TeX files to PDF format.
    
    This class provides methods to compile TeX files using various LaTeX engines
    and return the resulting PDF as bytes or save it to a file.
    """
    
    def __init__(self, latex_engine: str = "pdflatex"):
        """
        Initialize the TeX to PDF converter.
        
        Args:
            latex_engine (str): LaTeX engine to use ('pdflatex', 'xelatex', 'lualatex')
        """
        self.latex_engine = latex_engine
        self._validate_latex_engine()
    
    def _validate_latex_engine(self) -> None:
        """Validate that the specified LaTeX engine is available."""
        try:
            result = subprocess.run(
                [self.latex_engine, "--version"],
                capture_output=True,
                check=True, # Use check=True for cleaner error handling
                text=True,
                timeout=10
            )
        except FileNotFoundError:
            raise RuntimeError(f"LaTeX engine '{self.latex_engine}' not found. Please install a TeX distribution (like MiKTeX, TeX Live, or MacTeX).")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"LaTeX engine '{self.latex_engine}' is not working properly: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"LaTeX engine '{self.latex_engine}' timed out during validation.")
    
    async def tex_to_pdf_bytes(self, tex_input: Union[str, Path, UploadFile]) -> bytes:
        """
        Convert a TeX input to PDF and return as bytes. This is the main router method.
        
        Args:
            tex_input: Path to TeX file, or FastAPI UploadFile object.
            
        Returns:
            bytes: The compiled PDF as bytes.
        """
        # This logic correctly routes the input to the appropriate handler
        print("is file",isinstance(tex_input, UploadFile))
        
        if isinstance(tex_input, UploadFile):
            return await self._compile_from_upload_file(tex_input)
        else:
            return await self._compile_from_file_path(tex_input)
    
    async def _compile_from_file_path(self, tex_file_path: Union[str, Path]) -> bytes:
        """
        Compile TeX file from a file system path. (This method is now corrected)
        """
        tex_path = Path(tex_file_path)

        if not tex_path.exists():
            raise FileNotFoundError(f"TeX file not found: {tex_path}")

        if tex_path.suffix.lower() not in ['.tex', '.latex']:
            raise ValueError(f"Input file must be a .tex or .latex file, got: {tex_path.suffix}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_tex_file = temp_path / tex_path.name
            shutil.copy2(tex_path, temp_tex_file)
            
            # Copy auxiliary files (images, styles, etc.) from the source directory
            self._copy_auxiliary_files(tex_path.parent, temp_path)
            
            pdf_path = self._compile_tex(temp_tex_file, temp_path)
            
            with open(pdf_path, 'rb') as pdf_file:
                return pdf_file.read()
    
    async def _compile_from_upload_file(self, upload_file: UploadFile) -> bytes:
        """
        Compile TeX file from a FastAPI UploadFile object. (This method was already correct)
        """
        if not upload_file.filename:
            raise ValueError("UploadFile must have a filename.")
        
        filename = upload_file.filename.lower()
        if not (filename.endswith('.tex') or filename.endswith('.latex')):
            raise ValueError(f"Upload file must be a .tex or .latex file, but got: {upload_file.filename}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_tex_file = temp_path / upload_file.filename
            
            # Read the content from the UploadFile and write it to the temporary file
            content = await upload_file.read()
            with open(temp_tex_file, 'wb') as f:
                f.write(content)
            
            # Note: For multipart uploads including auxiliary files (e.g., images),
            # you would need to handle multiple files from the request here.
            # This implementation assumes a self-contained .tex file.
            
            pdf_path = self._compile_tex(temp_tex_file, temp_path)
            
            with open(pdf_path, 'rb') as pdf_file:
                return pdf_file.read()

    def _copy_auxiliary_files(self, source_dir: Path, dest_dir: Path) -> None:
        """Copy common auxiliary files to the temporary compilation directory."""
        common_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.eps', 
                           '.bib', '.cls', '.sty', '.bst'}
        
        for file_path in source_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in common_extensions:
                shutil.copy2(file_path, dest_dir / file_path.name)
    
    def _compile_tex(self, tex_file: Path, work_dir: Path) -> Path:
        """
        The core compilation logic. Runs the LaTeX engine in a temporary directory.
        """
        pdf_file = tex_file.with_suffix('.pdf')
        cmd = [self.latex_engine, "-interaction=nonstopmode", "-file-line-error", str(tex_file.name)]
        
        try:
            # First compilation pass
            result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, timeout=60)

            # If compilation fails and no PDF is produced, raise an error
            if result.returncode != 0 and not (work_dir / pdf_file.name).exists():
                missing_packages = self._extract_missing_packages(result.stdout)
                if missing_packages:
                    packages_str = ", ".join(missing_packages)
                    raise RuntimeError(
                        f"LaTeX compilation failed due to missing packages: {packages_str}. "
                        f"Try installing them (e.g., with 'tlmgr install {' '.join(missing_packages)}').\n"
                        f"Full log:\n{result.stdout}"
                    )
                raise RuntimeError(f"LaTeX compilation failed. Log:\n{result.stdout}\n{result.stderr}")
            
            # Run a second time to resolve references (if bibtex/biber is needed, more steps are required)
            if (work_dir / pdf_file.name).exists():
                subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, timeout=60)
            
            final_pdf_path = work_dir / pdf_file.name
            if not final_pdf_path.exists():
                raise RuntimeError("PDF file was not generated after compilation.")
            
            return final_pdf_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("LaTeX compilation timed out after 60 seconds.")

    def _extract_missing_packages(self, latex_output: str) -> List[str]:
        """Extract missing .sty package names from the LaTeX log."""
        missing_packages = []
        pattern = r"File `([^']+\.sty)' not found"
        matches = re.findall(pattern, latex_output)
        
        for match in matches:
            package_name = match.replace('.sty', '')
            if package_name not in missing_packages:
                missing_packages.append(package_name)
        
        return missing_packages