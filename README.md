# paper-trackr
[![Demo](https://img.shields.io/badge/demo-click%20here-orange.svg)](https://felipevzps.github.io/newsletter/paper-trackr_newsletter.html)
[![PyPI version](https://img.shields.io/pypi/v/paper-trackr)](https://pypi.org/project/paper-trackr/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Tired of missing out on cool papers? `paper-trackr` keeps an eye on **PubMed**, **EuropePMC**, and **bioRxiv** for you, scanning recent papers and sending to you via email. Just set your keywords and authors, and let it do the digging!

---

# features

- Tracks new papers across [PubMed](https://pubmed.ncbi.nlm.nih.gov/), [EuropePMC](https://europepmc.org/), and [bioRxiv](https://www.biorxiv.org/)
- Custom filters for keywords and authors
- Send email alerts `(optional)`
- Easy to use and automate

---

# quick usage

```bash
# install the package via pip
$ pip install paper-trackr

# create your first query (e.g., bioinformatics papers in bioRxiv)
$ paper-trackr manage --add

# search for papers published in the last 3 days (dry-run = don't send email)
$ paper-trackr --dry-run --days 3

# (optional) configure sender/receiver emails for alerts
$ paper-trackr configure

# send papers published in the last 3 days by email
$ paper-trackr --days 3
```

---

# managing queries

You can create multiple queries using `manage --add`:
```bash
# interactively add a new search query
$ paper-trackr manage --add

# example: creating a query to search for bioinformatics + genomics related papers in bioRxiv
Would you like to create a new search query? (y/N): y
Enter keywords (comma-separated, or leave empty): bioinformatics, genomics
Enter authors (comma-separated, or leave empty):
Enter sources (bioRxiv, PubMed, EuropePMC — comma-separated, or leave empty for all): bioRxiv
Search query saved.
```
>[!NOTE]
>You can also create queries for your favorite researcher / groups!  
>Just include their names in the author sessions.

You can check your queries using `manage --list`
```bash
# list all saved queries
$ paper-trackr manage --list

Saved queries:
  [1] keywords: bioinformatics, genomics | authors: none | sources: bioRxiv
```

You can also delete queries using `manage --delete N`:
```bash
# delete the 1st query
$ paper-trackr manage --delete 1
Query #1 removed.
```

Or delete all queries using `manage --clear`
```bash
# clear all saved queries (asks for confirmation)
$ paper-trackr manage --clear

Are you sure you want to delete all saved queries? (y/N): y
All queries deleted.
```

---

# email alerts (optional)

To receive email alerts, configure sender and receiver emails:

```bash
# configure
$ paper-trackr configure
```

You’ll be prompted to provide:  
  * Sender email 
  * **Google App Password**
  * Receiver emails (you can enter multiple, separated by spaces)

```bash
# configure
$ paper-trackr configure

# example
? Enter sender email: your_email@gmail.com
? Enter sender password (Google App Password): *******************
? Enter receiver emails (comma-separated): recipient1@gmail.com, recipient2@university.edu
```
>[!IMPORTANT]
>Google App Password is not your Gmail password.  
>You must generate an App Password via your Google Account → [Create App Password](https://support.google.com/accounts/answer/185833?hl=en)  

Once configured, all future `paper-trackr` runs will deliver results directly to your email inbox.  
See an example below, or [click here to read the latest papers published in bioinformatics.](https://felipevzps.github.io/newsletter/paper-trackr_newsletter.html).

![](https://github.com/felipevzps/paper-trackr/blob/main/images/email_example.png)

>[!NOTE]
>`paper-trackr` does not have a published paper.    
>This image is just an **illustrative example** of the type of email you’ll receive using `paper-trackr`!

---

# automating daily paper tracking (optional)

To get the most out of `paper-trackr`, you can automate its execution on a daily basis.  
By creating a simple bash script and scheduling it with [cron](https://en.wikipedia.org/wiki/Cron), you’ll receive fresh paper updates every day!  

Example script: `run-paper-trackr.sh`

```bash
# create a script to run paper-trackr
$ mkdir paper-trackr-logs && cd paper-trackr-logs 
$ vi run-paper-trackr.sh

# content of the script:
#!/bin/bash

# run paper-trackr (default days is 3)
paper-trackr --days 1

# make sure your script is executable:
$ chmod +x run-paper-trackr.sh
```

Now, you just have to schedule it with a `cron table file`:
```bash
# open your cron table file
$ crontab -e

# add a line like this to run the script every day at 5 AM:
0 5 * * * /path/to/paper-trackr-logs/run-paper-trackr.sh >> /path/to/paper-trackr-logs/logs/cron.log 2>&1
```

This ensures that `paper-trackr` will check for new papers every morning and email you if configured!

---

# contact 

For questions, feel free to open an [issue](https://github.com/felipevzps/paper-trackr/issues).

---

# license

```
MIT License

Copyright (c) 2025 Felipe Vaz Peres

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
