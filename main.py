from src import config, logger, web_scrapper

def main() -> None:
    cfg = config.Config()
    
    log = logger.get_logger(cfg.logger.level, cfg.logger.output_file)
    log.bind(app="GP2")
    log.info("Starting the service...")

    scraper = web_scrapper.SeleniumScraper(cfg, log)
    scraper.scrape()

if __name__ == "__main__":
    main()