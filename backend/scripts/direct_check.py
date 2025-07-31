"""
Simple script to test basic Python functionality and file operations
This version removes Unicode characters that cause issues in Windows console.
"""

def safe_write(f, message):
    """Helper function to write text safely to the file"""
    try:
        # Replace any problematic Unicode characters
        safe_message = (
            message
            .replace('✅', '[OK]')
            .replace('❌', '[ERROR]')
        )
        f.write(safe_message + '\n')
        f.flush()
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    output_file = 'test_output.txt'
    try:
        # Test 1: Basic Python functionality
        with open(output_file, 'w', encoding='utf-8') as f:
            safe_write(f, "=== Direct Check Script ===")
            safe_write(f, "1. Basic Python test successful")
            
            # Test 2: Environment variables
            import os
            safe_write(f, "\n2. Environment Variables:")
            safe_write(f, f"   Current Directory: {os.getcwd()}")
            safe_write(f, f"   Python Executable: {sys.executable}")
            
            # Test 3: Check .env file
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
            safe_write(f, f"\n3. Looking for .env at: {env_path}")
            
            if os.path.exists(env_path):
                safe_write(f, "   [OK] .env file found")
                
                # Read .env file with explicit error handling
                try:
                    with open(env_path, 'r', encoding='utf-8') as env_file:
                        lines = []
                        line_count = 0
                        for i, line in enumerate(env_file):
                            try:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    lines.append(line)
                                    line_count += 1
                                if i < 5:  # Only log the first few lines
                                    safe_write(f, f"   Line {i+1}: {line[:100]}")
                            except Exception as line_error:
                                safe_write(f, f"   [ERROR] Reading line {i+1}: {str(line_error)}")
                                continue
                        
                        safe_write(f, f"\n   Successfully read {line_count} non-comment lines from .env")
                        
                        # Write first few non-comment lines (masking sensitive data)
                        if lines:
                            safe_write(f, "\n   First few non-comment lines (sensitive data masked):")
                            for line in lines[:3]:
                                # Mask potential passwords/tokens
                                masked_line = line
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    if any(s in key.lower() for s in ['pass', 'secret', 'key', 'token']):
                                        value = '***MASKED***'
                                    masked_line = f"{key}={value}"
                                safe_write(f, f"   - {masked_line}")
                        
                except Exception as e:
                    safe_write(f, f"   [ERROR] Reading .env file: {str(e)}")
            else:
                safe_write(f, f"   [ERROR] .env file not found at {env_path}")
                
                # List directory contents for debugging
                dir_path = os.path.dirname(env_path)
                if os.path.exists(dir_path):
                    safe_write(f, f"\n   Directory contents of {os.path.dirname(env_path)}:")
                    try:
                        for item in os.listdir(dir_path):
                            item_path = os.path.join(dir_path, item)
                            item_type = "(file)" if os.path.isfile(item_path) else "(dir)"
                            safe_write(f, f"   - {item} {item_type}")
                    except Exception as e:
                        safe_write(f, f"   [ERROR] Listing directory: {str(e)}")
            
            safe_write(f, "\n4. Script completed successfully")
            
    except Exception as e:
        # Create a new file if we can't write to the existing one
        try:
            with open('test_error.txt', 'w', encoding='utf-8') as err_file:
                import traceback
                err_file.write("=== Script Error ===\n")
                err_file.write(f"Error: {str(e)}\n\n")
                err_file.write("Traceback:\n")
                traceback.print_exc(file=err_file)
                err_file.flush()
        except Exception as err:
            print(f"[FATAL] Could not write error to file: {err}")
            print(f"Original error: {e}")

if __name__ == "__main__":
    import sys
    
    # Set console output encoding to UTF-8 if possible
    if sys.stdout.encoding != 'utf-8':
        try:
            import io
            import sys
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except Exception as e:
            print(f"Could not set UTF-8 encoding: {e}")
    
    # Run main function
    main()
    
    # Force flush all buffers
    sys.stdout.flush()
    sys.stderr.flush()
