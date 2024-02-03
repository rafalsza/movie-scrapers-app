# Scraper Movie Rankings App

The Scraper Movie Rankings App is a Python-based web scraper application designed to retrieve and display movie rankings from popular movie websites.

## Features

- **Web Scraping:** Utilizes web scraping techniques to fetch real-time movie rankings from popular websites.
- **Ranking Display:** Displays movie rankings along with relevant details such as title, release year, and rating.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)

## Getting Started

### Prerequisites

- docker

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/rafalsza/movie-scrapers-app.git

2. Edit docker-compose.yml file IPINFO_API_KEY (register to https://ipinfo.io)

    ```bash
   IPINFO_API_KEY=your_api_key
3. Run docker container

    ```bash
   docker compose up -d

### Usage

   ```bash
   http://localhost
   http://0.0.0.0:80