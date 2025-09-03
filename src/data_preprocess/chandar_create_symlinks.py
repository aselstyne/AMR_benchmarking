### Create symbolic links for all the fasta files stored in subfolders of ../../amr_genomic_data and place them in ./ncbi_genome ###
import os
import glob
from pathlib import Path
import argparse

PATH_ASSEMBLIES_ROOT = "../../amr_genomic_data" # Change to reflect your folder structure. This is the path_dataroot in our usual config.

def main():
	source_dir = Path(PATH_ASSEMBLIES_ROOT).resolve()
	target_dir = Path('./ncbi_genome').resolve()
	target_dir.mkdir(parents=True, exist_ok=True)

	# Find all .fna files recursively
	print("finding fasta files...")
	fna_files = list(source_dir.glob('**/*.fna'))
	print("complete")

	for fna_file in fna_files:
		# Symlink name: parent folder name (genome_id)
		genome_id = fna_file.parent.name
		link_name = target_dir / f"{genome_id}.fna"
		# Remove existing symlink/file if present
		if link_name.exists() or link_name.is_symlink():
			link_name.unlink()
		# Create symlink
		os.symlink(fna_file, link_name)
		print(f"Linked {fna_file} -> {link_name}")

if __name__ == "__main__":
	# Add argument for PATH_ASSEMBLIES_ROOT
	parser = argparse.ArgumentParser()
	parser.add_argument("--path_assemblies_root", default=PATH_ASSEMBLIES_ROOT)
	args = parser.parse_args()
	PATH_ASSEMBLIES_ROOT = args.path_assemblies_root

	main()
