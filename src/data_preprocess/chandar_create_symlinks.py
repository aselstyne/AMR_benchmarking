### Create symbolic links for all the fasta files stored in subfolders of ../../amr_genomic_data and place them in ./ncbi_genome ###
import os
import glob
from pathlib import Path
import argparse
from tqdm import tqdm

PATH_ASSEMBLIES_ROOT = "../../amr_genomic_data" # Change to reflect your folder structure. This is the path_dataroot in our usual config.

def main():
	source_dir = Path(PATH_ASSEMBLIES_ROOT).resolve()
	target_dir = Path('./ncbi_genome').resolve()
	target_dir.mkdir(parents=True, exist_ok=True)

	# Find all .fna files recursively
	print("Finding all fasta files...")
	fna_files = list(source_dir.glob('**/*.fna'))
	print(f"Found {len(fna_files)} fasta files.")

	files_created = set()

	print(f"Genome symlinks will be saved in {target_dir} with filename format: Assembly GCA_xxxxxxx -> xxxxxxx.fna")

	for fna_file in tqdm(fna_files, desc="Creating symlinks", unit="file"):
		# Symlink name: parent folder name (genome_id)
		genome_id = fna_file.parent.name
		link_name = target_dir / f"{genome_id.replace('GCA_', '')}.fna"
		# Remove existing symlink/file if present
		if link_name.exists() or link_name.is_symlink():
			link_name.unlink()
		# Create symlink
		os.symlink(fna_file, link_name)
		if link_name in files_created:
			print(f"Warning: Duplicate genome_id detected: {genome_id}. Overwriting existing symlink.")
		else:
			files_created.add(link_name)


if __name__ == "__main__":
	# Add argument for PATH_ASSEMBLIES_ROOT
	parser = argparse.ArgumentParser()
	parser.add_argument("--path_assemblies_root", default=PATH_ASSEMBLIES_ROOT)
	args = parser.parse_args()
	PATH_ASSEMBLIES_ROOT = args.path_assemblies_root

	main()
