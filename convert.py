import os
import shutil
import re
import zipfile

def create_cbz_from_directory(image_dir, output_path=None, delete_after=False):
    """
    Create a CBZ file from all images in a directory
    
    Args:
        image_dir: Directory containing the renamed images
        output_path: Path for the CBZ file (default: image_dir.cbz)
        delete_after: Delete the individual images after zipping (default: False)
    """
    if output_path is None:
        output_path = image_dir + '.cbz'
    
    # Get all image files, sorted naturally
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    
    images = []
    for item in os.listdir(image_dir):
        if os.path.isfile(os.path.join(image_dir, item)):
            ext = os.path.splitext(item)[1].lower()
            if ext in image_extensions:
                images.append(item)
    
    if not images:
        print("No images found to zip!")
        return None
    
    images.sort()
    
    print(f"\nCreating CBZ: {output_path}")
    print(f"Adding {len(images)} images...")
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as cbz:
        for image in images:
            image_path = os.path.join(image_dir, image)
            # Add to zip without path (just filename inside)
            cbz.write(image_path, image)
            print(f"  Added: {image}")
    
    print(f"✓ Created: {output_path}")
    print(f"  Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    
    # Optionally delete individual files
    if delete_after:
        print("\nDeleting individual image files...")
        for image in images:
            os.remove(os.path.join(image_dir, image))
        print(f"✓ Deleted {len(images)} files")
    
    return output_path

def create_zip_image_archive(image_dir, output_path=None, format='cbz'):
    """
    Create a ZIP or CBZ archive from images
    
    Args:
        image_dir: Directory containing images
        output_path: Output archive path
        format: 'zip' for regular zip, 'cbz' for comic book zip
    """
    if output_path is None:
        ext = '.cbz' if format.lower() == 'cbz' else '.zip'
        output_path = image_dir + ext
    
    return create_cbz_from_directory(image_dir, output_path)
def extract_number(text):
    """Extract the first number from text for sorting"""
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        return float(match.group(1))
    return 0

def extract_last_number(filename):
    """Extract the last number from filename for sorting"""
    name_without_ext = os.path.splitext(filename)[0]
    
    # Find all numbers in the filename
    numbers = re.findall(r'\d+', name_without_ext)
    
    if numbers:
        # Use the LAST number as the primary sort key
        return int(numbers[-1])
    return 0

def list_directories(path="."):
    """List all directories in the given path"""
    try:
        items = os.listdir(path)
        dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
        dirs.sort()
        return dirs
    except Exception as e:
        print(f"Error listing directories: {e}")
        return []

def choose_directory(prompt, path="."):
    """Interactive directory chooser"""
    while True:
        dirs = list_directories(path)
        
        if not dirs:
            print(f"\nNo directories found in: {os.path.abspath(path)}")
            custom = input("Enter a directory path manually (or '..' to go up, 'q' to quit): ").strip()
            if custom.lower() == 'q':
                return None
            elif custom == '..':
                path = os.path.dirname(os.path.abspath(path))
                continue
            elif os.path.isdir(custom):
                return os.path.abspath(custom)
            else:
                print(f"Invalid directory: {custom}")
                continue
        
        print(f"\n{prompt}")
        print(f"Current location: {os.path.abspath(path)}")
        print("-" * 50)
        
        for i, dir_name in enumerate(dirs, 1):
            print(f"{i:3}. {dir_name}")
        
        print(f"\nOptions:")
        print(f"  Enter number (1-{len(dirs)}) to select a directory")
        print(f"  Enter '..' to go to parent directory")
        print(f"  Enter 'm' to type a path manually")
        print(f"  Enter 'q' to quit")
        
        choice = input("\nYour choice: ").strip()
        
        if choice.lower() == 'q':
            return None
        elif choice.lower() == '..':
            path = os.path.dirname(os.path.abspath(path))
        elif choice.lower() == 'm':
            custom = input("Enter full directory path: ").strip()
            if os.path.isdir(custom):
                return os.path.abspath(custom)
            else:
                print(f"Directory not found: {custom}")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(dirs):
                selected_path = os.path.join(path, dirs[idx])
                print(f"\nSelected: {selected_path}")
                confirm = input("Confirm selection? (y/n): ").strip().lower()
                if confirm == 'y':
                    return os.path.abspath(selected_path)
                else:
                    print("Selection cancelled.")
            else:
                print(f"Invalid number. Please enter 1-{len(dirs)}")
        else:
            print("Invalid choice. Please try again.")

def copy_images_with_indexes(root_dir, output_dir):
    """
    Go through all subdirectories in root_dir (sorted by name),
    copy images from each directory with new names:
    <directory_index>'-'<picture_index><extension>
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all directories and sort them by name
    directories = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            directories.append((item, item_path))
    
    # Sort directories alphabetically/numerically by name
    directories.sort(key=lambda x: extract_number(x[0]))
    
    if not directories:
        print("No subdirectories found!")
        return
    
    print(f"\nFound {len(directories)} directories to process")
    
    # Image file extensions to look for
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    
    # Track total images copied
    total_images = 0
    
    # Process each directory with its index (starting from 1)
    for dir_index, (dir_name, dir_path) in enumerate(directories, start=1):
        print(f"\nDirectory {dir_index}: '{dir_name}'")
        
        # Get all image files in this directory and sort them
        images = []
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                ext = os.path.splitext(item)[1].lower()
                if ext in image_extensions:
                    images.append(item)
        
        # Sort images by name
        images.sort(key=extract_last_number)
        
        if not images:
            print(f"  No images found, skipping...")
            continue
        
        print(f"  Found {len(images)} images")
        
        # Copy each image with its index (starting from 1)
        for pic_index, image_file in enumerate(images, start=1):
            ext = os.path.splitext(image_file)[1]
            
            # Create new name: <directory_index>-<picture_index><ext>
            new_name = f"{dir_index}-{pic_index}{ext}"
            
            source_path = os.path.join(dir_path, image_file)
            dest_path = os.path.join(output_dir, new_name)
            
            # Handle duplicate names
            counter = 1
            while os.path.exists(dest_path):
                new_name = f"{dir_index}-{pic_index}_{counter}{ext}"
                dest_path = os.path.join(output_dir, new_name)
                counter += 1
            
            shutil.copy2(source_path, dest_path)
            print(f"    {image_file} -> {new_name}")
            total_images += 1
    
    print(f"\nCompleted! Copied {total_images} images to '{output_dir}'")

def copy_images_with_padded_indexes(root_dir, output_dir, padding=3):
    """
    Same as above but with zero-padded numbers (e.g., 01-001, 02-015)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all directories and sort them by name
    directories = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            directories.append((item, item_path))
    
    # Sort directories alphabetically/numerically by name
    directories.sort(key=lambda x: extract_number(x[0]))
    
    if not directories:
        print("No subdirectories found!")
        return
    
    print(f"\nFound {len(directories)} directories to process")
    print(f"Using {padding}-digit zero-padded numbering")
    
    # Image file extensions to look for
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    
    # Track total images copied
    total_images = 0
    
    # Process each directory with its index
    for dir_index, (dir_name, dir_path) in enumerate(directories, start=1):
        print(f"\nDirectory {dir_index:0{padding}d}: '{dir_name}'")
        
        # Get all image files in this directory and sort them
        images = []
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                ext = os.path.splitext(item)[1].lower()
                if ext in image_extensions:
                    images.append(item)
        
        # Sort images by name
        images.sort(key=extract_last_number)
        
        if not images:
            print(f"  No images found, skipping...")
            continue
        
        print(f"  Found {len(images)} images")
        
        # Copy each image with its index
        for pic_index, image_file in enumerate(images, start=1):
            ext = os.path.splitext(image_file)[1]
            
            # Create new name with zero-padded numbers
            new_name = f"{dir_index:0{padding}d}-{pic_index:0{padding}d}{ext}"
            
            source_path = os.path.join(dir_path, image_file)
            dest_path = os.path.join(output_dir, new_name)
            
            # Handle duplicate names
            counter = 1
            while os.path.exists(dest_path):
                new_name = f"{dir_index:0{padding}d}-{pic_index:0{padding}d}_{counter}{ext}"
                dest_path = os.path.join(output_dir, new_name)
                counter += 1
            
            shutil.copy2(source_path, dest_path)
            print(f"    {image_file} -> {new_name}")
            total_images += 1
    
    print(f"\nCompleted! Copied {total_images} images to '{output_dir}'")


# Updated main with interactive directory selection
if __name__ == "__main__":
    print("=" * 60)
    print("IMAGE COPY & RENAME SCRIPT")
    print("=" * 60)
    print("\nThis script copies images from subdirectories and renames them")
    print("with sequential indexes (DirectoryIndex-PictureIndex.extension)")
    
    # Choose source directory
    print("\n" + "=" * 60)
    print("STEP 1: SELECT SOURCE DIRECTORY")
    print("=" * 60)
    print("Navigate to the directory that CONTAINS your chapter/volume folders")
    
    # Change working directory to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory changed to script location: {script_dir}")

    source_dir = choose_directory("Select source directory (contains subdirectories with images):")
    
    if source_dir is None:
        print("\nOperation cancelled.")
        exit()
    
    print(f"\n✓ Source directory: {source_dir}")
    
    # Show contents of selected directory
    subdirs = list_directories(source_dir)
    if subdirs:
        print(f"\nSubdirectories found ({len(subdirs)}):")
        for i, d in enumerate(subdirs[:10], 1):
            print(f"  {i}. {d}")
        if len(subdirs) > 10:
            print(f"  ... and {len(subdirs) - 10} more")
    else:
        print("\n⚠ No subdirectories found in selected folder!")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Operation cancelled.")
            exit()
    
    # Choose output directory
    print("\n" + "=" * 60)
    print("STEP 2: SELECT OUTPUT DIRECTORY")
    print("=" * 60)
    print("Navigate to where you want the renamed images to be saved")
    
    output_dir = choose_directory("Select output directory (where renamed images will be saved):")
    
    if output_dir is None:
        print("\nOperation cancelled.")
        exit()
    
    print(f"\n✓ Output directory: {output_dir}")
    
    # If source and output are the same, warn user
    if source_dir == output_dir:
        print("\n⚠ WARNING: Source and output directories are the same!")
        print("This will copy files with new names into the same location.")
        proceed = input("Continue? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Operation cancelled.")
            exit()
    
    # Choose numbering format
    print("\n" + "=" * 60)
    print("STEP 3: CHOOSE NUMBERING FORMAT")
    print("=" * 60)
    print("\n1. Simple (e.g., 1-1.jpg, 1-2.jpg, 2-1.jpg)")
    print("2. Zero-padded (e.g., 001-001.jpg, 001-002.jpg)")
    
    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    # Confirm operation
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Source:      {source_dir}")
    print(f"Destination: {output_dir}")
    print(f"Format:      {'Zero-padded' if choice == '2' else 'Simple'}")
    if choice == '2':
        pad = input("Enter number of padding digits (default 3): ").strip()
        padding = int(pad) if pad.isdigit() and int(pad) > 0 else 3
        print(f"Padding:     {padding} digits")
    else:
        padding = 0
    
    confirm = input("\nProceed with operation? (y/n): ").strip().lower()
    
    if confirm == 'y':
        print("\n" + "=" * 60)
        print("PROCESSING...")
        print("=" * 60)
        
        if choice == '2':
            copy_images_with_padded_indexes(source_dir, output_dir, padding)
        else:
            copy_images_with_indexes(source_dir, output_dir)
        
        print("\n" + "=" * 60)
        print("OPERATION COMPLETE!")
        print("=" * 60)
    else:
        print("\nOperation cancelled.")

    print("\n" + "=" * 60)
    zip_choice = input("Do you want to create a CBZ archive? (y/n): ").strip().lower()
    
    if zip_choice == 'y':
        default_name = os.path.basename(source_dir) + '.cbz'
        custom_name = input(f"Enter archive name (or press Enter for '{default_name}'): ").strip()
        
        if not custom_name:
            custom_name = default_name
        if not custom_name.endswith('.cbz'):
            custom_name += '.cbz'
        
        zip_path = os.path.join(os.path.dirname(output_dir), custom_name)
        create_cbz_from_directory(output_dir, zip_path)