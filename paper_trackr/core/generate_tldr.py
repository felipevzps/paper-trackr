import subprocess
from pathlib import Path
from paper_trackr.config.global_settings import SCITLDR_DIR, SCITLDR_DATA_DIR, SCITLDR_MODEL_DIR, SCITLDR_OUT_DIR, SCITLDR_DATA_SUBDIR, SCITLDR_SOURCE_FILE, SCITLDR_TEST_FILE, SCITLDR_BART_XSUM, BEAM_SIZE, LENGTH_PENALTY, MAX_LENGTH, MIN_LENGTH

def prepare_abstract_source_file(articles):
    source_path = SCITLDR_DATA_SUBDIR / SCITLDR_SOURCE_FILE
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with open(source_path, "w", encoding="utf-8") as f:
        for article in articles:
            abstract = article.get("abstract", "").replace("\n", " ").strip()
            f.write(abstract + "\n")
    return source_path

def prepare_fairseq_inference_files():
    task_dir = SCITLDR_DATA_SUBDIR
    file_to_encode = SCITLDR_SOURCE_FILE
    encoded_output = file_to_encode.replace(".source", ".bpe.source")
    test_prefixes = encoded_output.replace(".source", "")
    bin_dir = task_dir.parent / f"{task_dir.name}-bin"

    task_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"\nStep 2.1: BPE encoding of {file_to_encode}...")

        subprocess.run([
            "python3.8", "-m", "multiprocessing_bpe_encoder",
            "--encoder-json", "encoder.json",
            "--vocab-bpe", "vocab.bpe",
            "--inputs", str(task_dir / file_to_encode),
            "--outputs", str(task_dir / encoded_output),
            "--workers", "8",
            "--keep-empty"
        ], cwd=SCITLDR_DATA_DIR, check=True)

        print(f"\nStep 2.2: Running fairseq-preprocess...")

        subprocess.run([
            "fairseq-preprocess",
            "--only-source",
            "--testpref", str(task_dir / test_prefixes),
            "--source-lang", "source",
            "--destdir", str(bin_dir),
            "--srcdict", "dict.txt",
            "--workers", "8"
        ], cwd=SCITLDR_DATA_DIR, check=True)

        print(f"\nStep 2.3: Copying source dict to target dict...")
        source_dict = bin_dir / "dict.source.txt"
        target_dict = bin_dir / "dict.target.txt"
        target_dict.write_text(source_dict.read_text(), encoding="utf-8")

        print("Fairseq inference data preparation completed!")

    except subprocess.CalledProcessError as e:
        print(f"Error during fairseq preprocessing: {e}")

def run_scitldr_inference(articles):
    try:
        print("\nStep 1: Creating source file with paper-trackr abstracts...")
        prepare_abstract_source_file(articles)

        print("\nStep 2: Preparing SciTLDR inference files...")
        prepare_fairseq_inference_files()

        print("\nStep 3: Running SciTLDR inference...")
        subprocess.run([
            "python3.8", "scripts/generate.py",
            "--checkpoint_dir", str(SCITLDR_MODEL_DIR),
            "--checkpoint_file", SCITLDR_BART_XSUM,
            "--source_fname", SCITLDR_SOURCE_FILE,
            "--datadir", str(SCITLDR_DATA_DIR / SCITLDR_DATA_SUBDIR),
            "--outdir", str(SCITLDR_OUT_DIR),
            "--beam", BEAM_SIZE,
            "--lenpen", LENGTH_PENALTY,
            "--max_len_b", MAX_LENGTH,
            "--min_len", MIN_LENGTH,
            "--test_fname", SCITLDR_TEST_FILE
        ], cwd=SCITLDR_DIR, check=True)
    
        # read output tldrs and associate them with abstracts
        tldr_path = SCITLDR_OUT_DIR / SCITLDR_TEST_FILE
        with open(tldr_path, "r", encoding="utf-8") as f:
            tldrs = [line.strip() for line in f.readlines()]

        if len(tldrs) != len(articles):
            raise ValueError("Mismatch between number of TLDRs and abstracts.")

        for article, tldr in zip(articles, tldrs):
            article["tldr"] = tldr

        print("paper-trackr TLDRs generated successfully!") 
        return articles

    except subprocess.CalledProcessError as e:
        print(f"Error during execution: {e}")
