
# MobMetrics: A Tool for Processing and Analyzing Mobility Trace Metrics

**MobMetrics** is an application designed to efficiently analyze mobility traces of different types — such as pedestrians, vehicles, bicycles, and others. The tool computes native metrics and provides a modular architecture, allowing users to add their own metrics. Everything is accessible through an intuitive interface that simplifies usage and customization of analyses.

Based on the standard adopted by the *SBRC 2025 Tool Showcase*, this project was developed to meet the four quality badges described below:

- **1. Available Artifacts (Badge D):** Ensures that code and/or data are accessible in a public repository with minimal documentation, such as the `README.md` file.
- **2. Functional Artifacts (Badge F):** Certifies that the application can be successfully executed, including clear installation instructions, dependencies, and a functional example.
- **3. Sustainable Artifacts (Badge S):** Ensures that the code is organized, modular, and understandable, with minimal documentation to facilitate third-party comprehension.
- **4. Reproducible Experiments (Badge R):** Allows the experiments described in the paper to be reproduced, with scripts and instructions that yield the same results.

More information about the badges can be found at the [link](https://doc-artefatos.github.io/sbrc2025/).

---

# README Structure

- [MobMetrics](#mobmetrics-a-tool-for-processing-and-analyzing-mobility-trace-metrics)
- [Considered Badges](#considered-badges)
  - [1. Available Artifacts (Badge D)](#1-available-artifacts-badge-d)
  - [2. Functional Artifacts (Badge F)](#2-functional-artifacts-badge-f)
  - [3. Sustainable Artifacts (Badge S)](#3-sustainable-artifacts-badge-s)
  - [4. Reproducible Experiments (Badge R)](#4-reproducible-experiments-badge-r)
- [Installation](#installation)
  - [Dependencies](#dependencies)
- [Running](#running)
  - [Execution Environment](#execution-environment)
  - [Minimum Test](#minimum-test)
- [Minimum Requirements](#minimum-requirements)
- [LICENSE](#license)

---

# Installation

1. Install [Python](https://www.python.org/downloads/).

2. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (or Anaconda).

3. Install [Git](https://git-scm.com/downloads).

4. Clone the repository:

```bash
$ git clone {repository_url_here}.git
```

5. Open the repository:

```bash
$ cd /repository_path/MOBMETRICS
```

6. Create a new environment:

```bash
$ conda env create -f environment.yml
```
```bash
$ conda activate MobMetrics
```

7. Apply migrations:
```bash
$ python MobMetrics/manage.py makemigrations
```
```bash
$ python MobMetrics/manage.py migrate
```

## Dependencies

All dependencies are listed in the [environment.yml](./environment.yml) file.

---

# Running

To run the program, first start the Django server with the following command:

```bash
python MobMetrics/manage.py runserver
```

This command starts the local development server. After execution, you can access the application in your browser at:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

> Note: This link may vary depending on your local machine or settings. The terminal will display the exact URL with the following message:
>
> ```
> Starting development server at http://<local-address>/
> ```

---

## Execution Environment

The application is organized into four main tabs: `Home`, `Upload & Process`, `Results`, and `Manage Files`.

1. **Home**  
   The homepage provides an introduction to the application and basic usage instructions.

2. **Upload & Process**  
   This tab allows the upload of mobility traces and the configuration of parameters for metric analysis.  
   Each field includes a question mark icon that, when hovered over, displays explanatory descriptions.

3. **Results**  
   After submitting files in the previous tab, the results of analyses and comparisons between traces, entities, and labels are displayed here.  
   As in the previous tab, parameters for PCA and t-SNE can be configured, with hover-based descriptions.

4. **Manage Files**  
   This tab allows you to view, download, and delete previously uploaded files.  
   Files are listed with individual buttons to:
   - Download a `.zip` file containing `.csv` metric results.
   - Remove files from system memory.

> Important: Files remain stored in memory even after restarting the application unless manually deleted.

---

## Minimum Test

To test **MobMetrics**, use the datasets available in [experiments/Anglova](./experiments/Anglova/). These datasets were collected from [Anglova](https://anglova.net/).

The original dataset is [anglova.csv](./experiments/Anglova/anglova.csv), which was partitioned into four different traces. Each represents one type of entity:

- **Tanks**
- **Staff and Mortar**
- **Mechanized Infantry**
- **Logistics**

Each trace is in a separate `.csv` file.

### Step-by-Step

#### 1. Install and Run the Application

Ensure the application is installed and running. The instructions above explain how to do this.

#### 2. Upload and Configure Files

Go to the `Upload & Process` tab and upload each `.csv` file from [experiments/Anglova](./experiments/Anglova/), **one at a time**.

For each file, fill out the following fields:

- **Trace File:** Select the corresponding file.  
  > ⚠️ The `anglova.csv` file **is not used** in this step (but can be used if necessary).
- **Name:** A descriptive name for the file (e.g., `Anglova Tanks`)
- **Label:** The entity type (e.g., `Tanks`)
- **Geographical Coordinates:** Check as **active**
- **Distance Threshold:** `60`
- **Time Threshold:** `20`
- **Radius Threshold:** `10`
- **Quadrant Divisions:** `10`

##### Estimated execution time for each file:

- **Anglova Tanks:** ~[insert time]
- **Anglova Mechanized Infantry:** ~[insert time]
- **Anglova Logistics:** ~[insert time]
- **Anglova Staff and Mortar:** ~[insert time]

#### 3. Visualize Results

After uploading and processing all four files, go to the `Results` tab. Configure the following parameters:

- **PCA N Components:** `[insert value]`
- **t-SNE N Components:** `[insert value]`
- **t-SNE Perplexity:** `[insert value]`

Then generate the plots to visualize results.

#### 4. Manage Files

In the `Manage Files` tab, you can:

- Delete previously uploaded traces
- Download processed files for individual analysis

---

# Minimum Requirements

List the minimum hardware and software requirements to run the system, such as RAM, disk space, and operating system version.

---

# LICENSE
