# paper-trackr
[![Status](https://img.shields.io/badge/status-active-success.svg)]() [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Tired of missing out on cool papers? `paper-trackr` keeps an eye on **PubMed**, **EuropePMC**, and **bioRxiv** for you, scanning recent papers and sending to you via email. Just set your keywords and authors, and let it do the digging!

---

## features

- Tracks new articles across [PubMed](https://pubmed.ncbi.nlm.nih.gov/), [EuropePMC](https://europepmc.org/), and [bioRxiv](https://www.biorxiv.org/)
- Custom filters for keywords and authors
- Sends daily email alerts `(optional)`
- Configurable via a simple YAML file
- Easy to automate

---

## installation and usage

```bash
git clone https://github.com/felipevzps/paper-trackr.git
cd paper-trackr

# create a conda environment with requirements
conda env create -f environment.yml

# run paper-trackr (print results to terminal, don't send email)
python paper-trackr/main.py --dry-run

# search manually with keywords or authors
python main.py --keywords "bioinformatics" "genomics"
```

---

## configuration

Use this file to define your search preferences.  
Take a look at [search_queries.yml](https://github.com/felipevzps/paper-trackr/blob/main/paper-trackr/config/search_queries.yml):

```bash
- authors: []
  keywords:
  - bioinformatics
  - genomics
  sources:
  - bioRxiv
  - PubMed
  - EuropePMC
```

## e-mail alerts (optional)

To enable email alerts, create the `accounts.yml` file with your google app password.  
Take a look at [accounts.yml](https://github.com/felipevzps/paper-trackr/blob/main/paper-trackr/config/accounts.yml):

```bash
accounts_example.yml
sender:
  email: your_email@gmail.com
  password: your_google_app_password

receiver:
  email: receiver_email@gmail.com
```

## Contact 

For questions, feel free to open an [issue](https://github.com/felipevzps/paper-trackr/issues).
