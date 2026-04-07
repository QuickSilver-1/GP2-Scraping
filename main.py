from multiprocessing import Process
import multiprocessing
from src import config, logger, web_scrapper
import time

def main() -> None:
    cfg = config.Config()
    queries = [
        ("Россия, Москва, Западный административный округ", 9222),
        ("Северный административный округ, Москва", 9223),
        ("Южный административный округ, Москва", 9224),
        ("Россия, Москва, Северо-Восточный административный округ", 9225),
        ("Юго-Западный административный округ, Москва", 9226),
        # ("Россия, Москва, Северо-Западный административный округ", 9227),
        # ("Юго-Восточный административный округ, Москва", 9228),
        # ("Центральный административный округ, Москва", 9229),
        # ("Восточный административный округ, Москва", 9230)
    ]
    
    for i, query in enumerate(queries):
        query_text = query[0]
        port = query[1]
        excel_path = f"data/raw/data{i+2}.xlsx"
        
        # Создаем процесс, передавая ТОЛЬКО сериализуемые данные
        p = Process(
            target=mutiprocessing_scrape,
            args=(
                query_text,
                port,
                excel_path,
                cfg.scrapper,
                cfg.logger.level,
                cfg.logger.output_file,
                cfg.excel
            )
        )
        p.start()
        time.sleep(15)
        
    time.sleep(60*60*24)
    
def mutiprocessing_scrape(query_text, area_id, excel_path, scrapper_config, log_level, log_output, excel_config):    
    log = logger.get_logger(log_level, log_output)
    log.bind(app="GP2")
    log.info(f"Starting scrape for: {query_text}")
    
    excel_handler = web_scrapper.ExcelHandler(excel_config)
    excel_handler.set_raw_path(excel_path)
    
    scraper = web_scrapper.SeleniumScraper(scrapper_config, log, excel_handler, area_id)
    scraper.scrape(query_text)

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Критически важно для Windows
    main()